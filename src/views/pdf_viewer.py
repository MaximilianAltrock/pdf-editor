from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, 
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QWheelEvent
from PySide6.QtCore import Qt, Signal, QSize, QPoint

class PDFPageLabel(QLabel):
    """Label for displaying a single PDF page."""
    
    def __init__(self, page_number: int, parent=None):
        super().__init__(parent)
        self.page_number = page_number
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

class PDFViewerWidget(QWidget):
    """Widget for displaying PDF pages with continuous scrolling."""
    
    # Signals
    zoomChanged = Signal(float)  # Emitted when zoom level changes
    pageChanged = Signal(int)    # Emitted when visible page changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.page_labels = []  # List of PDFPageLabel widgets
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)  # Space between pages
        
        # Container widget for pages
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(20)
        
        # Scroll area for the pages
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.layout.addWidget(self.scroll_area)
        
        # Set dark theme
        self.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QWidget#container {
                background-color: #1e1e1e;
            }
            QLabel {
                background-color: #252526;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 10px;
            }
        """)
        self.container.setObjectName("container")
        
        # Enable mouse tracking for wheel events
        self.setMouseTracking(True)
        
        # Connect scroll signals
        self.scroll_area.verticalScrollBar().valueChanged.connect(
            self._on_scroll_changed
        )
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming and scrolling.
        
        Args:
            event: The wheel event
        """
        if event.modifiers() & Qt.ControlModifier:
            # Get the position before zoom for maintaining focus
            pos = self.scroll_area.widget().mapFrom(self, event.position().toPoint())
            
            # Calculate zoom delta (smoother on trackpad)
            delta = event.angleDelta().y() / 120.0  # Number of 15-degree steps
            factor = 1.0 + (delta * 0.1)  # 10% change per step
            
            # Apply zoom centered on mouse position
            self.set_zoom(self.zoom_level * factor, pos)
            event.accept()
        else:
            # Pass the event to the scroll area for normal scrolling
            event.ignore()
    
    def set_zoom(self, zoom_level: float, center: QPoint = None):
        """Set the zoom level, optionally maintaining focus on a point.
        
        Args:
            zoom_level: New zoom level (1.0 = 100%)
            center: Optional point to maintain focus on while zooming
        """
        # Store scroll position ratios before zoom
        if center:
            rel_x = center.x() / self.container.width()
            rel_y = center.y() / self.container.height()
        
        # Apply zoom limits
        old_zoom = self.zoom_level
        self.zoom_level = max(0.1, min(5.0, zoom_level))
        
        # Only update if zoom actually changed
        if self.zoom_level != old_zoom:
            self._update_all_pages()
            self.zoomChanged.emit(self.zoom_level)
            
            # Restore focus point after zoom
            if center:
                self.scroll_area.horizontalScrollBar().setValue(
                    int(rel_x * self.container.width() - center.x())
                )
                self.scroll_area.verticalScrollBar().setValue(
                    int(rel_y * self.container.height() - center.y())
                )
    
    def zoom_in(self):
        """Increase zoom level by 10%."""
        center = QPoint(
            self.scroll_area.viewport().width() // 2,
            self.scroll_area.viewport().height() // 2
        )
        self.set_zoom(self.zoom_level * 1.1, center)
    
    def zoom_out(self):
        """Decrease zoom level by 10%."""
        center = QPoint(
            self.scroll_area.viewport().width() // 2,
            self.scroll_area.viewport().height() // 2
        )
        self.set_zoom(self.zoom_level / 1.1, center)
        
    def reset_zoom(self):
        """Reset zoom level to 100%."""
        center = QPoint(
            self.scroll_area.viewport().width() // 2,
            self.scroll_area.viewport().height() // 2
        )
        self.set_zoom(1.0, center)
    
    def _on_scroll_changed(self):
        """Handle scroll position changes."""
        # Find the most visible page
        viewport = self.scroll_area.viewport()
        viewport_rect = viewport.rect()
        viewport_rect.translate(0, self.scroll_area.verticalScrollBar().value())
        
        max_visible_area = 0
        most_visible_page = 0
        
        for label in self.page_labels:
            page_rect = label.geometry()
            visible_rect = viewport_rect.intersected(page_rect)
            visible_area = visible_rect.width() * visible_rect.height()
            
            if visible_area > max_visible_area:
                max_visible_area = visible_area
                most_visible_page = label.page_number
        
        if most_visible_page != self.current_page:
            self.current_page = most_visible_page
            self.pageChanged.emit(most_visible_page)
    
    def go_to_page(self, page_number: int) -> bool:
        """Scroll to a specific page.
        
        Args:
            page_number: Zero-based page number to display
            
        Returns:
            bool: True if page exists and was scrolled to
        """
        if 0 <= page_number < len(self.page_labels):
            label = self.page_labels[page_number]
            self.scroll_area.ensureWidgetVisible(label, 50, 50)
            self.current_page = page_number
            self.pageChanged.emit(page_number)
            return True
        return False
    
    def set_document(self, total_pages: int):
        """Set up the viewer for a new document.
        
        Args:
            total_pages: Total number of pages in the document
        """
        self.clear()
        self.total_pages = total_pages
        self.current_page = 0
        self.pageChanged.emit(0)  # Emit signal for initial page
        
        # Create labels for all pages
        for i in range(total_pages):
            label = PDFPageLabel(i)
            self.page_labels.append(label)
            self.container_layout.addWidget(label)
    
    def display_page(self, page_number: int, image_or_pixmap):
        """Display a page.
        
        Args:
            page_number: Zero-based page number
            image_or_pixmap: QImage or QPixmap to display
        """
        if not (0 <= page_number < len(self.page_labels)):
            return
            
        if isinstance(image_or_pixmap, QImage):
            pixmap = QPixmap.fromImage(image_or_pixmap)
        else:
            pixmap = image_or_pixmap
        
        if pixmap:
            # Scale pixmap
            scaled_pixmap = pixmap.scaled(
                int(pixmap.width() * self.zoom_level),
                int(pixmap.height() * self.zoom_level),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Set the page label's pixmap
            self.page_labels[page_number].setPixmap(scaled_pixmap)
    
    def _update_all_pages(self):
        """Update all page displays with current zoom level."""
        for label in self.page_labels:
            if pixmap := label.pixmap():
                # Get original size pixmap
                orig_size = pixmap.size() / (self.zoom_level / 1.1)  # Approximate
                
                # Scale to new zoom level
                scaled_pixmap = pixmap.scaled(
                    int(orig_size.width() * self.zoom_level),
                    int(orig_size.height() * self.zoom_level),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                label.setPixmap(scaled_pixmap)
    
    def clear(self):
        """Clear all pages."""
        for label in self.page_labels:
            label.setParent(None)
            label.deleteLater()
        self.page_labels.clear()
        self.total_pages = 0
        self.current_page = 0
    
    def sizeHint(self) -> QSize:
        """Suggest a size for the widget."""
        return QSize(800, 1000)  # Default size suitable for most PDF pages
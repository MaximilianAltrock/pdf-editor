from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, 
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QWheelEvent
from PySide6.QtCore import Qt, Signal, QSize, QPoint, QEvent

class PDFPageLabel(QLabel):
    """Label for displaying a single PDF page."""
    
    def __init__(self, page_number: int, parent=None):
        super().__init__(parent)
        self.page_number = page_number
        self.original_pixmap = None  # Store original unscaled pixmap
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
        
        # Enable touch gestures
        self.grabGesture(Qt.PinchGesture)
        
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
        
        # Install event filter on scroll area and viewport
        self.scroll_area.viewport().installEventFilter(self)
        self.scroll_area.installEventFilter(self)
    
    def event(self, event):
        """Handle various events including gestures.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if event was handled
        """
        if event.type() == QEvent.Type.Gesture:
            return self.handle_gesture_event(event)
        return super().event(event)
    
    def handle_gesture_event(self, event):
        """Handle gesture events like pinch zoom.
        
        Args:
            event: The gesture event
            
        Returns:
            bool: True if event was handled
        """
        if gesture := event.gesture(Qt.PinchGesture):
            # Calculate center point for zooming
            center = self.scroll_area.viewport().mapFromGlobal(
                gesture.centerPoint().toPoint()
            )
            
            # Get scale change since last update
            scale_factor = gesture.scaleFactor()
            
            # Calculate new zoom level
            new_zoom = self.zoom_level * scale_factor
            
            # Apply zoom with the center point
            self.set_zoom(new_zoom, center)
            
            # Emit zoom changed signal for controller to handle
            self.zoomChanged.emit(self.zoom_level)
            
            return True
        return False
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for scrolling.
        
        Args:
            event: The wheel event
        """
        # Handle zoom with Ctrl+scroll on mouse (not trackpad)
        if event.modifiers() & Qt.ControlModifier:
            # Get the position before zoom for maintaining focus
            pos = self.scroll_area.widget().mapFrom(self, event.position().toPoint())
            
            # Calculate zoom delta (smoother on trackpad)
            delta = event.angleDelta().y() / 120.0  # Number of 15-degree steps
            factor = 1.0 + (delta * 0.1)  # 10% change per step
            
            # Calculate and set new zoom level
            new_zoom = self.zoom_level * factor
            self.set_zoom(new_zoom, pos)
            
            # Emit zoom changed signal for controller to handle
            self.zoomChanged.emit(self.zoom_level)
            
            # Prevent scrolling while zooming
            event.accept()
            return
            
        # For non-zoom scrolling, forward to the scroll area
        self.scroll_area.wheelEvent(event)
    
    def set_zoom(self, zoom_level: float, center=None):
        """Set zoom level and update page display.
        Args:
            zoom_level: New zoom level to set (will be clamped between 0.1 and 5.0)"""
        zoom_level = max(0.1, min(5.0, zoom_level))  # Enforce zoom limits
        if zoom_level != self.zoom_level:
            self.zoom_level = zoom_level
            self._update_all_pages()
    
    def zoom_in(self):
        """Increase zoom level by 10%."""
        center = QPoint(
            self.scroll_area.viewport().width() // 2,
            self.scroll_area.viewport().height() // 2
        )
        self.set_zoom(min(5.0, self.zoom_level * 1.1), center)
    
    def zoom_out(self):
        """Decrease zoom level by 10%."""
        center = QPoint(
            self.scroll_area.viewport().width() // 2,
            self.scroll_area.viewport().height() // 2
        )
        self.set_zoom(max(0.1, self.zoom_level / 1.1), center)
        
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
        most_visible_page = self.current_page
        
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
            
            # Calculate the target scroll position to center the page
            viewport_height = self.scroll_area.viewport().height()
            page_height = label.height()
            y_offset = label.pos().y()
            
            # Center the page vertically
            target_y = y_offset - (viewport_height - page_height) // 2
            
            # Ensure we don't scroll beyond bounds
            target_y = max(0, min(target_y, self.container.height() - viewport_height))
            
            # Scroll to the calculated position
            self.scroll_area.verticalScrollBar().setValue(target_y)
            
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
        
        # Create labels for all pages
        for i in range(total_pages):
            label = PDFPageLabel(i)
            self.page_labels.append(label)
            self.container_layout.addWidget(label)
        
        # Emit signal for initial page and update UI
        self.pageChanged.emit(0)  # This will trigger page loading in MainWindow
    
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
            # Store original pixmap
            self.page_labels[page_number].original_pixmap = pixmap
            
            # Scale pixmap using current zoom
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
            if original := label.original_pixmap:
                # Scale from original pixmap to maintain quality
                new_width = int(original.width() * self.zoom_level)
                new_height = int(original.height() * self.zoom_level)
                
                # Only rescale if dimensions actually changed
                current = label.pixmap()
                if not current or current.width() != new_width or current.height() != new_height:
                    scaled_pixmap = original.scaled(
                        new_width,
                        new_height,
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
    
    def eventFilter(self, obj, event):
        """Filter events to intercept wheel events before they reach the scroll area.
        
        Args:
            obj: The object the event was sent to
            event: The event
            
        Returns:
            bool: True if the event should be filtered out
        """
        if (isinstance(event, QWheelEvent) and 
            event.modifiers() & Qt.ControlModifier):
            # Emit zoom changed signal for controller to handle
            delta = event.angleDelta().y() / 120.0
            factor = 1.0 + (delta * 0.1)
            
            # Calculate and set new zoom level
            new_zoom = self.zoom_level * factor
            self.set_zoom(new_zoom)
            self.zoomChanged.emit(self.zoom_level)
            return True  # Prevent event from being processed further
        return super().eventFilter(obj, event)
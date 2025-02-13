from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QSize

class PDFThumbnailPanel(QWidget):
    """Side panel showing page thumbnails."""
    
    # Signals
    pageSelected = Signal(int)  # Emitted when a thumbnail is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.setup_ui()
        self.setVisible(True)  # Ensure visible by default
    
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title label
        title = QLabel("Pages")
        title.setStyleSheet("""
            QLabel {
                background-color: #252526;
                color: #d4d4d4;
                padding: 5px;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        layout.addWidget(title)
        
        # Thumbnail list
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setIconSize(QSize(120, 160))
        self.list_widget.setSpacing(10)
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_widget.itemClicked.connect(self._on_thumbnail_clicked)
        
        # Style the list widget
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: none;
            }
            QListWidget::item {
                background-color: #252526;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QListWidget::item:selected {
                background-color: #37373d;
                border: 1px solid #007acc;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        
        layout.addWidget(self.list_widget)
    
    def _on_thumbnail_clicked(self, item: QListWidgetItem):
        """Handle thumbnail selection.
        
        Args:
            item: The selected list widget item
        """
        if item is not None:
            page_number = self.list_widget.row(item)
            self.current_page = page_number
            self.pageSelected.emit(page_number)
    
    def add_thumbnail(self, pixmap: QPixmap, page_number: int):
        """Add a page thumbnail.
        
        Args:
            pixmap: The page image
            page_number: The page number (0-based)
        """
        # Check if page already exists
        if page_number < self.list_widget.count():
            return  # Skip if thumbnail for this page already exists
            
        # Create thumbnail
        scaled = pixmap.scaled(
            120, 160,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Create list item
        item = QListWidgetItem()
        item.setIcon(QIcon(scaled))
        item.setText(f"Page {page_number + 1}")
        item.setTextAlignment(Qt.AlignCenter)
        item.setSizeHint(QSize(130, 180))  # Width for icon + padding
        
        self.list_widget.addItem(item)
        
        # Select first page by default
        if page_number == 0:
            self.list_widget.setCurrentItem(item)
    
    def clear(self):
        """Clear all thumbnails."""
        self.list_widget.clear()
        self.current_page = 0
    
    def select_page(self, page_number: int):
        """Select a page thumbnail.
        
        Args:
            page_number: The page number to select (0-based)
        """
        if 0 <= page_number < self.list_widget.count():
            item = self.list_widget.item(page_number)
            self.list_widget.setCurrentItem(item)
            self.current_page = page_number
    
    def sizeHint(self) -> QSize:
        """Suggest a size for the widget."""
        return QSize(150, 600)  # Default width for thumbnail panel
    
    def show_current_page(self):
        """Ensure current page is visible in the view."""
        if current_item := self.list_widget.currentItem():
            self.list_widget.scrollToItem(
                current_item,
                QListWidget.PositionAtCenter
            )
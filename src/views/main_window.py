from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QFileDialog, QMessageBox,
    QSplitter, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImage, QPixmap, QKeySequence, QShortcut

from src.views.toolbar import PDFToolBar
from src.views.menu_bar import PDFMenuBar
from src.views.pdf_viewer import PDFViewerWidget
from src.views.thumbnail_panel import PDFThumbnailPanel
from src.models.pdf_document import PDFDocument, PDFError

class MainWindow(QMainWindow):
    """Main window of the PDF Editor application."""
    
    def __init__(self):
        super().__init__()
        self.pdf_document = None
        self.loaded_pages = set()  # Track which pages have been loaded
        self.settings = QSettings('MaximilianDev', 'PDF-Editor')
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        self.load_settings()
    
    def setup_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("PDF Editor")
        self.setMinimumSize(QSize(1000, 600))
        
        # Create and set menu bar
        self.menu_bar = PDFMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Create and add toolbar
        self.toolbar = PDFToolBar(self)
        self.addToolBar(self.toolbar)
        
        # Create central widget with splitter
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Add thumbnail panel
        self.thumbnail_panel = PDFThumbnailPanel()
        self.splitter.addWidget(self.thumbnail_panel)
        
        # Add PDF viewer
        self.pdf_viewer = PDFViewerWidget()
        self.splitter.addWidget(self.pdf_viewer)
        
        # Set initial splitter sizes (thumbnails:viewer = 1:4)
        self.splitter.setSizes([200, 800])
        
        layout.addWidget(self.splitter)
        self.setCentralWidget(central_widget)
        
        # Create and set status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Update status bar
        self.update_status_bar()
    
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connect menu actions
        self.menu_bar.fileOpenRequested.connect(self.open_file_dialog)
        self.menu_bar.fileSaveRequested.connect(self.save_document)
        self.menu_bar.fileSaveAsRequested.connect(self.save_document_as)
        self.menu_bar.zoomInRequested.connect(self.pdf_viewer.zoom_in)
        self.menu_bar.zoomOutRequested.connect(self.pdf_viewer.zoom_out)
        self.menu_bar.zoomResetRequested.connect(self.pdf_viewer.reset_zoom)
        self.menu_bar.toggleToolbarRequested.connect(self.toggle_toolbar)
        self.menu_bar.toggleThumbnailsRequested.connect(self.toggle_thumbnails)
        
        # Connect toolbar actions
        self.toolbar.fileOpenRequested.connect(self.open_file_dialog)
        self.toolbar.fileSaveRequested.connect(self.save_document)
        self.toolbar.fileSaveAsRequested.connect(self.save_document_as)
        self.toolbar.zoomInRequested.connect(self.pdf_viewer.zoom_in)
        self.toolbar.zoomOutRequested.connect(self.pdf_viewer.zoom_out)
        self.toolbar.zoomResetRequested.connect(self.pdf_viewer.reset_zoom)
        self.toolbar.pageRequested.connect(self.pdf_viewer.go_to_page)
        
        # Connect viewer signals
        self.pdf_viewer.zoomChanged.connect(self.on_zoom_changed)
        self.pdf_viewer.pageChanged.connect(self.on_page_changed)
        
        # Connect thumbnail panel signals
        self.thumbnail_panel.pageSelected.connect(self.pdf_viewer.go_to_page)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        QShortcut(QKeySequence(Qt.ALT | Qt.Key_G), self,
                 self.toolbar.pageSpinBox.setFocus)
    
    def load_settings(self):
        """Load application settings."""
        # Load window geometry
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
            
        # Load toolbar visibility
        toolbar_visible = self.settings.value('toolbar_visible', True, type=bool)
        self.toolbar.setVisible(toolbar_visible)
        
        # Load thumbnails visibility
        thumbnails_visible = self.settings.value('thumbnails_visible', True, type=bool)
        self.thumbnail_panel.setVisible(thumbnails_visible)
        
        # Load splitter state
        splitter_state = self.settings.value('splitter_state')
        if splitter_state:
            self.splitter.restoreState(splitter_state)
        
        # Load recent files
        recent_files = self.settings.value('recent_files', [], type=list)
        for filepath in recent_files:
            self.menu_bar.add_recent_file(filepath)
    
    def save_settings(self):
        """Save application settings."""
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('toolbar_visible', self.toolbar.isVisible())
        self.settings.setValue('thumbnails_visible', self.thumbnail_panel.isVisible())
        self.settings.setValue('splitter_state', self.splitter.saveState())
        self.settings.setValue('recent_files', self.menu_bar.recent_files)
    
    def toggle_toolbar(self, visible: bool):
        """Toggle toolbar visibility.
        
        Args:
            visible: Whether to show the toolbar
        """
        self.toolbar.setVisible(visible)
    
    def toggle_thumbnails(self, visible: bool):
        """Toggle thumbnails panel visibility.
        
        Args:
            visible: Whether to show the thumbnails panel
        """
        self.thumbnail_panel.setVisible(visible)
        if visible and self.splitter.sizes()[0] < 50:
            # Restore thumbnail panel width if it was collapsed
            self.splitter.setSizes([200, 800])
    
    def on_zoom_changed(self, zoom: float):
        """Handle zoom level changes.
        
        Args:
            zoom: New zoom level
        """
        self.status_bar.showMessage(f"Zoom: {zoom*100:.0f}%", 2000)
    
    def on_page_changed(self, page: int):
        """Handle page changes.
        
        Args:
            page: New page number (0-based)
        """
        if self.pdf_document:
            # Update toolbar page controls
            self.toolbar.update_page_info(page, self.pdf_document.page_count)
            
            # Update status bar
            self.status_bar.showMessage(
                f"Page {page + 1}/{self.pdf_document.page_count} | "
                f"File: {self.pdf_document.filepath}"
            )
            
            # Load adjacent pages if not already loaded
            self.load_page_range(max(0, page - 1), min(self.pdf_document.page_count, page + 2))
    
    def load_page_range(self, start: int, end: int):
        """Load a range of pages.
        
        Args:
            start: Start page number (inclusive)
            end: End page number (exclusive)
        """
        for page in range(start, end):
            if page not in self.loaded_pages:
                pixmap = self.pdf_document.get_page_image(page)
                if pixmap:
                    # Convert PyMuPDF pixmap to Qt image
                    img = QImage(
                        pixmap.samples,
                        pixmap.width,
                        pixmap.height,
                        pixmap.stride,
                        QImage.Format_RGB888
                    )
                    # Add to viewer and thumbnails
                    self.pdf_viewer.display_page(page, img)
                    if page == 0:  # Only first page gets added immediately
                        self.thumbnail_panel.add_thumbnail(QPixmap.fromImage(img), page)
                    self.loaded_pages.add(page)
    
    def open_document(self, filepath: str) -> bool:
        """Open a PDF document.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            bool: True if document was opened successfully
        """
        try:
            # Close any existing document
            if self.pdf_document:
                self.pdf_document.close()
            
            # Create and load new document
            self.pdf_document = PDFDocument(filepath)
            
            # Clear loaded pages tracking
            self.loaded_pages.clear()
            
            # Update UI
            self.toolbar.update_actions(True)
            self.menu_bar.update_actions(True)
            
            # Set document in viewer
            self.pdf_viewer.set_document(self.pdf_document.page_count)
            
            # Clear and reset thumbnail panel
            self.thumbnail_panel.clear()
            
            # Load initial pages
            self.load_page_range(0, min(3, self.pdf_document.page_count))
            
            # Load remaining thumbnails in background
            for page in range(self.pdf_document.page_count):
                if page > 0:  # Skip first page, already added
                    pixmap = self.pdf_document.get_page_image(page, zoom=0.2)  # Small size for thumbnails
                    if pixmap:
                        img = QImage(
                            pixmap.samples,
                            pixmap.width,
                            pixmap.height,
                            pixmap.stride,
                            QImage.Format_RGB888
                        )
                        self.thumbnail_panel.add_thumbnail(QPixmap.fromImage(img), page)
            
            # Add to recent files
            self.menu_bar.add_recent_file(filepath)
            
            return True
            
        except PDFError as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF: {str(e)}")
            self.pdf_document = None
            return False
    
    def update_status_bar(self):
        """Update the status bar with document information."""
        if self.pdf_document:
            page = self.pdf_viewer.current_page
            page_count = self.pdf_document.page_count
            self.status_bar.showMessage(
                f"Page {page + 1}/{page_count} | "
                f"File: {self.pdf_document.filepath}"
            )
        else:
            self.status_bar.showMessage("No document opened")
    
    def open_file_dialog(self):
        """Show file open dialog and open selected PDF."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        if filepath:
            self.open_document(filepath)
    
    def save_document(self):
        """Save the current document."""
        if self.pdf_document and self.pdf_document.filepath:
            try:
                self.pdf_document.save(self.pdf_document.filepath)
                self.status_bar.showMessage("Document saved", 2000)
            except PDFError as e:
                QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")
    
    def save_document_as(self):
        """Show save as dialog and save document to selected location."""
        if not self.pdf_document:
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        if filepath:
            try:
                self.pdf_document.save(filepath)
                self.status_bar.showMessage("Document saved", 2000)
            except PDFError as e:
                QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for PDF files.
        
        Args:
            event: The drag enter event
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().lower().endswith('.pdf'):
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for PDF files.
        
        Args:
            event: The drop event
        """
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            self.open_document(filepath)
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.pdf_document:
            self.pdf_document.close()
        self.save_settings()
        event.accept()

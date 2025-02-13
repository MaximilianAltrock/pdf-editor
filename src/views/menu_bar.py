from PySide6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal, Qt

class PDFMenuBar(QMenuBar):
    """Menu bar for the PDF Editor application."""
    
    # Signals for menu actions
    fileOpenRequested = Signal()
    fileSaveRequested = Signal()
    fileSaveAsRequested = Signal()
    zoomInRequested = Signal()
    zoomOutRequested = Signal()
    zoomResetRequested = Signal()
    toggleToolbarRequested = Signal(bool)
    toggleThumbnailsRequested = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_files = []  # Store recent file paths
        self.setup_menus()
        
    def setup_menus(self):
        """Set up all menus and their actions."""
        # File menu
        self.file_menu = QMenu("&File", self)
        self.addMenu(self.file_menu)
        
        # Open action
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)  # Ctrl+O
        open_action.setStatusTip("Open a PDF file")
        open_action.triggered.connect(self.fileOpenRequested.emit)
        self.file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = QMenu("Recent Files", self)
        self.file_menu.addMenu(self.recent_menu)
        
        self.file_menu.addSeparator()
        
        # Save action
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)  # Ctrl+S
        self.save_action.setStatusTip("Save the current document")
        self.save_action.triggered.connect(self.fileSaveRequested.emit)
        self.save_action.setEnabled(False)
        self.file_menu.addAction(self.save_action)
        
        # Save As action
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)  # Ctrl+Shift+S
        self.save_as_action.setStatusTip("Save the document to a new location")
        self.save_as_action.triggered.connect(self.fileSaveAsRequested.emit)
        self.save_as_action.setEnabled(False)
        self.file_menu.addAction(self.save_as_action)
        
        self.file_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)  # Ctrl+Q
        quit_action.setStatusTip("Quit the application")
        quit_action.triggered.connect(self.parent().close)
        self.file_menu.addAction(quit_action)
        
        # View menu
        view_menu = QMenu("&View", self)
        self.addMenu(view_menu)
        
        # Sidebars submenu
        sidebar_menu = QMenu("Sidebars", self)
        view_menu.addMenu(sidebar_menu)
        
        # Show/Hide Thumbnails
        toggle_thumbnails = QAction("Thumbnails Panel", self)
        toggle_thumbnails.setCheckable(True)
        toggle_thumbnails.setChecked(True)
        toggle_thumbnails.setShortcut("F9")
        toggle_thumbnails.setStatusTip("Show or hide the thumbnails panel")
        toggle_thumbnails.triggered.connect(self.toggleThumbnailsRequested.emit)
        sidebar_menu.addAction(toggle_thumbnails)
        
        # Show/Hide Toolbar
        toggle_toolbar = QAction("Toolbar", self)
        toggle_toolbar.setCheckable(True)
        toggle_toolbar.setChecked(True)
        toggle_toolbar.setShortcut("F8")
        toggle_toolbar.setStatusTip("Show or hide the toolbar")
        toggle_toolbar.triggered.connect(self.toggleToolbarRequested.emit)
        sidebar_menu.addAction(toggle_toolbar)
        
        view_menu.addSeparator()
        
        # Zoom submenu
        zoom_menu = QMenu("Zoom", self)
        view_menu.addMenu(zoom_menu)
        
        # Zoom actions
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)  # Ctrl++
        zoom_in_action.setStatusTip("Increase zoom level")
        zoom_in_action.triggered.connect(self.zoomInRequested.emit)
        zoom_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)  # Ctrl+-
        zoom_out_action.setStatusTip("Decrease zoom level")
        zoom_out_action.triggered.connect(self.zoomOutRequested.emit)
        zoom_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.setStatusTip("Reset zoom to 100%")
        reset_zoom_action.triggered.connect(self.zoomResetRequested.emit)
        zoom_menu.addAction(reset_zoom_action)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        self.addMenu(help_menu)
        
        # Keyboard shortcuts help
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setStatusTip("Show keyboard shortcuts")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
    def update_actions(self, document_loaded: bool):
        """Update action states based on whether a document is loaded.
        
        Args:
            document_loaded: Whether a PDF document is currently loaded
        """
        self.save_action.setEnabled(document_loaded)
        self.save_as_action.setEnabled(document_loaded)
        
    def add_recent_file(self, filepath: str):
        """Add a file to the recent files list.
        
        Args:
            filepath: Path to the file to add
        """
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        self.recent_files = self.recent_files[:5]  # Keep only 5 most recent
        self.update_recent_menu()
        
    def update_recent_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        for filepath in self.recent_files:
            action = QAction(filepath, self)
            action.triggered.connect(lambda f=filepath: self.open_recent_file(f))
            self.recent_menu.addAction(action)
            
    def open_recent_file(self, filepath: str):
        """Open a file from the recent files list.
        
        Args:
            filepath: Path to the file to open
        """
        # Emit the open signal - MainWindow will handle the actual opening
        self.fileOpenRequested.emit()
        
    def show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        shortcuts = """
        <h2>Keyboard Shortcuts</h2>
        <table>
        <tr><th>Action</th><th>Shortcut</th></tr>
        <tr><td>Open File</td><td>Ctrl+O</td></tr>
        <tr><td>Save</td><td>Ctrl+S</td></tr>
        <tr><td>Save As</td><td>Ctrl+Shift+S</td></tr>
        <tr><td>Zoom In</td><td>Ctrl++</td></tr>
        <tr><td>Zoom Out</td><td>Ctrl+-</td></tr>
        <tr><td>Reset Zoom</td><td>Ctrl+0</td></tr>
        <tr><td>Toggle Thumbnails</td><td>F9</td></tr>
        <tr><td>Toggle Toolbar</td><td>F8</td></tr>
        <tr><td>Go to Page</td><td>Alt+G</td></tr>
        <tr><td>Quit</td><td>Ctrl+Q</td></tr>
        </table>
        
        <p>Mouse & Trackpad:</p>
        <ul>
        <li>Scroll to navigate through pages</li>
        <li>Ctrl + scroll to zoom at cursor position</li>
        <li>Click thumbnails to jump to pages</li>
        <li>Drag splitter to resize panels</li>
        </ul>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)
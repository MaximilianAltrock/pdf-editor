from PySide6.QtWidgets import QToolBar, QStyle, QSpinBox, QLabel
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QSize

class PDFToolBar(QToolBar):
    """Main toolbar for the PDF Editor application."""
    
    # Signals
    fileOpenRequested = Signal()
    fileSaveRequested = Signal()
    fileSaveAsRequested = Signal()
    zoomInRequested = Signal()
    zoomOutRequested = Signal()
    zoomResetRequested = Signal()
    previousPageRequested = Signal()
    nextPageRequested = Signal()
    pageRequested = Signal(int)  # Emitted with requested page number (0-based)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(24, 24))
        self.setup_actions()
    
    def setup_actions(self):
        """Set up toolbar actions."""
        # File operations
        self.openAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_DialogOpenButton),
            text="Open PDF",
            tooltip="Open a PDF file (Ctrl+O)",
            triggered=self.fileOpenRequested.emit
        )
        
        self.saveAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_DialogSaveButton),
            text="Save",
            tooltip="Save current document (Ctrl+S)",
            triggered=self.fileSaveRequested.emit
        )
        
        self.saveAsAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_DriveFDIcon),
            text="Save As",
            tooltip="Save document as (Ctrl+Shift+S)",
            triggered=self.fileSaveAsRequested.emit
        )
        
        # Page navigation
        self.previousPageAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_ArrowLeft),
            text="Previous",
            tooltip="Go to previous page (Alt+Left)",
            triggered=self.previousPageRequested.emit
        )
        
        # Page number controls
        self.pageSpinBox = QSpinBox(self)
        self.pageSpinBox.setMinimum(1)
        self.pageSpinBox.setMaximum(1)
        self.pageSpinBox.setValue(1)
        self.pageSpinBox.setFixedWidth(70)
        self.pageSpinBox.setToolTip("Current page (Alt+G)")
        self.pageSpinBox.setStatusTip("Enter page number to go to that page")
        self.pageSpinBox.valueChanged.connect(
            lambda value: self.pageRequested.emit(value - 1)
        )
        
        # Total pages label
        self.totalPagesLabel = QLabel(" / 1", self)
        self.totalPagesLabel.setStyleSheet("""
            QLabel {
                color: #d4d4d4;
                padding: 0 5px;
            }
        """)
        
        self.nextPageAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_ArrowRight),
            text="Next",
            tooltip="Go to next page (Alt+Right)",
            triggered=self.nextPageRequested.emit
        )
        
        # View operations
        self.zoomOutAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_ArrowDown),
            text="Zoom Out",
            tooltip="Decrease zoom level (Ctrl+-)",
            triggered=self.zoomOutRequested.emit
        )
        
        self.zoomInAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_ArrowUp),
            text="Zoom In",
            tooltip="Increase zoom level (Ctrl++)",
            triggered=self.zoomInRequested.emit
        )
        
        self.zoomResetAction = self._create_action(
            icon=self.style().standardIcon(QStyle.SP_BrowserReload),
            text="100%",
            tooltip="Reset zoom to 100% (Ctrl+0)",
            triggered=self.zoomResetRequested.emit
        )
        
        # Add separators and actions
        self.addAction(self.openAction)
        self.addSeparator()
        self.addAction(self.saveAction)
        self.addAction(self.saveAsAction)
        self.addSeparator()
        self.addAction(self.previousPageAction)
        self.addWidget(self.pageSpinBox)
        self.addWidget(self.totalPagesLabel)
        self.addAction(self.nextPageAction)
        self.addSeparator()
        self.addAction(self.zoomOutAction)
        self.addAction(self.zoomInAction)
        self.addAction(self.zoomResetAction)
        
        # Set style for spinbox
        self.pageSpinBox.setStyleSheet("""
            QSpinBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 2px;
            }
            QSpinBox:hover {
                border: 1px solid #007acc;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background: #3d3d3d;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #4d4d4d;
            }
        """)
        
        # Initially disable document-specific actions
        self.update_actions(False)
    
    def _create_action(self, icon: QIcon, text: str, tooltip: str, triggered) -> QAction:
        """Create a toolbar action.
        
        Args:
            icon: Icon for the action
            text: Action text
            tooltip: Tooltip text
            triggered: Slot to connect to triggered signal
            
        Returns:
            QAction: The created action
        """
        action = QAction(icon, text, self)
        action.setToolTip(tooltip)
        action.setStatusTip(tooltip)
        action.triggered.connect(triggered)
        return action
    
    def update_actions(self, document_loaded: bool):
        """Update action states based on whether a document is loaded.
        
        Args:
            document_loaded: Whether a PDF document is currently loaded
        """
        self.saveAction.setEnabled(document_loaded)
        self.saveAsAction.setEnabled(document_loaded)
        self.zoomInAction.setEnabled(document_loaded)
        self.zoomOutAction.setEnabled(document_loaded)
        self.zoomResetAction.setEnabled(document_loaded)
        self.previousPageAction.setEnabled(document_loaded)
        self.nextPageAction.setEnabled(document_loaded)
        self.pageSpinBox.setEnabled(document_loaded)
    
    def update_page_info(self, current_page: int, total_pages: int):
        """Update page navigation controls.
        
        Args:
            current_page: Current page number (0-based)
            total_pages: Total number of pages
        """
        # Update spinbox without triggering valueChanged
        self.pageSpinBox.blockSignals(True)
        self.pageSpinBox.setMaximum(max(1, total_pages))
        self.pageSpinBox.setValue(current_page + 1)
        self.pageSpinBox.blockSignals(False)
        
        # Update total pages label
        self.totalPagesLabel.setText(f" / {total_pages}")
        
        # Update navigation buttons
        self.previousPageAction.setEnabled(current_page > 0)
        self.nextPageAction.setEnabled(current_page < total_pages - 1)
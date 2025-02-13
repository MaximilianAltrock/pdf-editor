from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class Theme:
    """Manages application theming."""
    
    # Dark theme colors
    BACKGROUND = "#1e1e1e"
    BACKGROUND_LIGHT = "#252526"
    FOREGROUND = "#d4d4d4"
    ACCENT = "#007acc"
    ACCENT_LIGHT = "#1f8ad2"
    BORDER = "#3d3d3d"
    HOVER = "#2a2d2e"
    
    @staticmethod
    def apply_dark_theme(app) -> None:
        """Apply dark theme to the application.
        
        Args:
            app: QApplication instance
        """
        palette = QPalette()
        
        # Set background colors
        palette.setColor(QPalette.Window, QColor(Theme.BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(Theme.FOREGROUND))
        palette.setColor(QPalette.Base, QColor(Theme.BACKGROUND_LIGHT))
        palette.setColor(QPalette.AlternateBase, QColor(Theme.BACKGROUND))
        
        # Set text colors
        palette.setColor(QPalette.Text, QColor(Theme.FOREGROUND))
        palette.setColor(QPalette.ButtonText, QColor(Theme.FOREGROUND))
        
        # Set button colors
        palette.setColor(QPalette.Button, QColor(Theme.BACKGROUND_LIGHT))
        
        # Set selection colors
        palette.setColor(QPalette.Highlight, QColor(Theme.ACCENT))
        palette.setColor(QPalette.HighlightedText, QColor(Theme.FOREGROUND))
        
        # Set tooltip colors
        palette.setColor(QPalette.ToolTipBase, QColor(Theme.BACKGROUND_LIGHT))
        palette.setColor(QPalette.ToolTipText, QColor(Theme.FOREGROUND))
        
        # Set disabled state colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(Theme.BORDER))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(Theme.BORDER))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(Theme.BORDER))
        
        # Apply palette to application
        app.setPalette(palette)
        
        # Set stylesheet for custom styling
        app.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QToolBar {
                background-color: #252526;
                border-bottom: 1px solid #3d3d3d;
                spacing: 4px;
                padding: 2px;
            }
            
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }
            
            QToolBar QToolButton:hover {
                background-color: #2a2d2e;
                border: 1px solid #3d3d3d;
            }
            
            QToolBar QToolButton:pressed {
                background-color: #3d3d3d;
            }
            
            QStatusBar {
                background-color: #252526;
                border-top: 1px solid #3d3d3d;
                color: #d4d4d4;
            }
            
            QDockWidget {
                titlebar-close-icon: url(resources/icons/close.png);
                titlebar-normal-icon: url(resources/icons/float.png);
            }
            
            QDockWidget::title {
                background-color: #252526;
                padding: 6px;
                border-bottom: 1px solid #3d3d3d;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #1e1e1e;
                width: 14px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                min-height: 20px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #4d4d4d;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: #1e1e1e;
                height: 14px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #3d3d3d;
                min-width: 20px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #4d4d4d;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.views.main_window import MainWindow
from src.views.theme import Theme

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Apply dark theme
    Theme.apply_dark_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
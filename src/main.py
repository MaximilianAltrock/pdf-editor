import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Editor")
    app.setOrganizationName("PDF Tool Python")

    window = MainWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
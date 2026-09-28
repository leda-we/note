import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.styles import APP_STYLE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Book Note")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

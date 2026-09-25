from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit

class BookEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Начните писать...")

        font = QFont("Georgia", 14)
        self.setFont(font)

        self.document().setDocumentMargin(45)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        self.setAcceptRichText(True)
        self.setStyleSheet("""QTextEdit{
        border: none;
        background-color: white;
        padding: 10px;
        }
    """)
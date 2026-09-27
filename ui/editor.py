from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt, Signal
class BookEditor(QTextEdit):
    link_requested = Signal(str)
    link_clicked = Signal(str)

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
        self.pending_link_cursor = None

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        cursor = self.textCursor()
        create_link_action = None
        if cursor.hasSelection():
            menu.addSeparator()

            create_link_action = menu.addAction("Создать ссылку")
        selected_action = menu.exec(event.globalPos())
        if (create_link_action is not None and selected_action == create_link_action):
            self.pending_link_cursor = cursor
            selected_text = cursor.selectedText()
            self.link_requested.emit(selected_text)
    def apply_internal_link(self, item_id, item_name, item_type):
        if self.pending_link_cursor is None:
            return
        cursor = self.pending_link_cursor

        char_format = QTextCharFormat()
        char_format.setAnchor(True)
        char_format.setAnchorHref(f"book://{item_id}")
        char_format.setFontUnderline(True)
        char_format.setToolTip(f"{item_type}: {item_name}")
        cursor.mergeCharFormat(char_format)
        self.pending_link_cusor = None
    
    def mousePressEvent(self, event):
        ctrl_pressed = (event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        left_button = (event.button() == Qt.MouseButton.LeftButton)
        if ctrl_pressed and left_button:
            position = event.position().toPoint()

            link = self.anchorAt(position)
            if link.startswith("book://"):
                item_id = link.removeprefix("book://")
                self.link_clicked.emit(item_id)
                event.accept()
                return
        super().mousePressEvent(event)
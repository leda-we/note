from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QColor
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt, Signal


class BookEditor(QTextEdit):
    link_requested = Signal(str)
    link_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Начните писать…")
        self.setFont(QFont("Georgia", 15))
        self.document().setDocumentMargin(38)
        self.document().setDefaultStyleSheet("p { line-height: 145%; margin-bottom: 16px; }")
        self.setTabStopDistance(40)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setAcceptRichText(True)
        self.pending_link_cursor = None

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        cursor = self.textCursor()
        create_link = None
        if cursor.hasSelection():
            menu.addSeparator()
            create_link = menu.addAction("Ссылка на объект…")
        chosen = menu.exec(event.globalPos())
        if create_link is not None and chosen == create_link:
            self.pending_link_cursor = QTextCursor(cursor)
            try:
                self.link_requested.emit(cursor.selectedText())
            finally:
                self.pending_link_cursor = None
        menu.deleteLater()

    def apply_internal_link(self, item_id, item_name, item_type):
        if self.pending_link_cursor is None:
            return
        cursor = self.pending_link_cursor
        fmt = QTextCharFormat()
        fmt.setAnchor(True)
        fmt.setAnchorHref(f"book://{item_id}")
        fmt.setFontUnderline(True)
        fmt.setForeground(QColor("#c8a36d"))
        fmt.setToolTip(f"{item_type}: {item_name}")
        cursor.mergeCharFormat(fmt)
        self.pending_link_cursor = None

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.button() == Qt.MouseButton.LeftButton:
            link = self.anchorAt(event.position().toPoint())
            if link.startswith("book://"):
                self.link_clicked.emit(link.removeprefix("book://"))
                event.accept()
                return
        super().mousePressEvent(event)

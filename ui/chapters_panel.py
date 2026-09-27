import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *

class ChapterPanel(QWidget):
    chapter_selected = Signal(str)
    chapter_created = Signal(str, str)
    chapter_renamed = Signal(str, str)
    chapter_deleted = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)
        layout = QVBoxLayout(self)
        title = QLabel("Chapters")
        self.chapters_list = QListWidget()
        layout.addWidget(title)
        layout.addWidget(self.chapters_list)

        self.chapters_list.currentItemChanged.connect(self.on_chapter_changed)
        self.chapters_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chapters_list.customContextMenuRequested.connect(self.open_context_menu)

    def create_chapter(self):
        title, ok = QInputDialog.getText(self, "New chapter", "Название главы:")
        if not ok or not title.strip():
            return
        chapter_id = str(uuid.uuid4())

        item = self.add_chapter(chapter_id, title.strip())
        self.chapter_created.emit(chapter_id, title.strip())
        self.chapters_list.setCurrentItem(item)

    def rename_chapter(self, item):
        old_title = item.text()

        new_title, ok = QInputDialog.getText(
            self,
            "Переименовать главу",
            "Новое название:",
            text=old_title
        )

        if not ok or not new_title.strip():
            return

        chapter_id = item.data(Qt.ItemDataRole.UserRole)
        item.setText(new_title.strip())
        self.chapter_renamed.emit(
            chapter_id,
            new_title.strip()
        )

    def delete_chapter(self, item):
        chapter_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        row = self.chapters_list.row(item)
        self.chapters_list.takeItem(row)
        self.chapter_deleted.emit(chapter_id)

    def on_chapter_changed(self, current, previous):
        if current is None:
            return
        chapter_id = current.data(
            Qt.ItemDataRole.UserRole
        )
        self.chapter_selected.emit(chapter_id)

    def open_context_menu(self, position):
        item = self.chapters_list.itemAt(position)

        menu = QMenu(self)
        create_action = menu.addAction("New chapter")
        rename_action = None
        delete_action = None

        if item is not None:
            menu.addSeparator()
            rename_action = menu.addAction("Rename")
            delete_action = menu.addAction("Delete")

        selected_action = menu.exec(
            self.chapters_list.mapToGlobal(position)
        )

        if selected_action is None:
            return

        if selected_action == create_action:
            self.create_chapter()

        elif item is not None and selected_action == rename_action:
            self.rename_chapter(item)

        elif item is not None and selected_action == delete_action:
            self.delete_chapter(item)

    def add_chapter(self, chapter_id, title):
        item = QListWidgetItem(title)
        item.setData(
            Qt.ItemDataRole.UserRole,
            chapter_id
        )
        self.chapters_list.addItem(item)

        return item
    
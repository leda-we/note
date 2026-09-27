from PySide6.QtWidgets import *
from ui.editor import BookEditor
from ui.chapters_panel import ChapterPanel
from database.database import Database
from PySide6.QtCore import *
from ui.inspiration_panel import InspirationPanel
from PySide6.QtGui import *
import uuid
from ui.object_panel import ObjectPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = Database()

        self.setWindowTitle("Book Note")
        self.resize(1200, 750)

        self.chapters = {}
        self.current_chapter_id = None

        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(700)
        self.save_timer.timeout.connect(self.save_current_chapter)

        self.object_save_timer = QTimer(self)
        self.object_save_timer.setSingleShot(True)
        self.object_save_timer.setInterval(700)
        self.object_save_timer.timeout.connect(self.save_current_object)
        

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        self.chapter_panel = ChapterPanel()

        self.editor = BookEditor()
        self.inspiration_panel = InspirationPanel()
        self.inspiration_panel.hide()
        self.object_panel = ObjectPanel()
        self.object_panel.hide()
        self.current_linked_item_id = None

        editor_container = QWidget()
        editor_layout = QHBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        

        editor_layout.addStretch()
        editor_layout.addWidget(self.editor)
        editor_layout.addStretch()

        self.editor.setMaximumWidth(850)
        self.editor.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding,
        )
        self.editor.link_requested.connect(self.create_link)

        main_layout.addWidget(self.chapter_panel)
        main_layout.addWidget(editor_container)
        main_layout.addWidget(self.inspiration_panel)
        main_layout.addWidget(self.object_panel)

        self.chapter_panel.chapter_created.connect(
            self.create_chapter
        )

        self.chapter_panel.chapter_selected.connect(
            self.open_chapter
        )
        self.chapter_panel.chapter_renamed.connect(
            self.rename_chapter
        )
        self.chapter_panel.chapter_deleted.connect(
            self.delete_chapter
        )

        self.editor.textChanged.connect(
            self.schedule_save
        )
        self.editor.link_clicked.connect(self.open_linked_item)

        self.object_panel.description_changed.connect(self.schedule_object_save)

        self.load_chapters()

        self.inspiration_shortcut = QShortcut(QKeySequence("ctrl+I"), self)
        self.inspiration_shortcut.activated.connect(self.toggle_inspiration_panel)



    def create_chapter(self, chapter_id, title):
        position = len(self.chapters)
        self.chapters[chapter_id] = {
            "title:": title,
            "text": "",
            "html": "",
        }
        self.db.create_chapter(
            chapter_id,
            title,
            position
        )
    def open_chapter(self,chapter_id):
        self.save_timer.stop()
        self.save_current_chapter()
        self.current_chapter_id = chapter_id
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return
        self.editor.blockSignals(True)
        if chapter["html"]:
            self.editor.setHtml(chapter["html"])
        else:
            self.editor.setPlainText(chapter["text"])

        self.editor.blockSignals(False)

    def save_current_chapter(self):
        if self.current_chapter_id is None:
            return
        if self.current_chapter_id not in self.chapters:
            return

        text = self.editor.toPlainText()
        content_html = self.editor.toHtml()

        self.chapters[
            self.current_chapter_id
        ]["text"] = text

        self.chapters[self.current_chapter_id]["html"] = content_html

        self.db.update_chapter_content(
            self.current_chapter_id,
            text,
            content_html,
        )

    def rename_chapter(self, chapter_id, new_title):
        if chapter_id not in self.chapters:
            return

        self.chapters[chapter_id]["title"] = new_title

        self.db.rename_chapter(
            chapter_id,
            new_title
        )

    def delete_chapter(self, chapter_id):
        if chapter_id not in self.chapters:
            return
        del self.chapters[chapter_id]

        self.db.delete_chapter(chapter_id)

        if self.current_chapter_id == chapter_id:
            self.current_chapter_id = None

            self.editor.blockSignals(True)
            self.editor.clear()
            self.editor.blockSignals(False)

    def load_chapters(self):
        chapters = self.db.get_chapters()

        for chapter in chapters:
            chapter_id = chapter["id"]

            self.chapters[chapter_id] = {
                "title": chapter["title"],
                "text": chapter["text"],
                "html": chapter["content_html"],
            }
            self.chapter_panel.add_chapter(
                chapter_id,
                chapter["title"]
            )

        if self.chapter_panel.chapters_list.count() > 0:
            self.chapter_panel.chapters_list.setCurrentRow(0)

    def schedule_save(self):
        self.save_timer.start()

    def closeEvent(self, event):
        self.save_timer.stop()
        self.save_current_chapter()
        event.accept()

    def toggle_inspiration_panel(self):
        if self.inspiration_panel.isVisible():
            self.inspiration_panel.hide()
        else:
            self.object_panel.hide()

            self.inspiration_panel.show()

    def create_link(self, selected_text):
        item_types = ["Персонаж", "Локация", "Заметка"]
        item_type, ok = QInputDialog.getItem(self, "Создать ссылку", "Тип:", item_types, 0, False)
        if not ok:
            return
        item_name, ok = QInputDialog.getText(self, "Название", "Название объекта:", text=selected_text)
        if not ok or not item_name.strip():
            return
        item_id = str(uuid.uuid4())
        type_map = {
            "Персонаж": "character",
            "Локация": "location",
            "Заметка": "note",
        }
        internal_type = type_map[item_type]
        self.db.create_linked_item(item_id, item_name.strip(), internal_type)
        self.editor.apply_internal_link(item_id, item_name.strip(), item_type)
        self.schedule_save()

    def open_linked_item(self, item_id):
        item = self.db.get_linked_item(item_id)
        if item is None:
            return
        self.current_linked_item_id = item_id

        type_names = {
            "character": "Персонаж",
            "location": "Локация",
            "note": "Заметка",
        }

        item_type = type_names.get(item["item_type"], item["item_type"])
        self.inspiration_panel.hide()
        self.object_panel.show_item(item["name"], item_type, item["description"])
        self.object_panel.show()

    def schedule_object_save(self):
        if self.current_linked_item_id is None:
            return
        self.object_save_timer.start()

    def save_current_object(self):
        if self.current_linked_item_id is None:
            return
        description = (self.object_panel.description_editor.toPlainText())
        self.db.update_linked_item_description(self.current_linked_item_id, description)

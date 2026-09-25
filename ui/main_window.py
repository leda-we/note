from PySide6.QtWidgets import *
from ui.editor import BookEditor
from ui.chapters_panel import ChapterPanel
from database.database import Database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = Database()

        self.setWindowTitle("Book Note")
        self.resize(1200, 750)

        self.chapters = {}
        self.current_chapter_id = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        self.chapter_panel = ChapterPanel()

        self.editor = BookEditor()

        editor_container = QWidget()
        editor_layout = QHBoxLayout(editor_container)

        editor_layout.addStretch()
        editor_layout.addWidget(self.editor)
        editor_layout.addStretch()

        self.editor.setMaximumWidth(850)
        self.editor.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding,
        )
        main_layout.addWidget(self.chapter_panel)
        main_layout.addWidget(editor_container)

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
            self.save_current_chapter
        )
        self.load_chapters()

    def create_chapter(self, chapter_id, title):
        position = len(self.chapters)
        self.chapters[chapter_id] = {
            "title:": title,
            "text": "",
        }
        self.db.create_chapter(
            chapter_id,
            title,
            position
        )
    def open_chapter(self,chapter_id):
        self.save_current_chapter()
        self.current_chapter_id = chapter_id
        chapter = self.chapters.get(chapter_id)
        if chapter is None:
            return
        self.editor.blockSignals(True)
        self.editor.setPlainText(
            chapter["text"]
        )
        self.editor.blockSignals(False)

    def save_current_chapter(self):
        if self.current_chapter_id is None:
            return
        if self.current_chapter_id not in self.chapters:
            return

        text = self.editor.toPlainText()

        self.chapters[
            self.current_chapter_id
        ]["text"] = text

        self.db.update_chapter_text(
            self.current_chapter_id,
            text
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
            }

            self.chapter_panel.add_chapter(
                chapter_id,
                chapter["title"]
            )
        if self.chapter_panel.chapters_list.count() > 0:
            self.chapter_panel.chapters_list.setCurrentRow(0)

        
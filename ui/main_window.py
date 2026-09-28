import json
import re
import shutil
import sqlite3
import uuid
from html import escape
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QByteArray
from PySide6.QtGui import QKeySequence, QShortcut, QPixmap, QTextDocument, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QVBoxLayout, QSplitter, QStackedWidget, QListWidget,
    QListWidgetItem, QInputDialog, QMessageBox, QFileDialog, QMenu, QSizePolicy,
)
from database.database import Database
from database.library import Library
from ui.library_page import LibraryPage
from ui.font_dialog import FontDialog
from ui.clipboard_image import clipboard_image
from ui.paper_surface import PaperSurface
from ui.chapters_panel import ChapterPanel
from ui.editor import BookEditor
from ui.editor_toolbar import EditorToolbar
from ui.object_panel import ObjectPanel
from ui.icons import make_icon
from ui.animated_button import LibraryButton
from ui.inspiration_panel import InspirationPanel

TYPES = {"character": "Персонаж", "location": "Локация", "note": "Заметка"}


class MainWindow(QMainWindow):
    def __init__(self, database_path=None):
        super().__init__()
        self._closed = False
        initial_path = Path(database_path).resolve() if database_path else Path(__file__).resolve().parent.parent / "book_writer.db"
        self.library = Library(initial_path.parent)
        self.library.register(initial_path)
        selected_path = initial_path if database_path else (self.library.last_book() or initial_path)
        self.db = Database(selected_path)
        self.library.mark_opened(self.db.path)
        self.current_chapter_id = None
        self.current_linked_item_id = None
        self.chapter_dirty = False
        self.object_dirty = False
        self.category = "all"
        self.focus_mode = False
        self.chapters = {}
        self.setWindowTitle("Book Note — мастерская писателя")
        self.resize(1440, 940)
        self.setMinimumSize(1100, 700)
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(700)
        self.save_timer.timeout.connect(self.save_current_chapter)
        self.object_save_timer = QTimer(self)
        self.object_save_timer.setSingleShot(True)
        self.object_save_timer.setInterval(700)
        self.object_save_timer.timeout.connect(self.save_current_object)
        self.build_ui()
        self.connect_signals()
        self.reload_tree()
        last = self.db.setting("last_chapter")
        if last not in self.chapters:
            last = next(iter(self.chapters), None)
        if last:
            self.open_chapter(last)
        else:
            self.set_empty_editor()
        self.refresh_catalog()
        geometry = self.db.setting("geometry")
        if geometry:
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode()))
        try:
            values = json.loads(self.db.setting("splitter"))
            if isinstance(values, list) and len(values) == 3 and all(isinstance(v, int) and v > 0 for v in values):
                self.workspace_splitter.setSizes(values)
        except (ValueError, TypeError):
            pass
        last_object = self.db.setting("last_object")
        if last_object and self.db.get_linked_item(last_object):
            self.open_linked_item(last_object)
        self.shortcuts = []
        for key, callback in [
            ("Ctrl+N", lambda: self.create_chapter(self.chapter_panel.selected_part())),
            ("Ctrl+S", self.save_all), ("Ctrl+F", self.show_search),
            ("F11", self.toggle_focus), ("Ctrl+Shift+I", self.toggle_inspiration_panel),
        ]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)
        self.statusBar().showMessage("Готово · Ctrl+N — новая глава · Ctrl+K — ссылка · F11 — фокус")

    def build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        header = QFrame()
        header.setObjectName("appHeader")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 16, 0)
        self.book_title = QPushButton(self.db.setting("book_title", "Моя книга"))
        self.book_title.setIcon(make_icon("book"))
        self.book_title.setObjectName("bookTitle")
        self.book_title.setToolTip("Изменить название книги")
        self.book_title.clicked.connect(self.edit_book)
        library_button = LibraryButton("Библиотека")
        self.library_button = library_button
        library_button.setObjectName("libraryButton")
        library_button.setIcon(make_icon("all"))
        library_button.clicked.connect(self.show_library)
        header_layout.addWidget(library_button)
        header_layout.addSpacing(14)
        header_layout.addWidget(self.book_title)
        self.chapter_title_label = QLabel("Ваша история начинается здесь")
        self.chapter_title_label.setTextFormat(Qt.TextFormat.PlainText)
        self.chapter_title_label.setObjectName("chapterTitle")
        self.chapter_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chapter_title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(self.chapter_title_label, 1)
        for text, tip, callback in [
            ("Поиск", "Найти текст в главе · Ctrl+F", self.show_search),
            ("Фокус", "Скрыть боковые панели · F11", self.toggle_focus),
            ("···", "Действия с книгой", self.show_book_menu),
        ]:
            button = QPushButton(text if text == "···" else "")
            if text != "···":
                button.setIcon(make_icon("search" if text == "Поиск" else "focus"))
                button.setAccessibleName(text)
                button.setFixedSize(34, 34)
            button.setToolTip(tip)
            button.clicked.connect(callback)
            header_layout.addWidget(button)
        root.addWidget(header)
        self.workspace_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.workspace_splitter.setHandleWidth(1)
        self.workspace_splitter.setChildrenCollapsible(False)
        root.addWidget(self.workspace_splitter, 1)
        self.chapter_panel = ChapterPanel()
        self.workspace_splitter.addWidget(self.chapter_panel)
        center = QFrame()
        center.setObjectName("editorContainer")
        center.setMinimumWidth(490)
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        self.editor = BookEditor()
        self.editor.setObjectName("bookEditor")
        self.editor_toolbar = EditorToolbar(self.editor)
        toolbar_container = QWidget()
        toolbar_container.setObjectName("toolbarContainer")
        toolbar_layout = QVBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(12, 10, 12, 0)
        toolbar_layout.addWidget(self.editor_toolbar)
        center_layout.addWidget(toolbar_container)
        self.search_bar = QWidget()
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(16, 6, 16, 6)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Найти в текущей главе…")
        self.search_input.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_input, 1)
        find_button = QPushButton("Далее")
        find_button.clicked.connect(self.find_next)
        search_layout.addWidget(find_button)
        close_search = QPushButton("×")
        close_search.clicked.connect(self.search_bar.hide)
        search_layout.addWidget(close_search)
        center_layout.addWidget(self.search_bar)
        self.search_bar.hide()
        page_container = QWidget()
        page_container.setObjectName("pageContainer")
        page_layout = QHBoxLayout(page_container)
        page_layout.setContentsMargins(28, 18, 28, 18)
        paper = PaperSurface()
        paper.setMaximumWidth(850)
        paper_layout = QVBoxLayout(paper)
        paper_layout.setContentsMargins(1, 26, 1, 12)
        paper_layout.setSpacing(0)
        self.page_kicker = QLabel()
        self.page_kicker.setObjectName("pageKicker")
        self.page_kicker.setAlignment(Qt.AlignmentFlag.AlignCenter)
        paper_layout.addWidget(self.page_kicker)
        self.page_title = QLabel()
        self.page_title.setTextFormat(Qt.TextFormat.PlainText)
        self.page_title.setObjectName("pageTitle")
        self.page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_title.setWordWrap(True)
        paper_layout.addWidget(self.page_title)
        ornament = QLabel("────  ❖  ────")
        ornament.setObjectName("ornament")
        ornament.setAlignment(Qt.AlignmentFlag.AlignCenter)
        paper_layout.addWidget(ornament)
        paper_layout.addWidget(self.editor, 1)
        page_layout.addWidget(paper, 1)
        center_layout.addWidget(page_container, 1)
        self.workspace_splitter.addWidget(center)
        self.right_panel = QFrame()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setMinimumWidth(285)
        self.right_panel.setMaximumWidth(430)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        tools = QHBoxLayout()
        catalog = QPushButton("Объекты")
        catalog.clicked.connect(self.show_catalog)
        inspiration = QPushButton("Вдохновение")
        inspiration.setToolTip("Ctrl+Shift+I")
        inspiration.clicked.connect(self.toggle_inspiration_panel)
        tools.addWidget(catalog)
        tools.addWidget(inspiration)
        right_layout.addLayout(tools)
        self.right_stack = QStackedWidget()
        right_layout.addWidget(self.right_stack, 1)
        self.catalog_page = QWidget()
        catalog_layout = QVBoxLayout(self.catalog_page)
        catalog_layout.setContentsMargins(0, 10, 0, 0)
        self.catalog_title = QLabel("МИР ВАШЕЙ КНИГИ")
        self.catalog_title.setObjectName("eyebrow")
        catalog_layout.addWidget(self.catalog_title)
        self.object_search = QLineEdit()
        self.object_search.setPlaceholderText("Поиск объектов…")
        self.object_search.textChanged.connect(self.refresh_catalog)
        catalog_layout.addWidget(self.object_search)
        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(lambda row: self.open_linked_item(row.data(Qt.ItemDataRole.UserRole)))
        catalog_layout.addWidget(self.object_list, 1)
        self.catalog_hint = QLabel("Создавайте персонажей, места и заметки.\nСвязывайте их с выделенным текстом через Ctrl+K.")
        self.catalog_hint.setObjectName("muted")
        self.catalog_hint.setWordWrap(True)
        catalog_layout.addWidget(self.catalog_hint)
        new_object = QPushButton("+  Новый объект")
        new_object.clicked.connect(lambda: self.create_object())
        catalog_layout.addWidget(new_object)
        self.object_panel = ObjectPanel()
        self.inspiration_panel = InspirationPanel()
        self.inspiration_panel.load_path(self.resolve_image(self.db.setting("inspiration_image")))
        self.right_stack.addWidget(self.catalog_page)
        self.right_stack.addWidget(self.object_panel)
        self.right_stack.addWidget(self.inspiration_panel)
        self.workspace_splitter.addWidget(self.right_panel)
        self.workspace_splitter.setStretchFactor(0, 0)
        self.workspace_splitter.setStretchFactor(1, 1)
        self.workspace_splitter.setStretchFactor(2, 0)
        self.workspace_splitter.setSizes([260, 830, 340])
        self.workspace_page = self.takeCentralWidget()
        self.app_stack = QStackedWidget()
        self.setCentralWidget(self.app_stack)
        self.app_stack.addWidget(self.workspace_page)
        self.library_page = LibraryPage()
        self.app_stack.addWidget(self.library_page)
        self.library_page.open_requested.connect(self.open_book)
        self.library_page.create_requested.connect(self.create_book)
        self.library_page.return_requested.connect(self.return_to_book)

    def connect_signals(self):
        self.chapter_panel.chapter_selected.connect(self.open_chapter)
        self.chapter_panel.create_requested.connect(self.create_chapter)
        self.chapter_panel.part_requested.connect(self.create_part)
        self.chapter_panel.rename_requested.connect(self.rename_node)
        self.chapter_panel.delete_requested.connect(self.delete_node)
        self.chapter_panel.move_requested.connect(self.move_chapter)
        self.chapter_panel.structure_changed.connect(self.reorder_book)
        self.chapter_panel.category_selected.connect(self.select_category)
        self.editor.textChanged.connect(self.schedule_save)
        self.editor.link_requested.connect(self.create_link)
        self.editor.link_clicked.connect(self.open_linked_item)
        self.editor_toolbar.link_requested.connect(self.request_link)
        self.editor_toolbar.font_requested.connect(self.choose_font)
        self.object_panel.changed.connect(self.schedule_object_save)
        self.object_panel.image_requested.connect(self.choose_object_image)
        self.object_panel.image_removed.connect(self.remove_object_image)
        self.object_panel.chapter_requested.connect(self.open_chapter)
        self.inspiration_panel.image_chosen.connect(self.save_inspiration)
        self.inspiration_panel.image_paste_requested.connect(lambda: self.paste_image(True))
        self.object_panel.image_paste_requested.connect(lambda: self.paste_image(False))


    def reload_tree(self):
        self.chapters = {row["id"]: dict(row) for row in self.db.get_chapters()}
        self.chapter_panel.populate(list(self.chapters.values()), [dict(p) for p in self.db.get_parts()], self.current_chapter_id, self.db.get_root_order())
        self.update_summary()

    def update_summary(self):
        words = sum(len(ch["text"].split()) for ch in self.chapters.values())
        chapter_words = 0
        if self.current_chapter_id in self.chapters:
            chapter_words = len(self.editor.toPlainText().split())
            words += chapter_words - len(self.chapters[self.current_chapter_id]["text"].split())
        self.chapter_panel.update_summary(self.db.setting("book_title", "Моя книга"), words, chapter_words)

    def create_chapter(self, part_id=""):
        if self.app_stack.currentWidget() is self.library_page:
            self.create_book()
            return
        title, ok = QInputDialog.getText(self, "Новая глава", "Название главы:")
        if not ok or not title.strip() or not self.save_current_chapter():
            return
        identifier = str(uuid.uuid4())
        self.db.create_chapter(identifier, title.strip(), part_id=part_id)
        self.reload_tree()
        self.open_chapter(identifier)
        self.editor.setFocus()

    def create_part(self):
        title, ok = QInputDialog.getText(self, "Новая часть", "Название части:")
        if ok and title.strip() and self.save_current_chapter():
            self.db.create_part(str(uuid.uuid4()), title.strip())
            self.reload_tree()

    def open_chapter(self, chapter_id):
        if not self.save_current_chapter() or chapter_id not in self.chapters:
            return
        chapter = self.chapters[chapter_id]
        self.current_chapter_id = chapter_id
        self.editor.blockSignals(True)
        self.editor.setEnabled(True)
        self.apply_book_font()
        self.editor.setPlaceholderText("Начните писать…")
        if chapter["content_html"]:
            self.editor.setHtml(chapter["content_html"])
        else:
            self.editor.setPlainText(chapter["text"])
        self.editor.blockSignals(False)
        self.chapter_dirty = False
        self.editor.document().setModified(False)
        self.editor_toolbar.setEnabled(True)
        self.editor_toolbar.refresh()
        match = re.match(r"^(Глава\s+[\dIVXLCDM]+)[. :—-]+(.+)$", chapter["title"], re.IGNORECASE)
        self.page_kicker.setText(match.group(1).upper() if match else "РУКОПИСЬ")
        self.page_title.setText(match.group(2) if match else chapter["title"])
        part = next((p["title"] for p in self.db.get_parts() if p["id"] == chapter["part_id"]), "")
        breadcrumb = "  /  ".join(filter(None, ["Книга", part, chapter["title"]]))
        self.chapter_title_label.setText(breadcrumb)
        self.chapter_title_label.setToolTip(breadcrumb)
        self.chapter_panel.tree.blockSignals(True)
        self.chapter_panel.tree.setCurrentItem(self.chapter_panel.chapter_nodes[chapter_id])
        self.chapter_panel.tree.blockSignals(False)
        self.db.set_setting("last_chapter", chapter_id)
        self.update_summary()

    def set_empty_editor(self):
        self.current_chapter_id = None
        self.editor.blockSignals(True)
        self.editor.clear()
        self.editor.setEnabled(False)
        self.editor.blockSignals(False)
        self.editor_toolbar.setEnabled(False)
        self.editor_toolbar.refresh()
        self.page_kicker.setText("НОВАЯ СТРАНИЦА")
        self.page_title.setText("Начните свою историю")
        self.editor.setPlaceholderText("Нажмите «Новая глава» слева\nили используйте Ctrl+N.")
        self.chapter_title_label.setText("Создайте первую главу")
        self.chapter_dirty = False

    def schedule_save(self):
        if self.current_chapter_id:
            self.chapter_dirty = True
            self.statusBar().showMessage("Сохранение…")
            self.save_timer.start()
            self.update_summary()

    def save_current_chapter(self):
        self.save_timer.stop()
        if not self.chapter_dirty or self.current_chapter_id not in self.chapters:
            return True
        text, html = self.editor.toPlainText(), self.editor.toHtml()
        try:
            self.db.update_chapter_content(self.current_chapter_id, text, html)
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Не удалось сохранить главу", str(error))
            return False
        self.chapters[self.current_chapter_id].update(text=text, content_html=html)
        self.chapter_dirty = False
        self.editor.document().setModified(False)
        self.statusBar().showMessage("Все изменения сохранены", 3000)
        self.update_links()
        return True

    def rename_node(self, kind, identifier):
        source = self.chapters.get(identifier) if kind == "chapter" else next((dict(p) for p in self.db.get_parts() if p["id"] == identifier), None)
        if not source:
            return
        title, ok = QInputDialog.getText(self, "Переименовать", "Название:", text=source["title"])
        if ok and title.strip() and self.save_current_chapter():
            (self.db.rename_chapter if kind == "chapter" else self.db.rename_part)(identifier, title.strip())
            self.reload_tree()
            if self.current_chapter_id:
                self.open_chapter(self.current_chapter_id)

    def delete_node(self, kind, identifier):
        message = "Удалить главу вместе с её текстом?" if kind == "chapter" else "Удалить часть? Главы останутся в книге без части."
        if QMessageBox.question(self, "Удаление", message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        if not self.save_current_chapter():
            return
        (self.db.delete_chapter if kind == "chapter" else self.db.delete_part)(identifier)
        if kind == "chapter" and self.current_chapter_id == identifier:
            self.set_empty_editor()
        self.reload_tree()
        if self.current_chapter_id:
            self.open_chapter(self.current_chapter_id)
        elif self.chapters:
            self.open_chapter(next(iter(self.chapters)))
        self.update_links()

    def move_chapter(self, identifier, part_id):
        if self.save_current_chapter():
            self.db.move_chapter(identifier, part_id)
            self.reload_tree()
            if self.current_chapter_id:
                self.open_chapter(self.current_chapter_id)

    def select_category(self, category):
        if not category:
            self.editor.setFocus()
            return
        self.category = category
        self.show_catalog()

    def show_catalog(self):
        if not self.save_current_object():
            return
        self.right_stack.setCurrentWidget(self.catalog_page)
        self.refresh_catalog()

    def refresh_catalog(self, *args):
        self.object_list.clear()
        query = self.object_search.text().casefold()
        items = self.db.get_items(None if self.category == "all" else self.category)
        for item in items:
            if query not in (item["name"] + " " + item["tags"]).casefold():
                continue
            row = QListWidgetItem(item["name"] + "\n" + TYPES.get(item["item_type"], item["item_type"]))
            row.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.object_list.addItem(row)
        self.catalog_title.setText({"all": "МИР ВАШЕЙ КНИГИ", "character": "ПЕРСОНАЖИ", "location": "ЛОКАЦИИ", "note": "ЗАМЕТКИ"}[self.category])
        self.catalog_hint.setVisible(self.object_list.count() == 0)

    def create_object(self, default_name=""):
        labels = list(TYPES.values())
        default_index = list(TYPES).index(self.category) if self.category in TYPES else 0
        label, ok = QInputDialog.getItem(self, "Новый объект", "Тип:", labels, default_index, False)
        if not ok:
            return None
        name, ok = QInputDialog.getText(self, "Новый объект", "Название:", text=default_name)
        if not ok or not name.strip():
            return None
        identifier = str(uuid.uuid4())
        self.db.create_linked_item(identifier, name.strip(), list(TYPES)[labels.index(label)])
        self.refresh_catalog()
        self.open_linked_item(identifier)
        return identifier

    def request_link(self):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            self.statusBar().showMessage("Сначала выделите слово или фразу для ссылки.", 5000)
            return
        self.editor.pending_link_cursor = cursor
        self.create_link(cursor.selectedText())

    def create_link(self, selected_text):
        if not self.current_chapter_id:
            return
        items = self.db.get_items()
        options = ["+ Создать новый объект"] + [f"{item['name']} · {TYPES.get(item['item_type'], '')} [{i+1}]" for i, item in enumerate(items)]
        try:
            choice, ok = QInputDialog.getItem(self, "Ссылка на объект", "Выберите объект:", options, 0, False)
            if not ok:
                return
            index = options.index(choice)
            identifier = self.create_object(selected_text) if index == 0 else items[index-1]["id"]
            if identifier:
                item = self.db.get_linked_item(identifier)
                self.editor.apply_internal_link(identifier, item["name"], TYPES.get(item["item_type"], "Объект"))
                self.open_linked_item(identifier)
        finally:
            self.editor.pending_link_cursor = None

    def open_linked_item(self, item_id):
        # Save before reading, including when reopening the same card.
        if not self.save_current_object():
            return
        item = self.db.get_linked_item(item_id)
        if item is None:
            return
        self.current_linked_item_id = item_id
        card = dict(item)
        card["image_path"] = self.resolve_image(card["image_path"])
        self.object_panel.show_item(card)
        self.right_stack.setCurrentWidget(self.object_panel)
        self.db.set_setting("last_object", item_id)
        self.update_links()

    def schedule_object_save(self):
        if self.current_linked_item_id:
            self.object_dirty = True
            self.object_save_timer.start()
            self.statusBar().showMessage("Сохранение объекта…")

    def save_current_object(self):
        self.object_save_timer.stop()
        if not self.object_dirty or not self.current_linked_item_id:
            return True
        values = self.object_panel.values()
        if values["image_path"]:
            try:
                values["image_path"] = str(Path(values["image_path"]).resolve().relative_to(self.db.path.parent.resolve()))
            except ValueError:
                pass
        if not values["name"]:
            old = self.db.get_linked_item(self.current_linked_item_id)
            values["name"] = old["name"]
        try:
            self.db.update_item(self.current_linked_item_id, values)
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Не удалось сохранить объект", str(error))
            return False
        self.object_dirty = False
        self.statusBar().showMessage("Все изменения сохранены", 3000)
        self.refresh_catalog()
        return True

    def update_links(self):
        identifier = self.current_linked_item_id
        if identifier:
            self.object_panel.set_links([c for c in self.chapters.values() if f"book://{identifier}" in c["content_html"]])


    def resolve_image(self, path):
        if not path:
            return ""
        image_path = Path(path)
        return str(image_path if image_path.is_absolute() else self.db.path.parent / image_path)

    def store_image(self, source):
        destination_dir = self.db.path.parent / "data" / "images"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / (uuid.uuid4().hex + Path(source).suffix.lower())
        shutil.copy2(source, destination)
        return str(destination.relative_to(self.db.path.parent))

    def paste_image(self, inspiration=False):
        if not inspiration and not self.current_linked_item_id:
            return
        image = clipboard_image()
        if image.isNull():
            QMessageBox.information(self, "Изображение", "В буфере обмена нет изображения.")
            return
        destination = self.db.path.parent / "data" / "images" / (uuid.uuid4().hex + ".png")
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not image.save(str(destination), "PNG"):
                raise OSError("Не удалось сохранить изображение.")
            stored = str(destination.relative_to(self.db.path.parent))
            if inspiration:
                self.db.set_setting("inspiration_image", stored)
                self.inspiration_panel.load_path(str(destination))
            else:
                self.object_panel.set_image(str(destination))
                self.schedule_object_save()
                self.save_current_object()
        except (OSError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Изображение", str(error))

    def choose_object_image(self):
        source, _ = QFileDialog.getOpenFileName(self, "Изображение объекта", "", "Изображения (*.png *.jpg *.jpeg *.webp *.bmp)")
        if source:
            if QPixmap(source).isNull():
                QMessageBox.warning(self, "Изображение", "Не удалось прочитать изображение.")
                return
            try:
                path = self.store_image(source)
            except OSError as error:
                QMessageBox.warning(self, "Изображение", str(error))
                return
            self.object_panel.set_image(self.resolve_image(path))
            self.schedule_object_save()

    def remove_object_image(self):
        self.object_panel.set_image("")
        self.schedule_object_save()

    def save_inspiration(self, path):
        try:
            stored = self.store_image(path) if path else ""
            self.db.set_setting("inspiration_image", stored)
            self.inspiration_panel.load_path(self.resolve_image(stored))
        except (OSError, sqlite3.Error) as error:
            QMessageBox.warning(self, "Изображение", str(error))

    def toggle_inspiration_panel(self):
        if self.app_stack.currentWidget() is self.library_page:
            return
        if not self.save_current_object():
            return
        if self.right_stack.currentWidget() is self.inspiration_panel:
            self.right_stack.setCurrentWidget(self.object_panel if self.current_linked_item_id else self.catalog_page)
        else:
            self.right_stack.setCurrentWidget(self.inspiration_panel)

    def edit_book(self):
        title, ok = QInputDialog.getText(self, "Книга", "Название книги:", text=self.db.setting("book_title", "Моя книга"))
        if not ok or not title.strip():
            return
        self.db.set_setting("book_title", title.strip())
        self.book_title.setText(title.strip())
        self.update_summary()

    def toggle_focus(self):
        if self.app_stack.currentWidget() is self.library_page:
            return
        self.focus_mode = not self.focus_mode
        self.chapter_panel.setVisible(not self.focus_mode)
        self.right_panel.setVisible(not self.focus_mode)
        self.editor.setFocus()

    def show_search(self):
        if self.app_stack.currentWidget() is self.library_page:
            self.library_page.search.setFocus()
            return
        self.search_bar.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def find_next(self):
        text = self.search_input.text()
        if not text:
            return
        original = self.editor.textCursor()
        if not self.editor.find(text):
            cursor = self.editor.textCursor()
            cursor.setPosition(0)
            self.editor.setTextCursor(cursor)
            if not self.editor.find(text):
                self.editor.setTextCursor(original)
                self.statusBar().showMessage("Совпадений не найдено", 3000)

    def show_book_menu(self):
        menu = QMenu(self)
        save = menu.addAction("Сохранить · Ctrl+S")
        export = menu.addAction("Экспорт книги…")
        menu.addSeparator()
        inspiration = menu.addAction("Вдохновение · Ctrl+Shift+I")
        selected = menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))
        if selected == save:
            self.save_all()
        elif selected == export:
            self.export_book()
        elif selected == inspiration:
            self.toggle_inspiration_panel()

    def ordered_chapters(self):
        chapters = list(self.chapters.values())
        ordered = []
        for kind, identifier in self.db.get_root_order():
            if kind == "part":
                ordered.extend(c for c in chapters if c["part_id"] == identifier)
            elif identifier in self.chapters:
                ordered.append(self.chapters[identifier])
        return ordered

    def reorder_book(self, roots):
        if not self.save_current_chapter():
            self.reload_tree()
            return
        try:
            self.db.reorder_tree(roots)
        except (sqlite3.Error, ValueError) as error:
            QMessageBox.warning(self, "Не удалось изменить порядок", str(error))
            self.reload_tree()
            return
        self.reload_tree()
        if self.current_chapter_id in self.chapters:
            chapter = self.chapters[self.current_chapter_id]
            part = next((p["title"] for p in self.db.get_parts() if p["id"] == chapter["part_id"]), "")
            breadcrumb = "  /  ".join(filter(None, ["Книга", part, chapter["title"]]))
            self.chapter_title_label.setText(breadcrumb)
            self.chapter_title_label.setToolTip(breadcrumb)
        self.statusBar().showMessage("Порядок глав и частей сохранён", 3000)

    def export_book(self):
        if not self.save_all():
            return
        path, selected_filter = QFileDialog.getSaveFileName(self, "Экспорт книги", "Моя книга.html", "HTML (*.html);;Текст (*.txt)")
        if not path:
            return
        if not Path(path).suffix:
            path += ".txt" if selected_filter.startswith("Текст") else ".html"
        title = self.db.setting("book_title", "Моя книга")
        parts = {p["id"]: p["title"] for p in self.db.get_parts()}
        previous_part = None
        plain = Path(path).suffix.lower() == ".txt"
        pieces = [title] if plain else [f"<h1>{escape(title)}</h1>"]
        for chapter in self.ordered_chapters():
            if chapter["part_id"] != previous_part and chapter["part_id"] in parts:
                part_title = parts[chapter["part_id"]]
                pieces.append(part_title if plain else f"<h1>{escape(part_title)}</h1>")
            previous_part = chapter["part_id"]
            if plain:
                pieces.extend([chapter["title"], chapter["text"]])
            else:
                html = chapter["content_html"]
                if not html:
                    doc = QTextDocument()
                    doc.setPlainText(chapter["text"])
                    html = doc.toHtml()
                match = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
                body = match.group(1) if match else escape(chapter["text"])
                pieces.append(f"<h2>{escape(chapter['title'])}</h2>{body}")
        output = "\n\n".join(pieces)
        if not plain:
            output = '<!doctype html><html lang="ru"><meta charset="utf-8"><title>' + escape(title) + '</title><style>body{max-width:760px;margin:60px auto;padding:0 24px;font:18px/1.6 Georgia,serif}h1,h2{text-align:center}p{white-space:pre-wrap}</style><body>' + output + '</body></html>'
        try:
            Path(path).write_text(output, encoding="utf-8")
            self.statusBar().showMessage("Книга экспортирована: " + path, 6000)
        except OSError as error:
            QMessageBox.warning(self, "Экспорт", str(error))

    def save_all(self):
        if self._closed:
            return True
        self.chapter_panel.tree.flush_structure()
        first = self.save_current_chapter()
        second = self.save_current_object()
        return first and second

    def closeEvent(self, event):
        if self._closed:
            event.accept()
            return
        if not self.save_all():
            event.ignore()
            return
        try:
            self.db.set_setting("geometry", bytes(self.saveGeometry().toBase64()).decode())
            if not self.focus_mode:
                self.db.set_setting("splitter", json.dumps(self.workspace_splitter.sizes()))
        except sqlite3.Error as error:
            QMessageBox.critical(self, "Не удалось сохранить настройки", str(error))
            event.ignore()
            return
        self.chapter_panel.tree.commit_timer.stop()
        self.db.close()
        self._closed = True
        event.accept()


    def show_library(self):
        if not self.save_all():
            return
        self.library_page.set_books(self.library.books(), str(self.db.path.resolve()))
        self.app_stack.setCurrentWidget(self.library_page)
        self.statusBar().showMessage("Библиотека · все ваши рукописи")

    def return_to_book(self):
        self.app_stack.setCurrentWidget(self.workspace_page)
        self.statusBar().showMessage("Все изменения сохранены", 2500)

    def create_book(self):
        title, ok = QInputDialog.getText(self, "Новая книга", "Название книги:")
        if not ok or not title.strip() or not self.save_all():
            return
        try:
            path = self.library.create_book(title.strip())
        except (OSError, sqlite3.Error) as error:
            QMessageBox.critical(self, "Не удалось создать книгу", str(error))
            return
        self.open_book(str(path))

    def open_book(self, path):
        if not self.save_all():
            return False
        path = Path(path).resolve()
        if path == self.db.path.resolve():
            self.return_to_book()
            return True
        if not path.is_file():
            QMessageBox.warning(self, "Книга недоступна", "Файл книги не найден.")
            return False
        next_db = None
        try:
            next_db = Database(path)
            next_db.get_chapters()
        except (OSError, sqlite3.Error) as error:
            if next_db is not None:
                next_db.close()
            QMessageBox.critical(self, "Не удалось открыть книгу", str(error))
            return False
        self.save_timer.stop()
        self.object_save_timer.stop()
        self.db.close()
        self.db = next_db
        self.current_chapter_id = None
        self.current_linked_item_id = None
        self.chapter_dirty = self.object_dirty = False
        self.category = "all"
        self.search_bar.hide()
        self.search_input.clear()
        self.object_search.clear()
        self.object_panel.tabs.setCurrentIndex(0)
        self.object_panel.set_links([])
        self.right_stack.setCurrentWidget(self.catalog_page)
        self.inspiration_panel.load_path(self.resolve_image(self.db.setting("inspiration_image")))
        self.book_title.setText(self.db.setting("book_title", "Моя книга"))
        self.setWindowTitle(self.db.setting("book_title", "Моя книга") + " — Book Note")
        self.apply_book_font()
        self.reload_tree()
        last = self.db.setting("last_chapter")
        if last not in self.chapters:
            last = next(iter(self.chapters), None)
        if last:
            self.open_chapter(last)
        else:
            self.set_empty_editor()
        self.refresh_catalog()
        last_object = self.db.setting("last_object")
        if last_object and self.db.get_linked_item(last_object):
            self.open_linked_item(last_object)
        self.chapter_panel.select_category("")
        self.library.mark_opened(path)
        self.return_to_book()
        return True

    def apply_book_font(self):
        font = QFont(self.db.setting("editor_font", "Georgia"), int(self.db.setting("editor_font_size", "15")))
        self.editor.setFont(font)
        self.editor.document().setDefaultFont(font)
        family = json.dumps(font.family(), ensure_ascii=False)
        self.editor.setStyleSheet(f"QTextEdit#bookEditor {{ font-family: {family}; font-size: {font.pointSize()}pt; }}")

    def choose_font(self):
        dialog = FontDialog(self.editor.currentFont(), self.editor.textCursor().hasSelection(), self)
        if dialog.exec():
            self.apply_editor_font(dialog.chosen_font())

    def apply_editor_font(self, font):
        if not self.current_chapter_id:
            return
        cursor = self.editor.textCursor()
        selected = cursor.hasSelection()
        original = QTextCursor(cursor)
        fmt = QTextCharFormat()
        fmt.setFontFamilies([font.family()])
        fmt.setFontPointSize(font.pointSizeF())
        cursor.beginEditBlock()
        if not selected:
            cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(fmt)
        cursor.endEditBlock()
        self.editor.setTextCursor(original)
        if not selected:
            self.db.set_setting("editor_font", font.family())
            self.db.set_setting("editor_font_size", round(font.pointSizeF()))
            self.apply_book_font()
            self.editor.mergeCurrentCharFormat(fmt)
        self.editor_toolbar.refresh()
        self.editor.setFocus()

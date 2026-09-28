from PySide6.QtCore import Qt, Signal
from ui.clipboard_image import enable_image_paste
from ui.aspect_image import AspectImage
from ui.tag_edit import TagEdit
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QSizePolicy, QFormLayout, QTabWidget, QScrollArea, QListWidget, QListWidgetItem, QHBoxLayout,
)


class ObjectPanel(QWidget):
    changed = Signal()
    image_requested = Signal()
    image_removed = Signal()
    chapter_requested = Signal(str)

    image_paste_requested = Signal()

    def __init__(self):
        super().__init__()
        self.loading = False
        self.image_path = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(8, 14, 8, 12)
        body_layout.setSpacing(14)
        self.image_label = AspectImage()
        body_layout.addWidget(self.image_label)
        self.paste_shortcut = enable_image_paste(self.image_label, self.image_paste_requested.emit)
        paste = QPushButton("Вставить из буфера")
        paste.setObjectName("quietButton")
        paste.clicked.connect(self.image_paste_requested.emit)
        body_layout.addWidget(paste)
        image_buttons = QHBoxLayout()
        choose = QPushButton("Изменить изображение")
        choose.setObjectName("quietButton")
        choose.clicked.connect(self.image_requested.emit)
        remove = QPushButton("×")
        remove.setToolTip("Убрать изображение")
        remove.clicked.connect(self.image_removed.emit)
        image_buttons.addWidget(choose, 1)
        image_buttons.addWidget(remove)
        body_layout.addLayout(image_buttons)
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(0)
        self.name_edit.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.name_edit.setObjectName("objectName")
        self.name_edit.setPlaceholderText("Название объекта")
        body_layout.addWidget(self.name_edit)
        self.type_label = QLabel()
        self.type_label.setObjectName("muted")
        body_layout.addWidget(self.type_label)
        self.quote_edit = QTextEdit()
        self.quote_edit.setPlaceholderText("Короткая цитата или настроение…")
        self.quote_edit.setFixedHeight(80)
        self.quote_edit.setObjectName("quoteEditor")
        body_layout.addWidget(self.quote_edit)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.fields = {}
        for key, title, placeholder in [
            ("country", "Страна", "Например, Великобритания"),
            ("period", "Период", "Например, XIX век"),
            ("tags", "Теги", "Город, туман, вдохновение"),
        ]:
            field = TagEdit() if key == "tags" else QLineEdit()
            field.setMinimumWidth(0)
            field.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            field.setPlaceholderText(placeholder)
            form.addRow(title, field)
            self.fields[key] = field
            field.textChanged.connect(self.notify)
        body_layout.addLayout(form)
        body_layout.addWidget(QLabel("Описание"))
        self.description_editor = QTextEdit()
        self.description_editor.setPlaceholderText("Что важно знать об этом объекте?")
        self.description_editor.setMinimumHeight(140)
        body_layout.addWidget(self.description_editor)
        body_layout.addStretch()
        scroll.setWidget(body)
        self.tabs.addTab(scroll, "Объект")
        self.notes_editor = QTextEdit()
        self.notes_editor.setPlaceholderText("Идеи, детали и заметки об объекте…")
        self.tabs.addTab(self.notes_editor, "Заметки")
        links_page = QWidget()
        links_layout = QVBoxLayout(links_page)
        label = QLabel("Главы, в которых есть ссылка на этот объект")
        label.setWordWrap(True)
        label.setObjectName("muted")
        links_layout.addWidget(label)
        self.links = QListWidget()
        self.links.itemClicked.connect(lambda item: self.chapter_requested.emit(item.data(Qt.ItemDataRole.UserRole)))
        links_layout.addWidget(self.links)
        self.tabs.addTab(links_page, "Связи")
        for widget in (self.name_edit, self.quote_edit, self.description_editor, self.notes_editor):
            widget.textChanged.connect(self.notify)

    def notify(self, *args):
        if not self.loading:
            self.changed.emit()

    def show_item(self, item):
        self.loading = True
        self.name_edit.setText(item["name"])
        self.type_label.setText({"character": "Персонаж", "location": "Локация", "note": "Заметка"}.get(item["item_type"], item["item_type"]))
        self.description_editor.setPlainText(item["description"])
        self.quote_edit.setPlainText(item["quote"])
        self.notes_editor.setPlainText(item["notes"])
        for key, field in self.fields.items():
            field.setText(item[key])
        self.set_image(item["image_path"])
        self.loading = False

    def values(self):
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_editor.toPlainText(),
            "notes": self.notes_editor.toPlainText(),
            "quote": self.quote_edit.toPlainText(),
            "image_path": self.image_path,
            **{key: field.text() for key, field in self.fields.items()},
        }

    def set_image(self, path):
        self.image_path = path
        self.image_label.set_image(path)

    def set_links(self, chapters):
        self.links.clear()
        for chapter in chapters:
            row = QListWidgetItem(chapter["title"])
            row.setData(Qt.ItemDataRole.UserRole, chapter["id"])
            self.links.addItem(row)

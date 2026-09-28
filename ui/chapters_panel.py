from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMenu, QProgressBar,
)

from ui.icons import make_icon
from ui.book_tree import BookTree

ROLE = Qt.ItemDataRole.UserRole


class ChapterPanel(QWidget):
    chapter_selected = Signal(str)
    create_requested = Signal(str)
    part_requested = Signal()
    rename_requested = Signal(str, str)
    delete_requested = Signal(str, str)
    move_requested = Signal(str, str)
    category_selected = Signal(str)
    structure_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("chapterPanel")
        self.setMinimumWidth(220)
        self.setMaximumWidth(380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(5)
        self.nav_buttons = []
        for symbol, title, category in [
            ("home", "Рукопись", ""),
            ("all", "Все объекты", "all"),
            ("character", "Персонажи", "character"),
            ("location", "Локации", "location"),
            ("note", "Заметки", "note"),
        ]:
            button = QPushButton("   " + title)
            button.setIcon(make_icon(symbol))
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, c=category: self.select_category(c))
            self.nav_buttons.append((category, button))
            layout.addWidget(button)
        self.nav_buttons[0][1].setChecked(True)
        layout.addSpacing(20)
        heading = QHBoxLayout()
        label = QLabel("СТРУКТУРА КНИГИ")
        label.setObjectName("eyebrow")
        heading.addWidget(label)
        heading.addStretch()
        add_part = QPushButton("+")
        add_part.setObjectName("smallButton")
        add_part.setToolTip("Добавить часть книги")
        add_part.clicked.connect(self.part_requested.emit)
        heading.addWidget(add_part)
        layout.addLayout(heading)
        self.tree = BookTree()
        self.tree.structure_changed.connect(self.structure_changed.emit)
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu)
        self.tree.currentItemChanged.connect(self.on_selection)
        layout.addWidget(self.tree, 1)
        create = QPushButton("+    Новая глава")
        create.setObjectName("navButton")
        create.clicked.connect(lambda: self.create_requested.emit(self.selected_part()))
        layout.addWidget(create)
        layout.addSpacing(12)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.summary.setObjectName("bookSummary")
        layout.addWidget(self.summary)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        layout.addWidget(self.progress)
        self.parts = []
        self.chapter_nodes = {}

    def select_category(self, category):
        for key, button in self.nav_buttons:
            button.setChecked(key == category)
        self.category_selected.emit(category)

    def selected_part(self):
        node = self.tree.currentItem()
        if not node:
            return ""
        kind, identifier = node.data(0, ROLE)
        if kind == "part":
            return identifier
        return node.parent().data(0, ROLE)[1] if node.parent() else ""

    def populate(self, chapters, parts, selected=None, root_order=None):
        expanded = {self.tree.topLevelItem(i).data(0, ROLE)[1]: self.tree.topLevelItem(i).isExpanded()
                    for i in range(self.tree.topLevelItemCount())}
        self.tree.blockSignals(True)
        self.tree.clear()
        self.parts = parts
        parents = {}
        for part in parts:
            node = QTreeWidgetItem([part["title"]])
            node.setData(0, ROLE, ("part", part["id"]))
            self.tree.addTopLevelItem(node)
            node.setExpanded(expanded.get(part["id"], True))
            parents[part["id"]] = node
        self.chapter_nodes = {}
        for chapter in chapters:
            node = QTreeWidgetItem([chapter["title"]])
            node.setFlags(node.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            node.setIcon(0, make_icon("note"))
            node.setToolTip(0, chapter["title"])
            node.setData(0, ROLE, ("chapter", chapter["id"]))
            parent = parents.get(chapter["part_id"])
            if parent:
                parent.addChild(node)
            else:
                self.tree.addTopLevelItem(node)
            self.chapter_nodes[chapter["id"]] = node
        if root_order:
            nodes = []
            while self.tree.topLevelItemCount():
                nodes.append(self.tree.takeTopLevelItem(0))
            by_key = {node.data(0, ROLE): node for node in nodes}
            ordered = []
            for key in root_order:
                node = by_key.pop(tuple(key), None)
                if node is not None:
                    ordered.append(node)
            ordered.extend(by_key.values())
            for node in ordered:
                self.tree.addTopLevelItem(node)
                if node.data(0, ROLE)[0] == "part":
                    node.setExpanded(expanded.get(node.data(0, ROLE)[1], True))
        if selected in self.chapter_nodes:
            self.tree.setCurrentItem(self.chapter_nodes[selected])
        self.tree.blockSignals(False)

    def on_selection(self, current, previous):
        if current:
            kind, identifier = current.data(0, ROLE)
            if kind == "chapter":
                self.chapter_selected.emit(identifier)

    def context_menu(self, position):
        node = self.tree.itemAt(position)
        menu = QMenu(self)
        add = menu.addAction("Новая глава")
        add_part = menu.addAction("Новая часть")
        actions = {}
        if node:
            kind, identifier = node.data(0, ROLE)
            menu.addSeparator()
            actions[menu.addAction("Переименовать")] = ("rename", kind, identifier)
            actions[menu.addAction("Удалить")] = ("delete", kind, identifier)
            if kind == "chapter":
                move = menu.addMenu("Переместить в часть")
                actions[move.addAction("Без части")] = ("move", identifier, "")
                for part in self.parts:
                    actions[move.addAction(part["title"])] = ("move", identifier, part["id"])
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        if action == add:
            part_id = ""
            if node:
                kind, identifier = node.data(0, ROLE)
                part_id = identifier if kind == "part" else (node.parent().data(0, ROLE)[1] if node.parent() else "")
            self.create_requested.emit(part_id)
        elif action == add_part:
            self.part_requested.emit()
        elif action in actions:
            operation, first, second = actions[action]
            {"rename": self.rename_requested, "delete": self.delete_requested, "move": self.move_requested}[operation].emit(first, second)

    def update_summary(self, title, words, chapter_words):
        fraction = chapter_words / words if words else 0
        text = f"{title}\nВ книге: {words:,} слов\nГлава: {chapter_words:,} слов · {fraction:.0%}"
        self.summary.setText(text.replace(",", " "))
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.progress.setRange(0, 1000)
        self.progress.setValue(round(fraction * 1000))
        self.progress.setToolTip(f"Доля текущей главы: {fraction:.1%} от всех слов книги")

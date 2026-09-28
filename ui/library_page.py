from PySide6.QtCore import Qt, Signal, QRectF, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QProgressBar, QSizePolicy,
)
from ui.icons import make_icon


class BookCover(QWidget):
    def __init__(self, title, index):
        super().__init__()
        self.title = title
        self.index = index
        self.setFixedHeight(220)
        self.setMinimumWidth(180)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(12, 5, self.width()-24, self.height()-14)
        tones = [("#443424", "#211d18"), ("#354139", "#18241f"), ("#3e3542", "#211b26"), ("#35414a", "#19212b")]
        a, b = tones[self.index % len(tones)]
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor(a))
        gradient.setColorAt(1, QColor(b))
        painter.setPen(QPen(QColor("#665039"), 1))
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, 5, 5)
        painter.setPen(QPen(QColor("#917044"), 1))
        painter.drawRoundedRect(rect.adjusted(18, 18, -14, -18), 2, 2)
        painter.drawLine(int(rect.left()+9), int(rect.top()+3), int(rect.left()+9), int(rect.bottom()-3))
        painter.setPen(QColor("#c4a578"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(rect.adjusted(26, 30, -22, -130), Qt.AlignmentFlag.AlignHCenter, "М А С Т Е Р С К А Я")
        painter.setPen(QColor("#eee0c8"))
        painter.setFont(QFont("Georgia", 17))
        painter.drawText(rect.adjusted(28, 64, -24, -40), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self.title)
        painter.setPen(QColor("#b68b52"))
        y = int(rect.bottom()-33)
        x = int(rect.center().x())
        painter.drawLine(x-30, y, x-8, y)
        painter.drawEllipse(QRectF(x-2, y-2, 4, 4))
        painter.drawLine(x+8, y, x+30, y)
        painter.end()


class LibraryPage(QWidget):
    open_requested = Signal(str)
    create_requested = Signal()
    return_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("libraryPage")
        self.records = []
        self.cards = []
        self.columns = 0
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 26, 44, 28)
        top = QHBoxLayout()
        brand = QLabel("BOOK NOTE  /  ЛИЧНАЯ БИБЛИОТЕКА")
        brand.setObjectName("eyebrow")
        top.addWidget(brand)
        top.addStretch()
        back = QPushButton("Вернуться к рукописи")
        back.clicked.connect(self.return_requested.emit)
        top.addWidget(back)
        root.addLayout(top)
        root.addSpacing(24)
        title = QLabel("Ваши истории")
        title.setObjectName("libraryTitle")
        root.addWidget(title)
        subtitle = QLabel("У каждой книги — свой мир. Продолжите начатое или откройте новую страницу.")
        subtitle.setObjectName("librarySubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)
        root.addSpacing(20)
        actions = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Найти книгу по названию…")
        self.search.setMaximumWidth(360)
        self.search.textChanged.connect(self.filter_cards)
        actions.addWidget(self.search)
        actions.addStretch()
        self.count_label = QLabel()
        self.count_label.setObjectName("muted")
        actions.addWidget(self.count_label)
        create = QPushButton("+  Новая книга")
        create.setObjectName("primaryButton")
        create.clicked.connect(self.create_requested.emit)
        actions.addWidget(create)
        root.addLayout(actions)
        root.addSpacing(14)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.shelf = QWidget()
        self.shelf.setObjectName("libraryShelf")
        self.grid = QGridLayout(self.shelf)
        self.grid.setContentsMargins(0, 0, 12, 16)
        self.grid.setHorizontalSpacing(24)
        self.grid.setVerticalSpacing(24)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.shelf)
        root.addWidget(self.scroll, 1)
        self.empty = QLabel("Книги с таким названием не найдены.")
        self.empty.setObjectName("muted")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.empty)
        self.empty.hide()
        self.reflow_timer = QTimer(self)
        self.reflow_timer.setSingleShot(True)
        self.reflow_timer.timeout.connect(self.reflow)

    def set_books(self, records, current_path):
        self.records = records
        self.current_path = current_path
        self.filter_cards()

    def filter_cards(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cards = []
        query = self.search.text().strip().casefold()
        for index, book in enumerate(self.records):
            if query not in book["title"].casefold():
                continue
            card = QFrame()
            card.setObjectName("bookCard")
            card.setFixedWidth(248)
            card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
            layout = QVBoxLayout(card)
            layout.setContentsMargins(14, 12, 14, 16)
            layout.setSpacing(10)
            layout.addWidget(BookCover(book["title"], index))
            state = QLabel("ОТКРЫТА СЕЙЧАС" if book["path"] == self.current_path else "РУКОПИСЬ")
            state.setObjectName("eyebrow")
            layout.addWidget(state)
            title = QLabel(book["title"])
            title.setTextFormat(Qt.TextFormat.PlainText)
            title.setWordWrap(True)
            title.setObjectName("cardTitle")
            title.setFixedHeight(52)
            layout.addWidget(title)
            stats = QLabel(f"{book['chapters']} глав · {book['words']:,} слов".replace(",", " "))
            stats.setObjectName("muted")
            layout.addWidget(stats)
            progress = QProgressBar()
            progress.setFixedHeight(4)
            progress.setTextVisible(False)
            progress.setRange(0, book["target"])
            progress.setValue(min(book["words"], book["target"]))
            layout.addWidget(progress)
            button = QPushButton("Продолжить писать" if book["available"] else "Файл недоступен")
            button.setEnabled(book["available"])
            button.setIcon(make_icon("note"))
            button.clicked.connect(lambda checked=False, path=book["path"]: self.open_requested.emit(path))
            layout.addWidget(button)
            self.cards.append(card)
        self.count_label.setText(f"Книг: {len(self.records)}")
        self.empty.setVisible(not self.cards)
        self.columns = 0
        self.reflow()

    def reflow(self):
        columns = max(1, self.scroll.viewport().width() // 272)
        if columns == self.columns:
            return
        self.columns = columns
        for index, card in enumerate(self.cards):
            self.grid.addWidget(card, index // columns, index % columns)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reflow_timer.start(0)

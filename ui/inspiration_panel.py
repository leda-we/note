from PySide6.QtCore import Qt, Signal
from ui.clipboard_image import enable_image_paste
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy


class InspirationPanel(QWidget):
    image_chosen = Signal(str)

    image_paste_requested = Signal()

    def __init__(self):
        super().__init__()
        self.original_pixmap = QPixmap()
        layout = QVBoxLayout(self)
        title = QLabel("НАСТРОЕНИЕ ИСТОРИИ")
        title.setObjectName("eyebrow")
        layout.addWidget(title)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setWordWrap(True)
        self.image_label.setMinimumSize(1, 1)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.image_label, 1)
        self.paste_shortcut = enable_image_paste(self.image_label, self.image_paste_requested.emit)
        paste = QPushButton("Вставить из буфера")
        paste.clicked.connect(self.image_paste_requested.emit)
        layout.addWidget(paste)
        choose = QPushButton("Выбрать изображение")
        choose.clicked.connect(self.choose_image)
        layout.addWidget(choose)
        remove = QPushButton("Убрать изображение")
        remove.clicked.connect(lambda: self.image_chosen.emit(""))
        layout.addWidget(remove)

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Изображение для вдохновения", "", "Изображения (*.png *.jpg *.jpeg *.webp *.bmp)")
        if path and not QPixmap(path).isNull():
            self.image_chosen.emit(path)

    def load_path(self, path):
        self.original_pixmap = QPixmap(path) if path else QPixmap()
        self.update_image()

    def update_image(self):
        if self.original_pixmap.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Добавьте изображение,\nкоторое помогает писать.")
        else:
            self.image_label.setPixmap(self.original_pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()

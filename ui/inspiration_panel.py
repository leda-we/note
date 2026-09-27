from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QMenu,
    QFileDialog,
)

class InspirationPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumWidth(280)
        self.setMaximumWidth(420)
        self.original_pixmap = None
        layout = QVBoxLayout(self)

        self.image_label = QLabel(
            "ПКМ -> выбрать изображение"
        )

        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setWordWrap(True)
        layout.addWidget(self.image_label)
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.open_context_menu)

    def open_context_menu(self, position):
        menu = QMenu(self)
        choose_action = menu.addAction("Выбрать изображение")
        remove_action = None
        if self.original_pixmap is not None:
            remove_action = menu.addAction("Убрать изображение")
        
        selected_action = menu.exec(self.image_label.mapToGlobal(position))
        if selected_action is None:
            return
        if selected_action == choose_action:
            self.choose_image()
        
        elif(remove_action is not None and selected_action == remove_action):
            self.remove_image()
        
    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")

        if not file_path:
            return

        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            return

        self.original_pixmap = pixmap
        self.update_image()

    def remove_image(self):
        self.original_pixmap = None
        self.image_label.clear()
        self.image_label.setText("ПКМ - выбрать изображение")
    def update_image(self):
        if self.original_pixmap is None:
            return

        scaled_pixmap = self.original_pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.update_image()
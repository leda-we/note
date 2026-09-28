from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class AspectImage(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)
        self.setFixedHeight(170)

    def set_image(self, path):
        self.pixmap = QPixmap(path) if path else QPixmap()
        self.update_height()
        self.update()

    def update_height(self):
        width = max(1, self.width())
        height = round(width * self.pixmap.height() / self.pixmap.width()) if not self.pixmap.isNull() else 170
        self.setFixedHeight(max(1, height))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_height()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 8, 8)
        painter.setClipPath(path)
        if self.pixmap.isNull():
            painter.fillRect(self.rect(), QColor("#27241f"))
            painter.setPen(QColor("#a89576"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Добавьте изображение\nдля этой истории")
        else:
            painter.drawPixmap(self.rect(), self.pixmap)
        painter.setClipping(False)
        painter.setPen(QPen(QColor("#514534"), 1))
        painter.drawPath(path)
        painter.end()

from PySide6.QtCore import Qt, QSize, QRectF, QTimer
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class AspectImage(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)
        self.setFixedHeight(170)
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.setInterval(16)
        self.resize_timer.timeout.connect(self.update_height)

    def set_image(self, path):
        self.resize_timer.stop()
        self.pixmap = QPixmap(path) if path else QPixmap()
        self.update_height()
        self.update()

    def update_height(self):
        width = max(1, self.width())
        height = round(width * self.pixmap.height() / self.pixmap.width()) if not self.pixmap.isNull() else 170
        height = max(1, min(16777215, height))
        if self.height() != height:
            self.setFixedHeight(height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Do not change widget geometry from inside a resize callback.
        # Coalesce splitter events and resize once the latest width has settled.
        if event.size().width() != event.oldSize().width():
            self.resize_timer.start()

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
            # Keep proportions even during the short coalescing interval.
            scale = min(self.width() / self.pixmap.width(), self.height() / self.pixmap.height())
            width, height = self.pixmap.width() * scale, self.pixmap.height() * scale
            target = QRectF((self.width()-width)/2, 0, width, height)
            painter.drawPixmap(target, self.pixmap, QRectF(self.pixmap.rect()))
        painter.setClipping(False)
        painter.setPen(QPen(QColor("#514534"), 1))
        painter.drawPath(path)
        painter.end()

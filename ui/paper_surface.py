import random
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QColor
from PySide6.QtWidgets import QFrame


class PaperSurface(QFrame):
    """Subtle paper grain is painted once into a repeatable tile."""
    def __init__(self):
        super().__init__()
        self.setObjectName("paper")
        self.grain = QPixmap(128, 128)
        self.grain.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.grain)
        rng = random.Random(17)
        for _ in range(1400):
            painter.setPen(QColor(223, 207, 178, rng.randrange(3, 11)))
            painter.drawPoint(rng.randrange(128), rng.randrange(128))
        painter.end()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setClipRect(self.rect().adjusted(4, 4, -4, -4))
        painter.drawTiledPixmap(self.rect(), self.grain)
        painter.end()

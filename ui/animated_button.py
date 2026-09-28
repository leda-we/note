from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve, Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QPushButton, QStyleOptionButton, QStyle


class LibraryButton(QPushButton):
    """Animate paint only: no layout, stylesheet, or geometry changes per frame."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._hover = 0.0
        self.animation = QPropertyAnimation(self, b"hoverAmount", self)
        self.animation.setDuration(170)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def get_hover(self):
        return self._hover

    def set_hover(self, value):
        self._hover = value
        self.update()

    hoverAmount = Property(float, get_hover, set_hover)

    def animate_to(self, value):
        self.animation.stop()
        self.animation.setStartValue(self._hover)
        self.animation.setEndValue(value)
        self.animation.start()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.animate_to(1.0)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.animate_to(0.0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        amount = self._hover
        def mix(a, b):
            a, b = QColor(a), QColor(b)
            return QColor(*(round(x+(y-x)*amount) for x,y in zip(a.getRgb()[:3], b.getRgb()[:3])))
        painter.setBrush(QColor("#30251b") if self.isDown() else mix("#211d18", "#3d3020"))
        painter.setPen(QPen(mix("#4a3b28", "#bd9559"), 1))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.5,0.5,-0.5,-0.5), 7, 7)
        option = QStyleOptionButton()
        self.initStyleOption(option)
        self.style().drawControl(QStyle.ControlElement.CE_PushButtonLabel, option, painter, self)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#c5a26c"), 1, Qt.PenStyle.DotLine))
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(3,3,-3,-3), 5, 5)
        painter.end()

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QLineEdit


class TagEdit(QLineEdit):
    """Display tags as pills; focus restores the ordinary editable text."""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(34)
        self.textChanged.connect(self.update_hint)

    def update_hint(self, text):
        self.setToolTip((text + "\n" if text else "") + "Нажмите для изменения. Разделяйте теги запятыми.")

    def paintEvent(self, event):
        tags = [value.strip() for value in self.text().split(",") if value.strip()]
        if self.hasFocus() or not tags:
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        metrics = self.fontMetrics()
        x = 1
        for index, tag in enumerate(tags):
            available = self.width() - x - 2
            if available < 24:
                break
            reserve = 32 if index < len(tags)-1 else 0
            width = min(metrics.horizontalAdvance(tag)+18, max(24, available-reserve))
            label = metrics.elidedText(tag, Qt.TextElideMode.ElideRight, int(width)-16)
            overflow = index > 0 and metrics.horizontalAdvance(tag)+18 > available
            if overflow:
                label = f"+{len(tags)-index}"
                width = min(available, metrics.horizontalAdvance(label)+16)
            rect = QRectF(x, 4, width, max(1,self.height()-8))
            painter.setPen(QPen(QColor("#5c4c35"), 1))
            painter.setBrush(QColor("#30291f"))
            painter.drawRoundedRect(rect, 11, 11)
            painter.setPen(QColor("#d5bd96"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
            x += width+5
            if overflow:
                break
        painter.end()

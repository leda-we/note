from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPainterPath


def make_icon(kind, color="#c9ad83"):
    pixmap = QPixmap(48, 48)
    pixmap.setDevicePixelRatio(2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(color), 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    if kind == "search":
        painter.drawEllipse(QRectF(4, 3, 12, 12))
        painter.drawLine(14, 14, 21, 21)
    elif kind == "focus":
        for x,y,dx,dy in ((3,3,1,1),(21,3,-1,1),(3,21,1,-1),(21,21,-1,-1)):
            painter.drawLine(x,y,x+dx*5,y)
            painter.drawLine(x,y,x,y+dy*5)
    elif kind == "character":
        painter.drawEllipse(QRectF(8, 3, 8, 8))
        path = QPainterPath(QPointF(4, 21))
        path.cubicTo(4, 11, 20, 11, 20, 21)
        path.closeSubpath()
        painter.drawPath(path)
    elif kind == "location":
        path = QPainterPath(QPointF(12, 22))
        path.cubicTo(9, 18, 4, 13, 4, 9)
        path.cubicTo(4, -1, 20, -1, 20, 9)
        path.cubicTo(20, 13, 15, 18, 12, 22)
        painter.drawPath(path)
        painter.drawEllipse(QRectF(9, 6, 6, 6))
    elif kind in ("book", "all"):
        painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2, 2)
        painter.drawLine(12, 4, 12, 20)
        painter.drawLine(6, 8, 9, 8)
        painter.drawLine(15, 8, 18, 8)
        painter.drawLine(6, 12, 9, 12)
        painter.drawLine(15, 12, 18, 12)
    elif kind == "home":
        path = QPainterPath(QPointF(2, 11))
        path.lineTo(12, 3)
        path.lineTo(22, 11)
        painter.drawPath(path)
        painter.drawRect(QRectF(5, 10, 14, 11))
        painter.drawRect(QRectF(10, 14, 4, 7))
    else:
        painter.drawRoundedRect(QRectF(5, 3, 14, 18), 2, 2)
        for y in (8, 12, 16):
            painter.drawLine(8, y, 16 if y != 16 else 12, y)
    painter.end()
    return QIcon(pixmap)

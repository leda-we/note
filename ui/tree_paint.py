from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPalette, QPen, QPainterPath
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle


class BookItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        clean = QStyleOptionViewItem(option)
        selected = bool(clean.state & QStyle.StateFlag.State_Selected)
        clean.state &= ~(QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver | QStyle.StateFlag.State_HasFocus)
        if selected:
            clean.palette.setColor(QPalette.ColorRole.Text, QColor("#f0d7b1"))
        super().paint(painter, clean, index)


def paint_row_background(tree, painter, option, index):
    selected = tree.selectionModel().isSelected(index)
    hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
    if not selected and not hovered:
        return
    painter.save()
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1, option.rect.y()+1, tree.viewport().width()-2, option.rect.height()-2)
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor("#513c25" if selected else "#30291f"))
        gradient.setColorAt(1, QColor("#3a2e21" if selected else "#30291f"))
        painter.setPen(QPen(QColor(0,0,0,0)))
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, 5, 5)
    finally:
        painter.restore()


def paint_branch(tree, painter, rect, index):
    painter.save()
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if tree.selectionModel().isSelected(index):
            painter.save()
            painter.setClipRect(rect)
            painter.fillRect(rect, QColor("#1c1a17"))
            option = QStyleOptionViewItem()
            option.rect = rect
            paint_row_background(tree, painter, option, index)
            painter.restore()
        if not tree.model().hasChildren(index):
            return
        painter.setPen(QPen(QColor("#bda98a"), 1.2))
        x, y = rect.right()-8, rect.center().y()
        path = QPainterPath()
        points = ((x-3,y-2),(x,y+1),(x+3,y-2)) if tree.isExpanded(index) else ((x-2,y-3),(x+1,y),(x-2,y+3))
        path.moveTo(QPointF(*points[0]))
        for point in points[1:]:
            path.lineTo(QPointF(*point))
        painter.drawPath(path)
    finally:
        painter.restore()

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QTreeWidget, QAbstractItemView, QStyle, QStyleOptionViewItem
from ui.tree_paint import BookItemDelegate, paint_row_background, paint_branch

ROLE = Qt.ItemDataRole.UserRole


class BookTree(QTreeWidget):
    structure_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("bookTree")
        self.setItemDelegate(BookItemDelegate(self))
        self.setMouseTracking(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setAutoScroll(True)
        self.setAutoExpandDelay(600)
        self._dragging = False
        self._pending_structure = None
        self.commit_timer = QTimer(self)
        self.commit_timer.setSingleShot(True)
        self.commit_timer.timeout.connect(self.flush_structure)

    def drawRow(self, painter, option, index):
        paint_row_background(self, painter, option, index)
        clean = QStyleOptionViewItem(option)
        clean.state &= ~(QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver | QStyle.StateFlag.State_HasFocus)
        super().drawRow(painter, clean, index)

    def drawBranches(self, painter, rect, index):
        paint_branch(self, painter, rect, index)

    def startDrag(self, supported_actions):
        self._dragging = True
        try:
            super().startDrag(supported_actions)
        finally:
            self._dragging = False
            if self._pending_structure is not None:
                self.commit_timer.start(0)

    def flush_structure(self):
        if self._dragging or self._pending_structure is None:
            return
        structure = self._pending_structure
        self._pending_structure = None
        self.structure_changed.emit(structure)

    def snapshot(self):
        result = []
        for index in range(self.topLevelItemCount()):
            node = self.topLevelItem(index)
            kind, identifier = node.data(0, ROLE)
            result.append({
                "kind": kind,
                "id": identifier,
                "children": [node.child(i).data(0, ROLE)[1] for i in range(node.childCount())],
            })
        return result

    @staticmethod
    def can_place(node, parent):
        if node is None:
            return False
        kind, _ = node.data(0, ROLE)
        if kind == "part":
            return parent is None
        return parent is None or (parent is not node and parent.data(0, ROLE)[0] == "part")

    def valid_drop(self, event):
        if event.source() is not self:
            return False
        target = self.itemAt(event.position().toPoint())
        indicator = self.dropIndicatorPosition()
        if indicator == QAbstractItemView.DropIndicatorPosition.OnItem:
            parent = target
        elif indicator == QAbstractItemView.DropIndicatorPosition.OnViewport or target is None:
            parent = None
        else:
            parent = target.parent()
        return self.can_place(self.currentItem(), parent)

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)
        if not self.valid_drop(event):
            event.ignore()

    def dropEvent(self, event):
        if not self.valid_drop(event):
            event.ignore()
            return
        before = self.snapshot()
        # Qt performs the move itself, preserving item identity and selected chapter.
        blocked = self.blockSignals(True)
        try:
            super().dropEvent(event)
        finally:
            self.blockSignals(blocked)
        after = self.snapshot()
        if after != before:
            self._pending_structure = after
            if not self._dragging:
                self.commit_timer.start(0)

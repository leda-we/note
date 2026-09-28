from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QImage
from PySide6.QtWidgets import QApplication, QMenu


def clipboard_image():
    clipboard = QApplication.clipboard()
    image = clipboard.image()
    if not image.isNull():
        return image
    mime = clipboard.mimeData()
    if mime.hasUrls():
        for url in mime.urls():
            if url.isLocalFile():
                image = QImage(url.toLocalFile())
                if not image.isNull():
                    return image
    return QImage()


def enable_image_paste(widget, callback):
    widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    widget.setToolTip("Нажмите на изображение и Ctrl+V, чтобы вставить из буфера обмена.")
    shortcut = QShortcut(QKeySequence.StandardKey.Paste, widget)
    shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
    shortcut.activated.connect(callback)
    widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    def show_menu(position):
        menu = QMenu(widget)
        action = menu.addAction("Вставить изображение")
        action.triggered.connect(callback)
        menu.exec(widget.mapToGlobal(position))
    widget.customContextMenuRequested.connect(show_menu)
    return shortcut

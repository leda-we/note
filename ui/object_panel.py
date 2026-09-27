from PySide6.QtCore import Signal
from PySide6.QtWidgets import *

class ObjectPanel(QWidget):
    description_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(280)
        self.setMaximumWidth(420)
        self.loading = False

        layout = QVBoxLayout(self)
        self.name_label = QLabel()
        self.name_label.setStyleSheet("""font-size: 22px; font-weight: bold;""")
        self.type_label = QLabel()
        description_title = QLabel("Описание")
        self.description_editor = QTextEdit()
        self.description_editor.setPlaceholderText("Добавьте описание...")

        layout.addWidget(self.name_label)
        layout.addWidget(self.type_label)
        layout.addSpacing(20)
        layout.addWidget(description_title)
        layout.addWidget(self.description_editor)

        self.description_editor.textChanged.connect(self.on_description_changed)
    def show_item(self, name, item_type, description):
        self.loading = True
        self.name_label.setText(name)
        self.type_label.setText(item_type)

        self.description_editor.setPlainText(description)
        self.loading = False

    def on_description_changed(self):
        if self.loading:
            return
        description = (self.description_editor.toPlainText())
        self.description_changed.emit(description)
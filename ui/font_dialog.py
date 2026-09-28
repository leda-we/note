from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QFontComboBox, QSpinBox, QLabel, QDialogButtonBox


class FontDialog(QDialog):
    def __init__(self, font, selection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Шрифт рукописи")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)
        hint = QLabel("Изменить выделенный текст" if selection else "Изменить всю текущую главу и шрифт новых глав")
        hint.setObjectName("muted")
        layout.addWidget(hint)
        form = QFormLayout()
        self.family = QFontComboBox()
        self.family.setCurrentFont(font)
        self.size = QSpinBox()
        self.size.setRange(8, 72)
        self.size.setValue(round(font.pointSizeF()) if font.pointSizeF() > 0 else 15)
        self.size.setSuffix(" пт")
        form.addRow("Гарнитура", self.family)
        form.addRow("Размер", self.size)
        layout.addLayout(form)
        self.preview = QLabel("История начинается\nс первой строки.")
        self.preview.setObjectName("fontPreview")
        self.preview.setMinimumHeight(150)
        self.preview.setWordWrap(True)
        layout.addWidget(self.preview)
        self.family.currentFontChanged.connect(self.update_preview)
        self.size.valueChanged.connect(self.update_preview)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Применить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.update_preview()

    def chosen_font(self):
        return QFont(self.family.currentFont().family(), self.size.value())

    def update_preview(self, *args):
        font = self.chosen_font()
        self.preview.setFont(font)
        self.preview.setStyleSheet(f'font-family: "{font.family()}"; font-size: {font.pointSize()}pt;')

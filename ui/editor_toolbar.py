from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QTextBlockFormat, QTextListFormat, QKeySequence, QShortcut, QTextCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QComboBox


class EditorToolbar(QFrame):
    link_requested = Signal()
    font_requested = Signal()

    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setObjectName("editorToolbar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        self.paragraph = QComboBox()
        self.paragraph.addItems(["Абзац", "Заголовок 1", "Заголовок 2", "Цитата"])
        self.paragraph.setFixedWidth(112)
        self.paragraph.activated.connect(self.set_paragraph)
        layout.addWidget(self.paragraph)
        self.font_button = self.button("Aa", "Шрифт и размер текста", lambda _: self.font_requested.emit(), False)
        layout.addWidget(self.font_button)
        self.bold_button = self.button("B", "Жирный · Ctrl+B", self.set_bold)
        self.italic_button = self.button("I", "Курсив · Ctrl+I", self.set_italic)
        self.underline_button = self.button("U", "Подчёркнутый · Ctrl+U", self.set_underline)
        for button in (self.bold_button, self.italic_button, self.underline_button):
            layout.addWidget(button)
        link = self.button("↗", "Ссылка на объект · Ctrl+K", lambda _: self.link_requested.emit(), False)
        layout.addWidget(link)
        bullets = self.button("≡", "Маркированный список", self.toggle_list, False)
        layout.addWidget(bullets)
        align = self.button("☷", "По ширине / по левому краю", self.toggle_alignment, False)
        layout.addWidget(align)
        layout.addStretch()
        self.word_count_label = QLabel()
        self.word_count_label.setObjectName("wordCount")
        layout.addWidget(self.word_count_label)
        self.shortcuts = []
        for key, button in [("Ctrl+B", self.bold_button), ("Ctrl+I", self.italic_button), ("Ctrl+U", self.underline_button), ("Ctrl+K", link)]:
            shortcut = QShortcut(QKeySequence(key), self.editor)
            shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
            shortcut.activated.connect(button.click)
            self.shortcuts.append(shortcut)
        self.editor.currentCharFormatChanged.connect(self.update_buttons)
        self.editor.cursorPositionChanged.connect(self.update_paragraph)
        self.editor.textChanged.connect(self.update_word_count)
        self.refresh()

    def button(self, text, tooltip, callback, checkable=True):
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip)
        button.setCheckable(checkable)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.clicked.connect(callback)
        return button

    def apply_format(self, text_format):
        self.editor.mergeCurrentCharFormat(text_format)
        self.editor.setFocus()

    def set_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
        self.apply_format(fmt)

    def set_italic(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self.apply_format(fmt)

    def set_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(checked)
        self.apply_format(fmt)

    def set_paragraph(self, index):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        block = QTextBlockFormat()
        block.setHeadingLevel(index if index in (1, 2) else 0)
        block.setTopMargin(18 if index else 0)
        block.setBottomMargin(16)
        block.setLeftMargin(24 if index == 3 else 0)
        block.setLineHeight(145, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
        cursor.mergeBlockFormat(block)
        fmt = QTextCharFormat()
        base = self.editor.document().defaultFont().pointSizeF()
        base = base if base > 0 else 15
        fmt.setFontPointSize([base, base * 5 / 3, base * 4 / 3, base][index])
        fmt.setFontWeight(QFont.Weight.Bold if index in (1, 2) else QFont.Weight.Normal)
        fmt.setFontItalic(index == 3)
        original = QTextCursor(cursor)
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        first = cursor.position()
        cursor.setPosition(end - 1 if end > start else end)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        cursor.setPosition(first, QTextCursor.MoveMode.KeepAnchor)
        cursor.mergeCharFormat(fmt)
        cursor.mergeBlockCharFormat(fmt)
        cursor.endEditBlock()
        self.editor.setTextCursor(original)
        if not original.hasSelection():
            self.editor.mergeCurrentCharFormat(fmt)
        self.update_paragraph()
        self.editor.setFocus()

    def toggle_list(self, checked=False):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        current = cursor.currentList()
        if current:
            current.remove(cursor.block())
            fmt = cursor.blockFormat()
            fmt.setIndent(0)
            cursor.setBlockFormat(fmt)
        else:
            fmt = QTextListFormat()
            fmt.setStyle(QTextListFormat.Style.ListDisc)
            cursor.createList(fmt)
        cursor.endEditBlock()
        self.editor.setFocus()

    def toggle_alignment(self, checked=False):
        alignment = self.editor.alignment()
        self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft if alignment == Qt.AlignmentFlag.AlignJustify else Qt.AlignmentFlag.AlignJustify)
        self.editor.setFocus()

    def update_buttons(self, fmt):
        self.bold_button.setChecked(fmt.fontWeight() >= QFont.Weight.Bold)
        self.italic_button.setChecked(fmt.fontItalic())
        self.underline_button.setChecked(fmt.fontUnderline())

    def update_paragraph(self):
        block = self.editor.textCursor().blockFormat()
        level = block.headingLevel()
        self.paragraph.setCurrentIndex(level if level in (1, 2) else (3 if block.leftMargin() > 0 else 0))

    def update_word_count(self):
        count = len(self.editor.toPlainText().split())
        self.word_count_label.setText(f"{count:,} слов".replace(",", " "))

    def refresh(self):
        self.update_buttons(self.editor.currentCharFormat())
        self.update_paragraph()
        self.update_word_count()

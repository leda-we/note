APP_STYLE = """
QMainWindow {
    background-color: #15110f;
    color: #f1e4d0;
}

QWidget {
    background-color: #15110f;
    color: #f1e4d0;
    font-family: "Georgia";
    font-size: 14px;
}

QLabel {
    color: #f1e4d0;
    background: transparent;
}

QPushButton {
    background-color: #2a211d;
    color: #f1e4d0;
    border: 1px solid #4a3931;
    border-radius: 10px;
    padding: 8px 12px;
}

QPushButton:hover {
    background-color: #342823;
}

QPushButton:pressed {
    background-color: #221a17;
}

QListWidget {
    background-color: #181311;
    border: 1px solid #2f2520;
    border-radius: 14px;
    outline: none;
    padding: 8px;
}

QListWidget::item {
    background: transparent;
    color: #eadbc7;
    padding: 10px 12px;
    margin: 4px 0;
    border-radius: 10px;
}

QListWidget::item:selected {
    background-color: #4a3325;
    color: #fff3e3;
}

QListWidget::item:hover {
    background-color: #2c221d;
}

QTextEdit {
    background-color: #1b1613;
    color: #f1e4d0;
    border: 1px solid #2f2520;
    border-radius: 16px;
    selection-background-color: #6a4a35;
    selection-color: #fff7ef;
}

QLineEdit {
    background-color: #1b1613;
    color: #f1e4d0;
    border: 1px solid #2f2520;
    border-radius: 10px;
    padding: 8px 10px;
}

QMenu {
    background-color: #1c1714;
    color: #f1e4d0;
    border: 1px solid #3b2c25;
    padding: 8px;
}

QMenu::item {
    padding: 8px 18px;
    border-radius: 8px;
}

QMenu::item:selected {
    background-color: #4a3325;
}

QScrollBar:vertical {
    background: #181311;
    width: 10px;
    margin: 4px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #5a4438;
    min-height: 30px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #6f5546;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #181311;
    height: 10px;
    margin: 4px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: #5a4438;
    min-width: 30px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #6f5546;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}
"""
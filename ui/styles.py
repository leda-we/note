APP_STYLE = """
QWidget { background: #1c1a17; color: #e4d9c7; font-family: "Segoe UI"; font-size: 13px; }
QMainWindow, QWidget#centralWidget { background: #171614; }
QLabel { background: transparent; }
QFrame { border: none; }
QFrame#appHeader { background: #201e1a; border-bottom: 1px solid #373129; }
QPushButton#bookTitle { font-family: "Georgia"; font-size: 18px; text-align: left; border: none; background: transparent; }
QLabel#chapterTitle, QLabel#muted, QLabel#wordCount { color: #a99e8c; }
QLabel#eyebrow { color: #ab9677; font-size: 11px; padding: 5px 2px; }
QLabel#pageTitle { font-family: "Georgia"; font-size: 29px; color: #ede0c9; padding: 20px 12px 8px; }
QLabel#ornament { color: #b68c55; font-size: 18px; padding-bottom: 8px; }
QLabel#bookSummary { background: #24211c; padding: 14px; border-radius: 7px; line-height: 1.5; }
QWidget#chapterPanel, QFrame#rightPanel { background: #1c1a17; }
QFrame#editorContainer, QWidget#pageContainer { background: #171614; }
QFrame#paper { background: #211f1b; border: 1px solid #2d2923; border-radius: 9px; }
QLabel#pageTitle, QLabel#ornament { background: transparent; }
QTextEdit#bookEditor { background: #211f1b; color: #e8ddca; border: none; border-radius: 8px; font-family: "Georgia"; font-size: 20px; }
QFrame#editorToolbar { background: #1c1a17; border-bottom: 1px solid #302c25; }
QPushButton, QToolButton { background: #28241e; border: 1px solid #393229; border-radius: 5px; padding: 7px 10px; }
QPushButton:hover, QToolButton:hover { background: #383024; border-color: #655037; }
QPushButton:pressed, QToolButton:checked { background: #4b3825; color: #f5d19a; }
QPushButton:disabled, QToolButton:disabled { color: #6d665c; }
QPushButton#navButton { background: transparent; border: none; text-align: left; padding: 9px 12px; font-size: 14px; }
QPushButton#navButton:hover { background: #29251f; }
QPushButton#navButton:checked { background: #443323; color: #f1d3a4; }
QPushButton#smallButton { padding: 2px 7px; border: none; background: transparent; font-size: 20px; color: #c6a77e; }
QToolButton { min-width: 22px; min-height: 22px; padding: 3px; font-family: "Georgia"; font-size: 16px; background: transparent; border-color: transparent; }
QLineEdit, QComboBox, QSpinBox { background: #24211c; border: 1px solid #3a332a; border-radius: 5px; padding: 6px; selection-background-color: #6c5030; }
QLineEdit:focus, QTextEdit:focus { border-color: #8e6c43; }
QLineEdit#objectName { background: transparent; font-family: "Georgia"; font-size: 24px; border: none; padding: 0; }
QTextEdit { background: #24211d; border: 1px solid #373128; border-radius: 6px; padding: 8px; selection-background-color: #715335; selection-color: #fff5e4; }
QTextEdit#quoteEditor { font-family: "Georgia"; font-style: italic; color: #cbbda8; }
QLabel#objectImage { background: #29251e; border: 1px solid #42372a; border-radius: 8px; color: #a9906d; }
QTreeWidget, QListWidget { background: transparent; border: none; outline: none; }
QTreeWidget::item { padding: 7px 2px; border-radius: 4px; }
QListWidget::item { padding: 10px 8px; border-radius: 4px; }
QTreeWidget::item:selected, QListWidget::item:selected { background: #493623; color: #f0d7b1; }
QTreeWidget::item:hover, QListWidget::item:hover { background: #30291f; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: transparent; color: #b1a694; padding: 11px 13px; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #f0dfc3; border-bottom-color: #c49a60; }
QScrollArea { border: none; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: #514536; min-height: 30px; border-radius: 3px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { height: 8px; background: transparent; }
QScrollBar::handle:horizontal { background: #514536; min-width: 25px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QSplitter::handle { background: #332e26; }
QSplitter::handle:hover { background: #ae8551; }
QMenu { background: #24201a; border: 1px solid #44392b; padding: 6px; }
QMenu::item { padding: 8px 24px; }
QMenu::item:selected { background: #493623; }
QProgressBar { border: none; background: #39332a; border-radius: 2px; }
QProgressBar::chunk { background: #b38a55; border-radius: 2px; }
QStatusBar { color: #9d917f; background: #1c1a17; border-top: 1px solid #302b23; }
QToolTip { background: #30291f; color: #edddc5; border: 1px solid #72593c; padding: 6px; }

/* Refined surfaces and typography. */
QFrame#appHeader { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #25221d,stop:1 #1c1a17); border-bottom: 1px solid #40372a; }
QWidget#chapterPanel, QFrame#rightPanel { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #211e19,stop:1 #191816); }
QWidget#pageContainer, QFrame#editorContainer { background: #161513; }
QFrame#paper { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #25221d,stop:0.6 #211f1b,stop:1 #1e1c18); border: 1px solid #393126; border-radius: 8px; }
QTextEdit#bookEditor { background: transparent; padding: 4px 6px; }
QLabel#pageKicker { background: transparent; color: #ae9876; font-family: "Segoe UI"; font-size: 11px; padding-top: 12px; }
QLabel#pageTitle { font-family: "Georgia"; font-weight: normal; font-size: 30px; padding: 12px 28px 10px; color: #f0e2cb; }
QLabel#ornament { color: #a8804b; padding-bottom: 16px; }
QPushButton#libraryButton { background: transparent; border: 1px solid #4a3b28; padding: 7px 11px; color: #c9ac7c; }
QPushButton#quietButton { background: transparent; color: #ad9b80; border: none; padding: 3px 6px; font-size: 11px; }
QPushButton#quietButton:hover { color: #f0d3a0; background: #30281e; }
QPushButton#navButton { font-family: "Georgia"; font-size: 14px; padding: 8px 12px; }
QTreeWidget { font-family: "Georgia"; font-size: 13px; }
QTreeWidget::item { padding: 5px 2px; }
QTreeWidget::item:selected, QListWidget::item:selected { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #513c25,stop:1 #3a2e21); }
QLineEdit#objectName { color: #f0e2ce; font-size: 26px; padding: 4px 0; }
QTextEdit#quoteEditor { background: #25221c; border: 1px solid #3c3428; border-left: 2px solid #8e6c43; font-size: 14px; padding: 10px; }
QFrame#rightPanel QLineEdit { background: transparent; border: none; border-bottom: 1px solid #3b3328; border-radius: 0; }
QFrame#rightPanel QLineEdit:focus { border-bottom: 1px solid #b99158; }
QFrame#rightPanel QLineEdit#objectName { border: none; }
QFrame#rightPanel QTextEdit { font-family: "Georgia"; font-size: 13px; }
QLabel#bookSummary { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #2d261c,stop:1 #211e18); border: 1px solid #3a3023; font-family: "Georgia"; padding: 14px; }
QFrame#editorToolbar QComboBox { border: none; background: transparent; padding: 5px 6px; }
QWidget#libraryPage, QWidget#libraryShelf { background: #191816; }
QLabel#libraryTitle { font-family: "Georgia"; font-size: 38px; color: #eee1ca; }
QLabel#librarySubtitle { color: #aa9c86; font-size: 14px; padding: 4px 0; }
QFrame#bookCard { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #29251f,stop:1 #211e19); border: 1px solid #423727; border-radius: 9px; }
QFrame#bookCard:hover { border-color: #8b6d43; }
QFrame#bookCard QLabel, QFrame#bookCard QWidget { background: transparent; }
QLabel#cardTitle { font-family: "Georgia"; font-size: 19px; color: #eadcc4; }
QPushButton#primaryButton { background: #a57e4b; color: #161411; border: 1px solid #c49c63; padding: 10px 18px; font-weight: 600; }
QPushButton#primaryButton:hover { background: #bd955c; }
QLabel#fontPreview { background: #24211c; color: #e8dac0; padding: 18px; border: 1px solid #4b3c28; border-radius: 6px; }

QPushButton#libraryButton { background: transparent; border: none; padding: 8px 12px; }
QWidget#toolbarContainer { background: #171511; }
QFrame#editorToolbar { background: #211e19; border: 1px solid #3a3228; border-radius: 12px; }
QTreeWidget#bookTree::item, QTreeWidget#bookTree::item:selected, QTreeWidget#bookTree::item:hover { background: transparent; border: none; }
"""

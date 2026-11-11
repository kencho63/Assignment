"""Qt stylesheet (QSS) that gives the whole app its custom look.

Widgets opt in to special looks through setObjectName(...), for example
button.setObjectName("primary") picks up the QPushButton#primary rule.
Combo boxes and spin boxes keep their default borders on purpose: styling a
border would make Qt stop drawing their arrows.
"""

APP_STYLE = """
QWidget { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; font-size: 14px; color: #1f2937; }
QMainWindow, QDialog { background-color: #f3f5fa; }
QLabel { background: transparent; }

QLabel#title     { font-size: 28px; font-weight: bold; color: #1e3a8a; }
QLabel#heading   { font-size: 18px; font-weight: bold; color: #1e3a8a; }
QLabel#statValue { font-size: 26px; font-weight: bold; color: #2563eb; }
QLabel#statTitle { color: #6b7280; }
QLabel#hint      { color: #6b7280; font-size: 12px; }

QFrame#card { background-color: white; border: 1px solid #dfe3ee; border-radius: 12px; }

QTabWidget::pane { border: none; }
QTabBar::tab { background: #e5e9f5; padding: 10px 22px; margin-right: 3px;
               border-top-left-radius: 8px; border-top-right-radius: 8px; font-weight: 600; }
QTabBar::tab:selected { background: #2563eb; color: white; }
QTabBar::tab:hover:!selected { background: #d5dbef; }

QLineEdit { background: white; border: 1px solid #c3cadb; border-radius: 6px; padding: 7px; }
QLineEdit:focus { border: 1px solid #2563eb; }
QLineEdit:disabled { background: #eceff6; color: #6b7280; }

QPushButton { background-color: #e5e9f5; border: none; border-radius: 8px;
              padding: 9px 18px; min-width: 70px; font-weight: 600; }
QPushButton:hover    { background-color: #d5dbef; }
QPushButton:disabled { background-color: #e5e7eb; color: #9ca3af; }
QPushButton#primary       { background-color: #2563eb; color: white; }
QPushButton#primary:hover { background-color: #1d4ed8; }
QPushButton#primary:disabled { background-color: #b7cdfa; color: white; }
QPushButton#danger        { background-color: #dc2626; color: white; }
QPushButton#danger:hover  { background-color: #b91c1c; }
QPushButton#danger:disabled { background-color: #f3b4b4; color: white; }

QTableWidget { background: white; alternate-background-color: #f6f8fd; border: 1px solid #dfe3ee;
               border-radius: 8px; gridline-color: #e8ebf3;
               selection-background-color: #cfe0ff; selection-color: #111827; }
QHeaderView::section { background-color: #1e3a8a; color: white; padding: 7px; border: none; font-weight: bold; }

QProgressBar { border: 1px solid #c3cadb; border-radius: 6px; background: white;
               text-align: center; height: 18px; }
QProgressBar::chunk { background-color: #2563eb; border-radius: 5px; }

QStatusBar { background: #e5e9f5; }
QToolTip { background: #1e3a8a; color: white; border: none; padding: 4px; }
"""

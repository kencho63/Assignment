"""Main window: menu bar + tabs (dashboard, students, marks, reports)."""

from PyQt6.QtCore import PYQT_VERSION_STR
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

import config
from ui.dashboard_page import DashboardPage
from ui.marks_page import MarksPage
from ui.reports_page import ReportsPage
from ui.students_page import StudentsPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Name and roll number in the title so every screenshot shows them
        self.setWindowTitle(f"{config.APP_NAME} - {config.STUDENT_NAME} ({config.ROLL_NO})")
        self.resize(1180, 740)
        self.setMinimumSize(980, 620)

        self.dashboard_page = DashboardPage()
        self.students_page = StudentsPage()
        self.marks_page = MarksPage()
        self.reports_page = ReportsPage()

        # Order must match the TAB_* numbers in config.py
        self.tabs = QTabWidget()
        self.tabs.addTab(self.dashboard_page, "Dashboard")
        self.tabs.addTab(self.students_page, "Students")
        self.tabs.addTab(self.marks_page, "Marks")
        self.tabs.addTab(self.reports_page, "Reports")
        self.setCentralWidget(self.tabs)

        self._create_menu_bar()
        self._connect_signals()
        self.dashboard_page.refresh()
        self.statusBar().showMessage("Ready")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        self._add_action(file_menu, "E&xit", "Ctrl+Q", self.close)

        go_menu = menu_bar.addMenu("&Go to")
        for number, name in enumerate(["&Dashboard", "&Students", "&Marks", "&Reports"]):
            # default argument i=number remembers which tab this menu item opens
            self._add_action(go_menu, name, f"Ctrl+{number + 1}",
                             lambda checked=False, i=number: self.tabs.setCurrentIndex(i))

        help_menu = menu_bar.addMenu("&Help")
        self._add_action(help_menu, "&About", "F1", self.show_about)

    def _add_action(self, menu, text, shortcut, slot):
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)

    def _connect_signals(self):
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.dashboard_page.navigate.connect(self.tabs.setCurrentIndex)
        for page in (self.students_page, self.marks_page, self.reports_page):
            page.status_message.connect(self.statusBar().showMessage)

    def on_tab_changed(self, index: int):
        """Every page reloads its data when it is opened, so tabs never show stale numbers."""
        self.tabs.widget(index).refresh()

    def show_about(self):
        QMessageBox.about(
            self, f"About {config.APP_NAME}",
            f"<h3>{config.APP_NAME} - Student Record Manager</h3>"
            f"<p>{config.STUDENT_NAME} - Roll No: {config.ROLL_NO}<br>{config.COURSE_NAME}</p>"
            f"<p>Built with PyQt6 {PYQT_VERSION_STR} and SQLite.</p>")

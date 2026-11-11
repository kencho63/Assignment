"""Dashboard: key numbers, a grade-distribution chart and the top students."""

import sqlite3

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QTableWidget, QVBoxLayout, QWidget,
)

import config
import database
import student_logic as logic
from ui.bar_chart import BarChart
from ui.helpers import configure_table, make_item, make_stat_card, show_db_error


class DashboardPage(QWidget):
    navigate = pyqtSignal(int)              # asks the main window to open another tab

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.add_button.clicked.connect(lambda: self.navigate.emit(config.TAB_STUDENTS))
        self.marks_button.clicked.connect(lambda: self.navigate.emit(config.TAB_MARKS))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        title = QLabel("Class Overview")
        title.setObjectName("title")
        self.add_button = QPushButton("Add a Student")
        self.add_button.setObjectName("primary")
        self.marks_button = QPushButton("Enter Marks")
        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(self.add_button)
        top_row.addWidget(self.marks_button)
        layout.addLayout(top_row)

        cards = QHBoxLayout()
        specs = [("students", "Students", "#2563eb"), ("marks", "Marks recorded", "#0891b2"),
                 ("average", "Class average", "#7c3aed"), ("pass_rate", "Pass rate", "#16a34a"),
                 ("scholarships", "Scholarships", "#d97706")]
        self.stat_labels = {}
        for key, caption, color in specs:
            card, value_label = make_stat_card(caption, color)
            self.stat_labels[key] = value_label
            cards.addWidget(card)
        layout.addLayout(cards)

        lower = QHBoxLayout()
        chart_card = QFrame()
        chart_card.setObjectName("card")
        chart_layout = QVBoxLayout(chart_card)
        chart_title = QLabel("Students per grade")
        chart_title.setObjectName("heading")
        self.chart = BarChart()
        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.chart)
        lower.addWidget(chart_card, 1)

        top_card = QFrame()
        top_card.setObjectName("card")
        top_layout = QVBoxLayout(top_card)
        top_title = QLabel("Top 5 students")
        top_title.setObjectName("heading")
        self.top_table = QTableWidget()
        configure_table(self.top_table, ["Roll", "Name", "Average", "Grade"], stretch_column=1)
        top_layout.addWidget(top_title)
        top_layout.addWidget(self.top_table)
        lower.addWidget(top_card, 1)
        layout.addLayout(lower, 1)

    def refresh(self):
        try:
            students = database.list_students()
            averages = database.student_averages()
            mark_count = database.count_marks()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return

        graded = [a for a in averages if a[5] is not None]
        summary = logic.class_summary([a[5] for a in graded])
        self.stat_labels["students"].setText(str(len(students)))
        self.stat_labels["marks"].setText(str(mark_count))
        self.stat_labels["average"].setText(f"{summary['average']:.1f}%")
        self.stat_labels["pass_rate"].setText(f"{summary['pass_rate']:.0f}%")
        self.stat_labels["scholarships"].setText(str(sum(1 for s in students if s.scholarship)))

        counts = logic.grade_distribution([a[5] for a in graded])
        self.chart.set_data(config.GRADES, [counts[g] for g in config.GRADES],
                            [config.GRADE_COLORS[g] for g in config.GRADES])

        top = sorted(graded, key=lambda a: a[5], reverse=True)[:5]
        self.top_table.setRowCount(len(top))
        for r, (roll, name, _course, _sch, _n, average) in enumerate(top):
            grade = logic.grade_for(average)
            values = [roll, name, f"{average:.1f}%", grade]
            for c, value in enumerate(values):
                color = config.GRADE_COLORS[grade] if c == 3 else None
                self.top_table.setItem(r, c, make_item(value, centered=c != 1, color=color))

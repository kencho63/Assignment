"""Reports tab: every student's average and grade, with filters and CSV export."""

import csv
import sqlite3

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QVBoxLayout, QWidget,
)

import config
import database
import student_logic as logic
from ui.helpers import configure_table, make_item, show_db_error, show_warning

HEADERS = ["Roll", "Name", "Course", "Subjects", "Average %", "Grade", "Scholarship"]


class ReportsPage(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.display_rows: list[list[str]] = []     # what the table currently shows
        self._build_ui()
        self._connect_signals()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        heading = QLabel("Results Report")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by roll number or name")
        self.search_input.setClearButtonEnabled(True)
        self.course_combo = QComboBox()
        self.course_combo.addItem(config.ALL_COURSES)
        self.course_combo.addItems(config.COURSES)
        self.grade_combo = QComboBox()
        self.grade_combo.addItem(config.ALL_GRADES)
        self.grade_combo.addItems(list(config.GRADES) + [config.NO_GRADE])
        self.export_button = QPushButton("Export to CSV")
        self.export_button.setObjectName("primary")
        filter_row.addWidget(self.search_input, 3)
        filter_row.addWidget(self.course_combo, 2)
        filter_row.addWidget(self.grade_combo, 1)
        filter_row.addWidget(self.export_button)
        layout.addLayout(filter_row)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("hint")
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        configure_table(self.table, HEADERS, stretch_column=1)
        layout.addWidget(self.table)

    def _connect_signals(self):
        self.search_input.textChanged.connect(self.refresh)
        self.course_combo.currentIndexChanged.connect(self.refresh)
        self.grade_combo.currentIndexChanged.connect(self.refresh)
        self.export_button.clicked.connect(self.export_csv)

    def refresh(self):
        try:
            data = database.student_averages()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return

        text = self.search_input.text().strip().lower()
        course = self.course_combo.currentText()
        wanted_grade = self.grade_combo.currentText()

        rows = []                                   # (average or None, display values, grade)
        for roll, name, student_course, scholarship, subjects, average in data:
            grade = logic.grade_for(average) if average is not None else config.NO_GRADE
            if text and text not in roll.lower() and text not in name.lower():
                continue
            if course != config.ALL_COURSES and student_course != course:
                continue
            if wanted_grade != config.ALL_GRADES and grade != wanted_grade:
                continue
            shown = "-" if average is None else f"{average:.1f}"
            rows.append((average, [roll, name, student_course, str(subjects), shown, grade,
                                   "Yes" if scholarship else "No"]))
        rows.sort(key=lambda r: -1 if r[0] is None else r[0], reverse=True)

        self.display_rows = [values for _, values in rows]
        self.table.setRowCount(len(rows))
        for r, (_, values) in enumerate(rows):
            for c, value in enumerate(values):
                color = config.GRADE_COLORS[value] if c == 5 else None
                self.table.setItem(r, c, make_item(value, centered=c != 1, color=color))

        summary = logic.class_summary([avg for avg, _ in rows if avg is not None])
        self.summary_label.setText(
            f"{len(rows)} student(s) shown   |   Average of those graded: "
            f"{summary['average']:.1f}%   |   Pass rate: {summary['pass_rate']:.0f}%")

    def export_csv(self):
        if not self.display_rows:
            show_warning(self, "Nothing to export", "There are no rows to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export report", "student_report.csv", "CSV files (*.csv)")
        if not path:                                # user pressed Cancel
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(HEADERS)
                writer.writerows(self.display_rows)
        except OSError as error:
            show_warning(self, "Export failed", f"Could not write the file:\n\n{error}")
            return
        self.status_message.emit(f"Exported {len(self.display_rows)} row(s) to {path}")

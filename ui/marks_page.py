"""Marks tab: record subject marks for a student and see their average and grade."""

import sqlite3

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QPushButton, QSpinBox, QTableWidget, QVBoxLayout, QWidget,
)

import config
import database
import student_logic as logic
from models import Mark
from ui.helpers import (
    ask_yes_no, configure_table, make_item, set_message, show_db_error,
)

HEADERS = ["Subject", "Score", "Out of", "Percent", "Grade"]


class MarksPage(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.marks: list[Mark] = []                 # same order as the table rows
        self._build_ui()
        self._connect_signals()
        self.refresh()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # ----- left: entry form -----
        form_card = QFrame()
        form_card.setObjectName("card")
        form_card.setFixedWidth(380)
        card_layout = QVBoxLayout(form_card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        heading = QLabel("Enter Marks")
        heading.setObjectName("heading")
        card_layout.addWidget(heading)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        self.student_combo = QComboBox()
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g. Mathematics")
        self.subject_input.setMaxLength(40)
        self.score_spin = QDoubleSpinBox()
        self.score_spin.setRange(0, 1000)
        self.score_spin.setDecimals(1)
        self.score_spin.setSingleStep(0.5)
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 1000)
        self.max_spin.setValue(config.DEFAULT_MAX_SCORE)
        form.addRow("Student:", self.student_combo)
        form.addRow("Subject:", self.subject_input)
        form.addRow("Score:", self.score_spin)
        form.addRow("Out of:", self.max_spin)
        card_layout.addLayout(form)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        card_layout.addWidget(self.message_label)

        self.add_button = QPushButton("Add Marks")
        self.add_button.setObjectName("primary")
        self.delete_button = QPushButton("Delete Selected Marks")
        self.delete_button.setObjectName("danger")
        card_layout.addWidget(self.add_button)
        card_layout.addWidget(self.delete_button)
        card_layout.addStretch()
        main_layout.addWidget(form_card)

        # ----- right: summary + table -----
        right = QVBoxLayout()
        summary_card = QFrame()
        summary_card.setObjectName("card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(20, 14, 20, 14)
        self.student_label = QLabel("No student selected")
        self.student_label.setObjectName("heading")
        self.summary_label = QLabel()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        summary_layout.addWidget(self.student_label)
        summary_layout.addWidget(self.summary_label)
        summary_layout.addWidget(self.progress)
        right.addWidget(summary_card)

        self.table = QTableWidget()
        configure_table(self.table, HEADERS, stretch_column=0)
        right.addWidget(self.table)
        main_layout.addLayout(right, 1)

    def _connect_signals(self):
        self.student_combo.currentIndexChanged.connect(self.load_marks)
        self.add_button.clicked.connect(self.on_add)
        self.delete_button.clicked.connect(self.on_delete)
        self.table.itemSelectionChanged.connect(self._update_buttons)
        self.subject_input.textChanged.connect(lambda: self.message_label.clear())

    def refresh(self):
        """Reload the student list (students may have been added or deleted)."""
        try:
            students = database.list_students()
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        current = self.student_combo.currentData()
        self.student_combo.blockSignals(True)
        self.student_combo.clear()
        for s in students:
            self.student_combo.addItem(f"{s.roll} - {s.name}", s.roll)
        index = self.student_combo.findData(current)
        self.student_combo.setCurrentIndex(index if index >= 0 else 0)
        self.student_combo.blockSignals(False)
        self.load_marks()

    def load_marks(self):
        roll = self.student_combo.currentData()
        self.marks = []
        if roll is not None:
            try:
                self.marks = database.list_marks(roll)
            except sqlite3.Error as error:
                show_db_error(self, error)

        self.table.blockSignals(True)
        self.table.setRowCount(len(self.marks))
        for row, m in enumerate(self.marks):
            percent = logic.percentage(m.score, m.max_score)
            grade = logic.grade_for(percent)
            values = [m.subject, f"{m.score:g}", m.max_score, f"{percent:.1f}%", grade]
            for col, value in enumerate(values):
                color = config.GRADE_COLORS[grade] if col == 4 else None
                self.table.setItem(row, col, make_item(value, centered=col != 0, color=color))
        self.table.blockSignals(False)
        self._update_summary(roll)
        self._update_buttons()

    def _update_summary(self, roll):
        if roll is None:
            self.student_label.setText("No students yet - add one on the Students tab")
            self.summary_label.setText("")
            self.progress.setValue(0)
            return
        self.student_label.setText(self.student_combo.currentText())
        if not self.marks:
            self.summary_label.setText("No marks recorded yet.")
            self.progress.setValue(0)
            return
        percents = [logic.percentage(m.score, m.max_score) for m in self.marks]
        average = sum(percents) / len(percents)
        self.summary_label.setText(
            f"{len(self.marks)} subject(s)   |   Average {average:.1f}%   |   "
            f"Grade {logic.grade_for(average)}")
        self.progress.setValue(int(round(average)))

    def _update_buttons(self):
        has_student = self.student_combo.currentData() is not None
        self.add_button.setEnabled(has_student)
        self.delete_button.setEnabled(bool(self.table.selectionModel().selectedRows()))

    def on_add(self):
        roll = self.student_combo.currentData()
        if roll is None:
            set_message(self.message_label, "Add a student first.", ok=False)
            return
        try:
            subject, score, max_score = logic.validate_mark(
                self.subject_input.text(), self.score_spin.value(), self.max_spin.value())
            database.add_mark(roll, subject, score, max_score)
        except logic.ValidationError as error:
            set_message(self.message_label, str(error), ok=False)
            return
        except database.DuplicateMarkError:
            set_message(self.message_label,
                        "This student already has marks for that subject. "
                        "Delete the old entry first.", ok=False)
            return
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self.subject_input.clear()
        self.score_spin.setValue(0)
        self.load_marks()
        set_message(self.message_label, f"Saved {subject}.")
        self.status_message.emit(f"Marks added for {roll}")

    def on_delete(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        mark = self.marks[rows[0].row()]
        if not ask_yes_no(self, "Confirm delete", f"Delete the {mark.subject} marks?"):
            return
        try:
            database.delete_mark(mark.id)
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self.load_marks()
        set_message(self.message_label, f"Deleted {mark.subject}.")
        self.status_message.emit("Marks deleted")

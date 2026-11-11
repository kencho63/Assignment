"""Students tab: search / filter students and add, edit or delete them."""

import sqlite3

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QSpinBox, QTableWidget, QVBoxLayout, QWidget,
)

import config
import database
import student_logic as logic
from models import Student
from ui.helpers import (
    ask_yes_no, configure_table, make_item, set_message, show_db_error,
)

HEADERS = ["Roll", "Name", "Course", "Sem", "Gender", "Contact", "Scholarship"]


class StudentsPage(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.students: list[Student] = []       # same order as the table rows
        self.selected_roll: str | None = None
        self._build_ui()
        self._connect_signals()
        self.refresh()

    # ------------------------------------------------------------
    # Building the screen
    # ------------------------------------------------------------
    def _build_ui(self):
        main_layout = QHBoxLayout(self)                  # layout 1: form | table
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(16)

        # ----- left: form card -----
        form_card = QFrame()
        form_card.setObjectName("card")
        form_card.setFixedWidth(380)
        card_layout = QVBoxLayout(form_card)              # layout 2: stacked card
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        heading = QLabel("Student Details")
        heading.setObjectName("heading")
        card_layout.addWidget(heading)

        form = QFormLayout()                              # layout 3: label + field rows
        form.setVerticalSpacing(10)
        self.roll_input = QLineEdit()
        self.roll_input.setPlaceholderText("e.g. CS011")
        self.roll_input.setMaxLength(20)
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(50)
        self.course_combo = QComboBox()
        self.course_combo.addItems(config.COURSES)
        self.semester_spin = QSpinBox()
        self.semester_spin.setRange(config.MIN_SEMESTER, config.MAX_SEMESTER)

        self.gender_group = QButtonGroup(self)
        gender_row = QHBoxLayout()
        for gender in config.GENDERS:
            radio = QRadioButton(gender)
            self.gender_group.addButton(radio)
            gender_row.addWidget(radio)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Numbers only (optional)")
        self.contact_input.setMaxLength(12)
        self.scholarship_check = QCheckBox("Receives a scholarship")

        form.addRow("Roll No:", self.roll_input)
        form.addRow("Name:", self.name_input)
        form.addRow("Course:", self.course_combo)
        form.addRow("Semester:", self.semester_spin)
        form.addRow("Gender:", gender_row)
        form.addRow("Contact:", self.contact_input)
        form.addRow("", self.scholarship_check)
        card_layout.addLayout(form)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        card_layout.addWidget(self.message_label)

        buttons = QGridLayout()                           # layout 4: 2x2 button grid
        self.add_button = QPushButton("Add")
        self.add_button.setObjectName("primary")
        self.update_button = QPushButton("Update")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("danger")
        self.clear_button = QPushButton("Clear")
        buttons.addWidget(self.add_button, 0, 0)
        buttons.addWidget(self.update_button, 0, 1)
        buttons.addWidget(self.delete_button, 1, 0)
        buttons.addWidget(self.clear_button, 1, 1)
        card_layout.addLayout(buttons)
        card_layout.addStretch()
        main_layout.addWidget(form_card)

        # ----- right: search row + table (this side stretches when resized) -----
        right = QVBoxLayout()
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by roll number or name")
        self.search_input.setClearButtonEnabled(True)
        self.filter_combo = QComboBox()
        self.filter_combo.addItem(config.ALL_COURSES)
        self.filter_combo.addItems(config.COURSES)
        filter_row.addWidget(self.search_input, 3)
        filter_row.addWidget(self.filter_combo, 1)
        right.addLayout(filter_row)

        self.count_label = QLabel()
        self.count_label.setObjectName("hint")
        right.addWidget(self.count_label)

        self.table = QTableWidget()
        configure_table(self.table, HEADERS, stretch_column=1)
        right.addWidget(self.table)
        main_layout.addLayout(right, 1)

    # ------------------------------------------------------------
    # Signals and slots (event handling)
    # ------------------------------------------------------------
    def _connect_signals(self):
        self.add_button.clicked.connect(self.on_add)
        self.update_button.clicked.connect(self.on_update)
        self.delete_button.clicked.connect(self.on_delete)
        self.clear_button.clicked.connect(self.clear_form)
        self.search_input.textChanged.connect(self.refresh)
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.roll_input.textChanged.connect(lambda: self.message_label.clear())
        self.name_input.textChanged.connect(lambda: self.message_label.clear())

    def refresh(self):
        """Reload the table from the database using the current search and filter."""
        try:
            self.students = database.list_students(
                self.search_input.text(), self.filter_combo.currentText())
        except sqlite3.Error as error:
            show_db_error(self, error)
            return

        self.table.blockSignals(True)           # don't fire selection events while filling
        self.table.setRowCount(len(self.students))
        for row, s in enumerate(self.students):
            values = [s.roll, s.name, s.course, s.semester, s.gender,
                      s.contact or "-", "Yes" if s.scholarship else "No"]
            for col, value in enumerate(values):
                self.table.setItem(row, col, make_item(value, centered=col != 1))
        self.table.blockSignals(False)

        self.selected_roll = None
        self.roll_input.setEnabled(True)
        self._update_buttons()
        self.count_label.setText(f"{len(self.students)} student(s) shown")

    def on_selection_changed(self):
        """Copy the selected table row back into the form."""
        rows = self.table.selectionModel().selectedRows()
        if rows:
            student = self.students[rows[0].row()]
            self.selected_roll = student.roll
            self.roll_input.setText(student.roll)
            self.roll_input.setEnabled(False)           # the roll number is the primary key
            self.name_input.setText(student.name)
            self.course_combo.setCurrentText(student.course)
            self.semester_spin.setValue(student.semester)
            self._set_gender(student.gender)
            self.contact_input.setText(student.contact)
            self.scholarship_check.setChecked(student.scholarship)
            self.message_label.clear()
        else:
            self.selected_roll = None
            self.roll_input.setEnabled(True)
        self._update_buttons()

    def _update_buttons(self):
        selected = self.selected_roll is not None
        self.add_button.setEnabled(not selected)
        self.update_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def _selected_gender(self) -> str:
        button = self.gender_group.checkedButton()
        return button.text() if button else ""

    def _set_gender(self, gender: str):
        for button in self.gender_group.buttons():
            button.setChecked(button.text() == gender)

    def _read_form(self) -> Student:
        """Validate the form; raises logic.ValidationError with a friendly message."""
        return logic.validate_student(
            self.roll_input.text(), self.name_input.text(), self.course_combo.currentText(),
            self.semester_spin.value(), self._selected_gender(), self.contact_input.text(),
            self.scholarship_check.isChecked())

    def on_add(self):
        try:
            student = self._read_form()
            database.add_student(student)
        except logic.ValidationError as error:
            set_message(self.message_label, str(error), ok=False)
            return
        except database.DuplicateRollError:
            set_message(self.message_label,
                        f"Roll number {self.roll_input.text().strip().upper()} already exists.",
                        ok=False)
            return
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self.clear_form()
        self.refresh()
        set_message(self.message_label, f"Added {student.name}.")
        self.status_message.emit(f"Student {student.roll} added")

    def on_update(self):
        try:
            student = self._read_form()
            changed = database.update_student(student)
        except logic.ValidationError as error:
            set_message(self.message_label, str(error), ok=False)
            return
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        if not changed:
            set_message(self.message_label, "That student no longer exists.", ok=False)
        self.refresh()
        if changed:
            set_message(self.message_label, f"Updated {student.name}.")
            self.status_message.emit(f"Student {student.roll} updated")

    def on_delete(self):
        roll = self.selected_roll
        if roll is None:
            return
        if not ask_yes_no(self, "Confirm delete",
                          f"Delete student {roll} and all of their marks?\nThis cannot be undone."):
            return
        try:
            database.delete_student(roll)
        except sqlite3.Error as error:
            show_db_error(self, error)
            return
        self.clear_form()
        self.refresh()
        set_message(self.message_label, f"Deleted {roll}.")
        self.status_message.emit(f"Student {roll} deleted")

    def clear_form(self):
        self.table.clearSelection()
        self.selected_roll = None
        self.roll_input.setEnabled(True)
        self.roll_input.clear()
        self.name_input.clear()
        self.course_combo.setCurrentIndex(0)
        self.semester_spin.setValue(config.MIN_SEMESTER)
        self.gender_group.setExclusive(False)       # needed to un-check a radio button
        for button in self.gender_group.buttons():
            button.setChecked(False)
        self.gender_group.setExclusive(True)
        self.contact_input.clear()
        self.scholarship_check.setChecked(False)
        self.message_label.clear()
        self._update_buttons()

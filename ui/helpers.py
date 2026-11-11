"""Small shared UI helpers (message boxes, table cells, stat cards, table setup)."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView, QFrame, QHeaderView, QLabel, QMessageBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)


def show_warning(parent, title: str, text: str) -> None:
    QMessageBox.warning(parent, title, text)


def show_db_error(parent, error: Exception) -> None:
    QMessageBox.critical(parent, "Database Error",
                         f"Something went wrong while reading or saving data:\n\n{error}")


def ask_yes_no(parent, title: str, text: str) -> bool:
    """Yes/No question (default answer is No). Returns True for Yes."""
    answer = QMessageBox.question(
        parent, title, text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No)
    return answer == QMessageBox.StandardButton.Yes


def set_message(label: QLabel, text: str, ok: bool = True) -> None:
    """Show a green (success) or red (problem) line of feedback under a form."""
    color = "#16a34a" if ok else "#dc2626"
    label.setStyleSheet(f"color: {color}; font-weight: bold;")
    label.setText(text)


def make_item(text, centered: bool = True, color: str | None = None) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))
    if centered:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    if color:
        item.setForeground(QColor(color))
    return item


def configure_table(table: QTableWidget, headers: list[str], stretch_column: int = 1) -> None:
    """Apply the same look and behaviour to every table in the app."""
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(stretch_column, QHeaderView.ResizeMode.Stretch)


def make_stat_card(caption: str, color: str = "#2563eb"):
    """A white card with a big number and a caption. Returns (card, value_label)."""
    card = QFrame()
    card.setObjectName("card")
    layout = QVBoxLayout(card)
    value = QLabel("0")
    value.setObjectName("statValue")
    value.setStyleSheet(f"color: {color};")
    value.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title = QLabel(caption)
    title.setObjectName("statTitle")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(value)
    layout.addWidget(title)
    return card, value

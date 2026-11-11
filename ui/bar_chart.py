"""A small bar chart drawn by hand with QPainter (no extra libraries needed)."""

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QTextOption
from PyQt6.QtWidgets import QWidget


class BarChart(QWidget):
    """One vertical bar per label, the value above the bar and the label below it."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels: list[str] = []
        self.values: list[int] = []
        self.colors: list[str] = []
        self.setMinimumHeight(220)

    def set_data(self, labels, values, colors):
        self.labels, self.values, self.colors = list(labels), list(values), list(colors)
        self.update()                       # ask Qt to repaint

    def _text(self, painter, rect, text):
        painter.drawText(rect, text, QTextOption(Qt.AlignmentFlag.AlignCenter))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin_x, top, bottom = 12, 22, 28
        plot_w = self.width() - 2 * margin_x
        plot_h = self.height() - top - bottom
        if plot_w <= 0 or plot_h <= 0:
            painter.end()
            return
        base_y = top + plot_h

        painter.setPen(QPen(QColor("#d1d5db"), 1))
        painter.drawLine(QLineF(margin_x, base_y, margin_x + plot_w, base_y))

        if not any(self.values):
            painter.setPen(QColor("#6b7280"))
            self._text(painter, QRectF(margin_x, top, plot_w, plot_h), "No marks recorded yet")
            painter.end()
            return

        top_value = max(self.values)
        slot = plot_w / len(self.values)
        bar_w = min(slot * 0.6, 60)
        for i, (label, value, color) in enumerate(zip(self.labels, self.values, self.colors)):
            height = plot_h * value / top_value
            x = margin_x + i * slot + (slot - bar_w) / 2
            y = base_y - height

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawRoundedRect(QRectF(x, y, bar_w, height), 4, 4)

            painter.setPen(QColor("#374151"))
            self._text(painter, QRectF(x - 10, y - 20, bar_w + 20, 18), str(value))
            self._text(painter, QRectF(margin_x + i * slot, base_y + 4, slot, 20), label)
        painter.end()

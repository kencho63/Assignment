import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Hello PyQt6")
layout = QVBoxLayout(window)
label = QLabel("Hello!")
button = QPushButton("Click me")
button.clicked.connect(lambda: label.setText("Button clicked!"))   # signal -> slot
layout.addWidget(label)
layout.addWidget(button)
window.show()
sys.exit(app.exec())

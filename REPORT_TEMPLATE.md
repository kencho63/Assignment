# Report template (12-20 pages PDF) - write each part in your own words

## 1. Title page
Project name (StudentSys), your name, roll number, course, date.

## 2. Abstract (~150 words) - write this LAST
What the system does + "built with PyQt6 and SQLite".

## 3. Introduction
Problem statement (how are student records managed now?), scope, target users (teachers, admin staff).

## 4. Framework study (Part A)
### A1 Profiles (1/2-1 page each): PyQt/PySide, Kivy, Tkinter, + wxPython (or other)
Origin/maintainer | underlying toolkit | licence (PyQt GPL/commercial vs PySide LGPL) | platforms | widget richness | how UI is defined (code / Qt Designer .ui / KV) | typical apps
### A2 Comparison matrix (rows = frameworks)
| Framework | Licence | Platforms | Widget set | Layout system | Event/signal model | Styling | Designer tooling | Packaging | Learning curve | Community | Best for |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PyQt6 | | | | | | | | | | | |
| Kivy | | | | | | | | | | | |
| Tkinter | | | | | | | | | | | |
| wxPython | | | | | | | | | | | |
### A3 Hello-world evidence
Code + screenshot for partA/hello_pyqt.py, hello_kivy.py, hello_tkinter.py; then 3-4 sentences on imports, boilerplate, event wiring.
### A4 Recommendation (~250 words)
Cite >= 3 matrix criteria; name one situation where another framework wins.

## 5. System design
- Feature list (see README)
- Wireframe per screen: Dashboard, Students, Marks, Reports (hand-drawn photo OK)
- Widget-and-layout plan (which widget in which layout)
- Data design:
  - students(roll PK, name, course, semester, gender, contact, scholarship)
  - marks(id PK, roll FK -> students ON DELETE CASCADE, subject, score, max_score, UNIQUE(roll, subject))
- Architecture diagram: main.py -> ui/* (UI layer) -> student_logic.py (rules) + database.py (SQLite) -> students.db

## 6. Implementation (10-20 line snippets, annotated)
One short subsection per requirement. Suggested snippets:
- Main window + menu: ui/main_window.py `__init__`, `_create_menu_bar`
- Widgets (8+): ui/students_page.py `_build_ui`
- Layouts: QHBoxLayout / QVBoxLayout / QFormLayout / QGridLayout in `_build_ui`  (REQUIRED: layout example)
- Signals/slots: ui/students_page.py `_connect_signals` + `on_selection_changed`  (REQUIRED: signal/slot example)
- Dialog: `ask_yes_no` (confirm delete), `QFileDialog` (export), About
- Validation: student_logic.py `validate_student` + the try/except in `on_add`
- Persistence: database.py `connect`, `add_student`
- Styling: ui/styles.py
- UI/logic separation: explain why student_logic.py has no PyQt imports (it is unit-testable)

## 7. Testing - record ACTUAL results honestly
Automated: `python -m unittest discover -s tests -v` (paste output). Manual table:
| # | Action | Input | Expected | Actual | Pass/Fail |
|---|---|---|---|---|---|
| 1 | Add valid student | CS011, Sita Rai, Business, sem 2, Female | Appears in table, green message | | |
| 2 | Add with empty roll | (blank) | Red message "Roll number is required" | | |
| 3 | Add duplicate roll | CS001 | "already exists" message | | |
| 4 | Invalid name | Bad123 | Red name message | | |
| 5 | Invalid contact | 12ab | Red contact message | | |
| 6 | No gender selected | - | "Please select a gender" | | |
| 7 | Search | "tashi" | Table filters live | | |
| 8 | Select row, edit, Update | change semester | Row updated | | |
| 9 | Delete -> No / Yes | select row | No keeps, Yes removes (and its marks) | | |
| 10 | Marks above maximum | 120 out of 100 | Red message | | |
| 11 | Duplicate subject for same student | Programming again | Duplicate message | | |
| 12 | Close and reopen app | - | Data still there | | |
| 13 | Resize window | drag corner | Layout stretches | | |
| 14 | Export CSV | Reports tab | File saved with filtered rows | | |

## 8. Screenshots (name/roll visible in title or About)
Dashboard, Students, Marks, Reports, a validation error, the delete confirmation, About.

## 9. Challenges & reflection
3 specific problems and fixes; what you'd do differently; would you pick PyQt again?

## 10. References
Official docs + EVERY AI-assisted portion (state that the code was generated with Claude and reviewed by you).

---
# Requirement checklist
- [ ] Main window: title, size, menu bar         -> ui/main_window.py
- [ ] 8+ widget types                            -> QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QRadioButton, QCheckBox, QPushButton, QTableWidget, QProgressBar
- [ ] 2+ layouts, resizes gracefully             -> QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout
- [ ] 5+ handled events                          -> ui/students_page.py `_connect_signals` (10+)
- [ ] Dialog/popup                               -> confirm delete, file save, About, error boxes
- [ ] Validation, no crashes                     -> student_logic.py + try/except in every slot
- [ ] Persistence                                -> SQLite data/students.db
- [ ] Styling                                    -> ui/styles.py (QSS)
- [ ] UI/logic split                             -> ui/ vs student_logic.py vs database.py
- [ ] Sample data in data/students.db            -> included
- [ ] README with install/run steps              -> included
- [ ] Part A: 3 hello-world programs + screenshots
- [ ] Stretch: search/filter (done), chart (done), CSV export (done); still open: PyInstaller size/startup time, 2nd-framework screen

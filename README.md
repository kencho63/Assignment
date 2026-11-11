# StudentSys - Student Record Manager

A desktop application built with **Python 3.10+** and **PyQt6**, storing its data in **SQLite**.
Unit V assignment - Part B (Topic 5.3), project idea 1: *Student record manager*.

## Features
- **Dashboard:** student count, marks recorded, class average, pass rate, scholarships; bar chart of students per grade; top 5 students; quick buttons
- **Students:** add, edit, delete; live search by roll number or name; filter by course; validation with friendly messages
- **Marks:** choose a student, add subject marks (score out of N); see their average, grade and a progress bar
- **Reports:** every student's average and grade; search + course + grade filters; class average and pass rate; export to CSV
- Menu bar with shortcuts (Ctrl+1 ... Ctrl+4 switch tabs, F1 = About), confirmation before deleting

Grading rules (A >= 80, B >= 70, C >= 60, D >= 50, otherwise F; pass mark 50%) are in `config.py`.

## Install and run

```bash
# 1. open a terminal in this folder (the one that contains main.py)

# 2. create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# 3. install the dependency
pip install -r requirements.txt

# 4. start the app
python main.py
```

The database `data/students.db` is created automatically on first run with 10 students and
sample marks (one student has no marks yet). A ready-made copy is included.

**Before taking screenshots:** open `config.py` and set `STUDENT_NAME` and `ROLL_NO`.
They appear in the window title and in *Help > About*.

## Run the tests
```bash
python -m unittest discover -s tests -v
```
(13 tests for validation, grading and the database layer. They use a temporary database.)

## Project structure
| File | Layer | Purpose |
|---|---|---|
| `main.py` | entry | creates the app, applies the stylesheet, opens the window |
| `config.py` | settings | name/roll number, courses, grading rules, paths |
| `models.py` | data | `Student` and `Mark` dataclasses |
| `student_logic.py` | logic | validation, grades, statistics (no PyQt, no SQL) |
| `database.py` | data | all SQLite code (tables, CRUD, averages) |
| `ui/styles.py` | UI | Qt stylesheet (QSS) |
| `ui/main_window.py` | UI | menu bar, tabs, About dialog |
| `ui/*_page.py` | UI | one file per tab |
| `ui/bar_chart.py` | UI | hand-drawn bar chart (QPainter) |
| `tests/` | tests | unit tests |
| `partA/` | Part A | hello-world programs: PyQt6, Kivy, Tkinter |

## AI assistance disclosure
> Edit this section honestly before submitting. The code in this project was generated with
> Claude (Anthropic). I have read it, understand it and can modify it.

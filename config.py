"""Application-wide settings.

>>> Change STUDENT_NAME and ROLL_NO before taking your report screenshots. <<<
They appear in the window title and in Help > About.
"""

from pathlib import Path

APP_NAME = "StudentSys"
STUDENT_NAME = "Your Name"
ROLL_NO = "Your Roll No"
COURSE_NAME = "Unit V - Exploring GUI Frameworks (PyQt6)"

# Paths are built from this file's location, so nothing is hard-coded.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "students.db"

# Academic rules
COURSES = ("Computer Science", "Electronics", "Civil Engineering", "Business")
ALL_COURSES = "All Courses"
GENDERS = ("Male", "Female", "Other")
MIN_SEMESTER, MAX_SEMESTER = 1, 8
DEFAULT_MAX_SCORE = 100
PASS_PERCENT = 50.0
GRADE_BANDS = ((80, "A"), (70, "B"), (60, "C"), (50, "D"))   # anything lower is F
GRADES = ("A", "B", "C", "D", "F")
NO_GRADE = "N/A"
ALL_GRADES = "All Grades"
GRADE_COLORS = {"A": "#16a34a", "B": "#0891b2", "C": "#d97706",
                "D": "#ea580c", "F": "#dc2626", NO_GRADE: "#6b7280"}

# Tab positions in the main window (used by the dashboard shortcut buttons)
TAB_DASHBOARD, TAB_STUDENTS, TAB_MARKS, TAB_REPORTS = 0, 1, 2, 3

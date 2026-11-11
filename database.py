"""Data layer: SQLite storage for students and their marks. No PyQt code here."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

import config
from models import Mark, Student

db_path = Path(config.DB_PATH)          # the tests point this at a temporary file


class DuplicateRollError(Exception):
    """A student with this roll number already exists."""


class DuplicateMarkError(Exception):
    """This student already has marks for this subject."""


SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    roll        TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    course      TEXT NOT NULL,
    semester    INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    gender      TEXT NOT NULL,
    contact     TEXT NOT NULL DEFAULT '',
    scholarship INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS marks (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    roll      TEXT NOT NULL REFERENCES students(roll) ON DELETE CASCADE,
    subject   TEXT NOT NULL,
    score     REAL NOT NULL,
    max_score INTEGER NOT NULL CHECK (max_score > 0),
    CHECK (score >= 0 AND score <= max_score),
    UNIQUE (roll, subject)
);
"""

SAMPLE_STUDENTS = [
    ("CS001", "Tashi Dorji", "Computer Science", 3, "Male", "17123456", True),
    ("CS002", "Pema Lhamo", "Computer Science", 3, "Female", "17234567", False),
    ("CS003", "Karma Wangchuk", "Computer Science", 5, "Male", "", False),
    ("EL001", "Sonam Choden", "Electronics", 2, "Female", "77345678", True),
    ("EL002", "Dechen Zangmo", "Electronics", 4, "Female", "17456789", False),
    ("CV001", "Jigme Tenzin", "Civil Engineering", 6, "Male", "77567890", False),
    ("CV002", "Yeshey Pelden", "Civil Engineering", 2, "Other", "", False),
    ("BU001", "Choki Dema", "Business", 1, "Female", "17678901", True),
    ("BU002", "Ugyen Norbu", "Business", 3, "Male", "77789012", False),
    ("BU003", "Kinley Om", "Business", 1, "Female", "", False),      # no marks yet
]
SAMPLE_MARKS = {
    "CS001": {"Programming": 88, "Mathematics": 79, "Databases": 91},
    "CS002": {"Programming": 72, "Mathematics": 65, "Databases": 70},
    "CS003": {"Programming": 55, "Mathematics": 48, "Databases": 60},
    "EL001": {"Circuits": 93, "Mathematics": 85},
    "EL002": {"Circuits": 61, "Mathematics": 58},
    "CV001": {"Surveying": 45, "Mechanics": 38},
    "CV002": {"Surveying": 66, "Mechanics": 71},
    "BU001": {"Accounting": 84, "Economics": 90},
    "BU002": {"Accounting": 52, "Economics": 49},
}


@contextmanager
def connect():
    """Open the database, commit on success, roll back on error, always close."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")      # needed for ON DELETE CASCADE
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(seed: bool = True) -> None:
    """Create tables; on a brand-new database also insert the sample data."""
    with connect() as conn:
        conn.executescript(SCHEMA)
        empty = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0
        if seed and empty:
            conn.executemany("INSERT INTO students VALUES (?,?,?,?,?,?,?)", SAMPLE_STUDENTS)
            for roll, subjects in SAMPLE_MARKS.items():
                for subject, score in subjects.items():
                    conn.execute(
                        "INSERT INTO marks (roll, subject, score, max_score) VALUES (?,?,?,100)",
                        (roll, subject, score))


# ---------------------------------------------------------------- students
def _to_student(row) -> Student:
    return Student(row[0], row[1], row[2], row[3], row[4], row[5], bool(row[6]))


def list_students(search: str = "", course: str = config.ALL_COURSES) -> list[Student]:
    sql = "SELECT roll, name, course, semester, gender, contact, scholarship FROM students WHERE 1=1"
    params: list = []
    if search.strip():
        like = f"%{search.strip()}%"
        sql += " AND (roll LIKE ? OR name LIKE ?)"
        params += [like, like]
    if course != config.ALL_COURSES:
        sql += " AND course = ?"
        params.append(course)
    sql += " ORDER BY roll"
    with connect() as conn:
        return [_to_student(r) for r in conn.execute(sql, params).fetchall()]


def add_student(s: Student) -> None:
    try:
        with connect() as conn:
            conn.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?)",
                         (s.roll, s.name, s.course, s.semester, s.gender, s.contact,
                          int(s.scholarship)))
    except sqlite3.IntegrityError:
        raise DuplicateRollError(s.roll) from None


def update_student(s: Student) -> bool:
    """Return True if a row was changed."""
    with connect() as conn:
        cur = conn.execute(
            "UPDATE students SET name=?, course=?, semester=?, gender=?, contact=?, "
            "scholarship=? WHERE roll=?",
            (s.name, s.course, s.semester, s.gender, s.contact, int(s.scholarship), s.roll))
        return cur.rowcount > 0


def delete_student(roll: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM students WHERE roll = ?", (roll,))   # marks cascade


# ------------------------------------------------------------------- marks
def list_marks(roll: str) -> list[Mark]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, roll, subject, score, max_score FROM marks WHERE roll=? ORDER BY subject",
            (roll,)).fetchall()
    return [Mark(*r) for r in rows]


def add_mark(roll: str, subject: str, score: float, max_score: int) -> None:
    try:
        with connect() as conn:
            conn.execute("INSERT INTO marks (roll, subject, score, max_score) VALUES (?,?,?,?)",
                         (roll, subject, score, max_score))
    except sqlite3.IntegrityError:
        raise DuplicateMarkError(subject) from None


def delete_mark(mark_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM marks WHERE id = ?", (mark_id,))


def count_marks() -> int:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM marks").fetchone()[0]


def student_averages() -> list[tuple]:
    """(roll, name, course, scholarship, subject_count, average_percent or None)."""
    with connect() as conn:
        return conn.execute(
            "SELECT s.roll, s.name, s.course, s.scholarship, COUNT(m.id), "
            "AVG(m.score * 100.0 / m.max_score) "
            "FROM students s LEFT JOIN marks m ON m.roll = s.roll "
            "GROUP BY s.roll ORDER BY s.roll").fetchall()

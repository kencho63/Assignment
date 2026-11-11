"""Run from the project folder:  python -m unittest discover -s tests -v"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import database
import student_logic as logic
from models import Student


def valid_args(**changes):
    args = dict(roll="cs010", name="  Tashi   Dorji ", course="Business", semester=2,
                gender="Male", contact="17123456", scholarship=False)
    args.update(changes)
    return args


class ValidationTests(unittest.TestCase):
    def test_valid_student_is_cleaned(self):
        s = logic.validate_student(**valid_args())
        self.assertEqual((s.roll, s.name), ("CS010", "Tashi Dorji"))

    def test_invalid_students(self):
        bad = [dict(roll=""), dict(roll="a b!"), dict(name=""), dict(name="Bad123"),
               dict(course="Magic"), dict(semester=9), dict(gender=""),
               dict(contact="12ab"), dict(contact="123")]
        for changes in bad:
            with self.subTest(changes=changes):
                with self.assertRaises(logic.ValidationError):
                    logic.validate_student(**valid_args(**changes))

    def test_empty_contact_is_allowed(self):
        self.assertEqual(logic.validate_student(**valid_args(contact="")).contact, "")

    def test_marks_validation(self):
        self.assertEqual(logic.validate_mark(" Maths ", 55.5, 100), ("Maths", 55.5, 100))
        for args in [("", 5, 100), ("Maths", -1, 100), ("Maths", 101, 100), ("Maths", 5, 0)]:
            with self.subTest(args=args):
                with self.assertRaises(logic.ValidationError):
                    logic.validate_mark(*args)


class GradeTests(unittest.TestCase):
    def test_grade_boundaries(self):
        cases = {100: "A", 80: "A", 79.9: "B", 70: "B", 60: "C", 50: "D", 49.9: "F", 0: "F"}
        for percent, grade in cases.items():
            self.assertEqual(logic.grade_for(percent), grade, percent)

    def test_distribution_and_summary(self):
        self.assertEqual(logic.grade_distribution([90, 85, 40])["A"], 2)
        summary = logic.class_summary([90, 40])
        self.assertEqual((summary["average"], summary["pass_rate"]), (65.0, 50.0))
        self.assertEqual(logic.class_summary([])["graded"], 0)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        database.db_path = Path(self.tmp.name) / "test.db"
        database.init_db(seed=False)
        self.student = logic.validate_student(**valid_args())

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_list_search_filter(self):
        database.add_student(self.student)
        self.assertEqual(len(database.list_students()), 1)
        self.assertEqual(len(database.list_students("tashi")), 1)
        self.assertEqual(len(database.list_students("nobody")), 0)
        self.assertEqual(len(database.list_students("", "Civil Engineering")), 0)

    def test_duplicate_roll_rejected(self):
        database.add_student(self.student)
        with self.assertRaises(database.DuplicateRollError):
            database.add_student(self.student)

    def test_update_and_delete(self):
        database.add_student(self.student)
        self.student.name = "Changed Name"
        self.assertTrue(database.update_student(self.student))
        self.assertEqual(database.list_students()[0].name, "Changed Name")
        database.delete_student(self.student.roll)
        self.assertEqual(database.list_students(), [])
        self.assertFalse(database.update_student(self.student))

    def test_marks_and_cascade_delete(self):
        database.add_student(self.student)
        database.add_mark("CS010", "Maths", 80, 100)
        database.add_mark("CS010", "Physics", 60, 100)
        with self.assertRaises(database.DuplicateMarkError):
            database.add_mark("CS010", "Maths", 70, 100)
        self.assertEqual(database.student_averages()[0][5], 70.0)
        database.delete_student("CS010")
        self.assertEqual(database.count_marks(), 0)

    def test_student_without_marks_has_no_average(self):
        database.add_student(self.student)
        self.assertIsNone(database.student_averages()[0][5])

    def test_data_persists_between_connections(self):
        database.add_student(self.student)
        self.assertEqual(database.list_students()[0].roll, "CS010")   # fresh connection

    def test_seed_data(self):
        database.db_path = Path(self.tmp.name) / "seeded.db"
        database.init_db()
        self.assertEqual(len(database.list_students()), 10)


if __name__ == "__main__":
    unittest.main()

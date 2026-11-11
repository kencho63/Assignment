"""Business rules: validation, grading and statistics. Pure Python - no PyQt, no SQL."""

import re

import config
from models import Student


class ValidationError(ValueError):
    """Raised with a user-friendly message when input is not acceptable."""


ROLL_PATTERN = re.compile(r"^[A-Za-z0-9-]{2,20}$")


def validate_student(roll, name, course, semester, gender, contact, scholarship) -> Student:
    """Check every field and return a clean Student, or raise ValidationError."""
    roll = roll.strip().upper()
    name = " ".join(name.split())          # collapse repeated spaces
    contact = contact.strip()

    if not roll:
        raise ValidationError("Roll number is required.")
    if not ROLL_PATTERN.match(roll):
        raise ValidationError("Roll number: 2-20 letters, digits or '-' only.")
    if not name:
        raise ValidationError("Name is required.")
    if len(name) < 2 or not all(ch.isalpha() or ch in " .'-" for ch in name):
        raise ValidationError("Name must contain letters only (no digits or symbols).")
    if course not in config.COURSES:
        raise ValidationError("Please choose a course from the list.")
    if not config.MIN_SEMESTER <= semester <= config.MAX_SEMESTER:
        raise ValidationError(
            f"Semester must be between {config.MIN_SEMESTER} and {config.MAX_SEMESTER}.")
    if gender not in config.GENDERS:
        raise ValidationError("Please select a gender.")
    if contact and not (contact.isdigit() and 7 <= len(contact) <= 12):
        raise ValidationError("Contact must be 7-12 digits (numbers only) or left empty.")
    return Student(roll, name, course, semester, gender, contact, bool(scholarship))


def validate_mark(subject, score, max_score):
    """Return (subject, score, max_score) cleaned, or raise ValidationError."""
    subject = " ".join(subject.split())
    if not subject:
        raise ValidationError("Subject name is required.")
    if len(subject) > 40:
        raise ValidationError("Subject name is too long (40 characters maximum).")
    if not 1 <= max_score <= 1000:
        raise ValidationError("'Out of' must be between 1 and 1000.")
    if score < 0:
        raise ValidationError("Score cannot be negative.")
    if score > max_score:
        raise ValidationError(f"Score ({score:g}) cannot be higher than the maximum ({max_score}).")
    return subject, float(score), int(max_score)


def percentage(score: float, max_score: int) -> float:
    return score * 100.0 / max_score


def grade_for(percent: float) -> str:
    for threshold, letter in config.GRADE_BANDS:
        if percent >= threshold:
            return letter
    return "F"


def grade_distribution(percents) -> dict:
    """Count how many students fall in each grade."""
    counts = {grade: 0 for grade in config.GRADES}
    for p in percents:
        counts[grade_for(p)] += 1
    return counts


def class_summary(percents) -> dict:
    """Average and pass rate for a list of percentages."""
    if not percents:
        return {"graded": 0, "average": 0.0, "pass_rate": 0.0}
    passed = sum(1 for p in percents if p >= config.PASS_PERCENT)
    return {"graded": len(percents),
            "average": sum(percents) / len(percents),
            "pass_rate": passed * 100.0 / len(percents)}

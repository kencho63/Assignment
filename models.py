"""Plain data containers shared by the logic, data and UI layers."""

from dataclasses import dataclass


@dataclass
class Student:
    roll: str
    name: str
    course: str
    semester: int
    gender: str
    contact: str
    scholarship: bool


@dataclass
class Mark:
    id: int
    roll: str
    subject: str
    score: float
    max_score: int

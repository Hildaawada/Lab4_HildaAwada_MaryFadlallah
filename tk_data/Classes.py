"""
Classes module for the School Management System
===============================================

This module defines the core data models: ``Person``, ``Student``, ``Instructor``, and ``Courses``.
It enforces validation rules (age, email format) and provides helper methods
for course registration and instructor assignment.

Author: Hilda Awada & Mary Fadlallah
Version: 1.0
License: MIT
"""

from dataclasses import dataclass, field
from typing import List
import re

# Regex for validating email format
_EMAIL_Check = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Person:
    """
    Represents a base person with name, age, and email.

    :param Fullname: Full name of the person
    :type Fullname: str
    :param Age: Age of the person (must be non-negative)
    :type Age: int
    :param _email: Email address (validated against regex)
    :type _email: str
    """

    Fullname: str
    Age: int
    _email: str

    def __post_init__(self):
        """Validate age and email format after initialization."""
        if self.Age < 0:
            raise ValueError("Invalid Age Number")
        if not _EMAIL_Check.match(self._email):
            raise ValueError("The Email Format is Invalid")

    @property
    def email(self) -> str:
        """
        Get the email address.

        :return: Email address
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, new_email: str):
        """
        Set a new email after validating its format.

        :param new_email: New email address
        :type new_email: str
        :raises ValueError: If email format is invalid
        """
        if not _EMAIL_Check.match(new_email):
            raise ValueError("The Email Format is Invalid")
        self._email = new_email

    def introducing(self) -> str:
        """
        Return an introduction message.

        :return: Introduction string
        :rtype: str
        """
        return f"Hi, this is {self.Fullname}, I'm {self.Age} years old, you can reach out to my email: {self._email}"


@dataclass
class Courses:
    """
    Represents a course in the system.

    :param Course_ID: Unique identifier for the course
    :type Course_ID: str
    :param Course_Title: Name/title of the course
    :type Course_Title: str
    :param instructor_id: ID of the assigned instructor (optional)
    :type instructor_id: str | None
    :param Enrolled_StudentIDs: List of enrolled student IDs
    :type Enrolled_StudentIDs: List[str]
    """

    Course_ID: str
    Course_Title: str
    instructor_id: str | None = None
    Enrolled_StudentIDs: List[str] = field(default_factory=list)

    def add_new_student(self, student_ID: str) -> None:
        """
        Enroll a student in the course if not already enrolled.

        :param student_ID: Unique ID of the student
        :type student_ID: str
        """
        if student_ID not in self.Enrolled_StudentIDs:
            self.Enrolled_StudentIDs.append(student_ID)


@dataclass
class Student(Person):
    """
    Represents a student, inheriting from Person.

    :param student_ID: Unique identifier for the student
    :type student_ID: str
    :param registered_courses_ids: List of registered course IDs
    :type registered_courses_ids: List[str]
    """

    student_ID: str
    registered_courses_ids: List[str] = field(default_factory=list)

    def register_course(self, course: Courses) -> None:
        """
        Register the student for a course and update both sides.

        :param course: Course object
        :type course: Courses
        """
        if course.Course_ID not in self.registered_courses_ids:
            self.registered_courses_ids.append(course.Course_ID)
            course.add_new_student(self.student_ID)


@dataclass
class Instructor(Person):
    """
    Represents an instructor, inheriting from Person.

    :param instructor_id: Unique identifier for the instructor
    :type instructor_id: str
    :param assigned_courses_ids: List of assigned course IDs
    :type assigned_courses_ids: List[str]
    """

    instructor_id: str
    assigned_courses_ids: List[str] = field(default_factory=list)

    def assign_course(self, course: Courses) -> None:
        """
        Assign the instructor to a course and update both sides.

        :param course: Course object
        :type course: Courses
        """
        if course.Course_ID not in self.assigned_courses_ids:
            self.assigned_courses_ids.append(course.Course_ID)
            course.instructor_id = self.instructor_id

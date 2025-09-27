"""
School Management System - Classes Module
=========================================

This module defines the core data models used in the School Management System:
    - Person
    - Student
    - Instructor
    - Courses

These classes enforce validation (age, email), maintain relationships
between students, instructors, and courses, and provide helper methods
for registration and assignment.

:author: Your Name
:project: School Management System (Lab 2)
:version: 1.0.0
:copyright: (c) 2025 Your University
"""

from dataclasses import dataclass, field
from typing import List
import re

# Email validation pattern (e.g., "example@domain.com")
_EMAIL_Check = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Person:
    """
    Base class for people in the system.

    :param Fullname: Full name of the person
    :type Fullname: str
    :param Age: Age of the person (must be non-negative)
    :type Age: int
    :param _email: Email of the person (validated on creation and update)
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
        Get the email address of the person.

        :return: Valid email address
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, new_email: str):
        """
        Update the email address with validation.

        :param new_email: The new email to set
        :type new_email: str
        :raises ValueError: If email format is invalid
        """
        if not _EMAIL_Check.match(new_email):
            raise ValueError("The Email Format is Invalid")
        self._email = new_email

    def introducing(self) -> str:
        """
        Return a string introduction for the person.

        :return: Introduction string
        :rtype: str
        """
        return f"Hi, this is {self.Fullname}, I'm {self.Age} years old, you can reach out to my email: {self._email}"


@dataclass
class Courses:
    """
    Represents a course offered by the school.

    :param Course_ID: Unique course identifier
    :type Course_ID: str
    :param Course_Title: Title of the course
    :type Course_Title: str
    :param instructor_id: Assigned instructor ID (optional)
    :type instructor_id: str | None
    :param Enrolled_StudentIDs: List of enrolled student IDs
    :type Enrolled_StudentIDs: list[str]
    """

    Course_ID: str
    Course_Title: str
    instructor_id: str | None = None
    Enrolled_StudentIDs: List[str] = field(default_factory=list)

    def add_new_student(self, student_ID: str):
        """
        Add a student to this course.

        :param student_ID: Unique student ID
        :type student_ID: str
        """
        if student_ID not in self.Enrolled_StudentIDs:
            self.Enrolled_StudentIDs.append(student_ID)


@dataclass
class Student(Person):
    """
    Represents a student in the school.

    Inherits from Person and adds:
      - student_ID
      - registered courses

    :param student_ID: Unique student identifier
    :type student_ID: str
    :param registered_courses_ids: List of registered course IDs
    :type registered_courses_ids: list[str]
    """

    student_ID: str
    registered_courses_ids: List[str] = field(default_factory=list)

    def register_course(self, course: Courses):
        """
        Register the student in a course and update both sides.

        :param course: Course object to register in
        :type course: Courses
        """
        if course.Course_ID not in self.registered_courses_ids:
            self.registered_courses_ids.append(course.Course_ID)
            course.add_new_student(self.student_ID)


@dataclass
class Instructor(Person):
    """
    Represents an instructor in the school.

    Inherits from Person and adds:
      - instructor_id
      - assigned courses

    :param instructor_id: Unique instructor identifier
    :type instructor_id: str
    :param assigned_courses_ids: List of assigned course IDs
    :type assigned_courses_ids: list[str]
    """

    instructor_id: str
    assigned_courses_ids: List[str] = field(default_factory=list)

    def assign_course(self, course: Courses):
        """
        Assign this instructor to a course.

        Updates both the instructor and the course.

        :param course: Course object to assign
        :type course: Courses
        """
        if course.Course_ID not in self.assigned_courses_ids:
            self.assigned_courses_ids.append(course.Course_ID)
            course.instructor_id = self.instructor_id

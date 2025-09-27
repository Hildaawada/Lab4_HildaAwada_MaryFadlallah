"""
School Management System - CSV Module
=====================================

This module provides utility functions to save and load students,
instructors, and courses to/from CSV files.

It ensures smooth import/export for persistence and data sharing.

:author: Hilda Awada
:project: School Management System 
:version: 1.0.0
:copyright: (c) 2025 Your University
"""

import csv
from typing import List
from Classes import Student, Courses, Instructor


# ----------------------------------------------------------------------
# SAVE FUNCTIONS
# ----------------------------------------------------------------------

def Save_students(path: str, Students_List: List[Student]) -> None:
    """
    Save all students to a CSV file.

    :param path: File path where to save (e.g., 'students.csv')
    :type path: str
    :param Students_List: List of Student objects
    :type Students_List: list[Student]
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "age", "email", "registered_courses"])
        for s in Students_List:
            writer.writerow([
                s.student_ID,
                s.Fullname,
                s.Age,
                s.email,  # uses Person.email property
                ";".join(s.registered_courses_ids)  # flatten list into string
            ])


def save_courses(path: str, courses: List[Courses]) -> None:
    """
    Save all courses to a CSV file.

    :param path: File path where to save (e.g., 'courses.csv')
    :type path: str
    :param courses: List of Course objects
    :type courses: list[Courses]
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["course_id", "course_name", "instructor_id", "enrolled_students"])
        for c in courses:
            writer.writerow([
                c.Course_ID,
                c.Course_Title,
                c.instructor_id if c.instructor_id else "",
                ";".join(c.Enrolled_StudentIDs)
            ])


def save_instructors(path: str, instructors: List[Instructor]) -> None:
    """
    Save all instructors to a CSV file.

    :param path: File path where to save (e.g., 'instructors.csv')
    :type path: str
    :param instructors: List of Instructor objects
    :type instructors: list[Instructor]
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["instructor_id", "name", "age", "email", "assigned_courses"])
        for i in instructors:
            writer.writerow([
                i.instructor_id,
                i.Fullname,
                i.Age,
                i.email,
                ";".join(i.assigned_courses_ids)
            ])


# ----------------------------------------------------------------------
# LOAD FUNCTIONS
# ----------------------------------------------------------------------

def load_students(path: str) -> List[Student]:
    """
    Load students from a CSV file.

    :param path: Path to CSV file (e.g., 'students.csv')
    :type path: str
    :return: List of Student objects
    :rtype: list[Student]
    """
    students_list: List[Student] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registered = row["registered_courses"].split(";") if row["registered_courses"] else []
            s = Student(
                Fullname=row["name"],
                Age=int(row["age"]),
                _email=row["email"],
                student_ID=row["student_id"],
                registered_courses_ids=registered
            )
            students_list.append(s)
    return students_list


def load_courses(path: str) -> List[Courses]:
    """
    Load courses from a CSV file.

    :param path: Path to CSV file (e.g., 'courses.csv')
    :type path: str
    :return: List of Courses objects
    :rtype: list[Courses]
    """
    courses_list: List[Courses] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            enrolled = row["enrolled_students"].split(";") if row["enrolled_students"] else []
            c = Courses(
                Course_ID=row["course_id"],
                Course_Title=row["course_name"],
                instructor_id=row["instructor_id"] or None,
                Enrolled_StudentIDs=enrolled
            )
            courses_list.append(c)
    return courses_list


def load_instructors(path: str) -> List[Instructor]:
    """
    Load instructors from a CSV file.

    :param path: Path to CSV file (e.g., 'instructors.csv')
    :type path: str
    :return: List of Instructor objects
    :rtype: list[Instructor]
    """
    instructors_list: List[Instructor] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            assigned = row["assigned_courses"].split(";") if row["assigned_courses"] else []
            ins = Instructor(
                Fullname=row["name"],
                Age=int(row["age"]),
                _email=row["email"],
                instructor_id=row["instructor_id"],
                assigned_courses_ids=assigned
            )
            instructors_list.append(ins)
    return instructors_list

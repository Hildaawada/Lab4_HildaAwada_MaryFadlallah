"""
School Management System - Database Module
==========================================

This module handles all interactions with the SQLite database
for the School Management System. It provides CRUD operations
for students, instructors, and courses, as well as registration,
assignment, searching, and backup.

:author: Hilda Awada
:project: School Management System (Lab 2 - PyQt)
:version: 1.0.0
:copyright: (c) 2025 Hilda Awada
"""

import sqlite3, shutil, os
from typing import Optional, List, Dict

DB_PATH = "school.db"


def connect(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create and return a SQLite connection with foreign keys enabled.

    :param db_path: Path to the SQLite database file, defaults to DB_PATH
    :type db_path: str, optional
    :return: SQLite connection object
    :rtype: sqlite3.Connection
    """
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize the database with required tables.

    This function creates the following tables if they do not exist:
    - students
    - instructors
    - courses
    - registrations

    :param db_path: Path to the SQLite database file, defaults to DB_PATH
    :type db_path: str, optional
    """
    with connect(db_path) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            age          INTEGER NOT NULL CHECK(age >= 0),
            email        TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            age           INTEGER NOT NULL CHECK(age >= 0),
            email         TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS courses (
            course_id     TEXT PRIMARY KEY,
            course_name   TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS registrations (
            student_id TEXT NOT NULL,
            course_id  TEXT NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
        );
        """)

# ----------------------------------------------------------------------
# STUDENTS
# ----------------------------------------------------------------------

def create_student(student_id: str, name: str, age: int, email: str) -> None:
    """Insert a new student into the database.

    :param student_id: Unique identifier for the student
    :type student_id: str
    :param name: Student's full name
    :type name: str
    :param age: Student's age
    :type age: int
    :param email: Student's email
    :type email: str
    :raises sqlite3.IntegrityError: If student_id already exists
    """
    with connect() as con:
        con.execute(
            "INSERT INTO students(student_id, name, age, email) VALUES(?,?,?,?)",
            (student_id.strip(), name.strip(), age, email.strip())
        )


def get_students() -> List[sqlite3.Row]:
    """Retrieve all students and their registered courses.

    :return: List of students with concatenated course IDs
    :rtype: list[sqlite3.Row]
    """
    with connect() as con:
        return list(con.execute("""
            SELECT s.*,
                   IFNULL(GROUP_CONCAT(r.course_id, ','), '') AS courses
            FROM students s
            LEFT JOIN registrations r ON r.student_id = s.student_id
            GROUP BY s.student_id
            ORDER BY s.student_id
        """))


def update_student(student_id: str, name: str, age: int, email: str, new_id: Optional[str] = None) -> None:
    """Update student details, optionally changing the student ID.

    :param student_id: Current student ID
    :type student_id: str
    :param name: Updated name
    :type name: str
    :param age: Updated age
    :type age: int
    :param email: Updated email
    :type email: str
    :param new_id: Optional new student ID
    :type new_id: str, optional
    """
    with connect() as con:
        if new_id and new_id != student_id:
            con.execute("UPDATE students SET student_id=? WHERE student_id=?", (new_id, student_id))
            con.execute("UPDATE registrations SET student_id=? WHERE student_id=?", (new_id, student_id))
            student_id = new_id
        con.execute("UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
                    (name.strip(), age, email.strip(), student_id))


def delete_student(student_id: str) -> None:
    """Delete a student and their registrations.

    :param student_id: ID of the student to delete
    :type student_id: str
    """
    with connect() as con:
        con.execute("DELETE FROM students WHERE student_id=?", (student_id.strip(),))

# ----------------------------------------------------------------------
# INSTRUCTORS
# ----------------------------------------------------------------------

def create_instructor(instructor_id: str, name: str, age: int, email: str) -> None:
    """Insert a new instructor into the database.

    :param instructor_id: Unique identifier for the instructor
    :type instructor_id: str
    :param name: Instructor's full name
    :type name: str
    :param age: Instructor's age
    :type age: int
    :param email: Instructor's email
    :type email: str
    """
    with connect() as con:
        con.execute(
            "INSERT INTO instructors(instructor_id, name, age, email) VALUES(?,?,?,?)",
            (instructor_id.strip(), name.strip(), age, email.strip())
        )


def get_instructors() -> List[sqlite3.Row]:
    """Retrieve all instructors and their assigned courses.

    :return: List of instructors with concatenated course IDs
    :rtype: list[sqlite3.Row]
    """
    with connect() as con:
        return list(con.execute("""
            SELECT i.*,
                   IFNULL(GROUP_CONCAT(c.course_id, ','), '') AS courses
            FROM instructors i
            LEFT JOIN courses c ON c.instructor_id = i.instructor_id
            GROUP BY i.instructor_id
            ORDER BY i.instructor_id
        """))


def update_instructor(instructor_id: str, name: str, age: int, email: str, new_id: Optional[str] = None) -> None:
    """Update instructor details, optionally changing the ID.

    :param instructor_id: Current instructor ID
    :type instructor_id: str
    :param name: Updated name
    :type name: str
    :param age: Updated age
    :type age: int
    :param email: Updated email
    :type email: str
    :param new_id: Optional new instructor ID
    :type new_id: str, optional
    """
    with connect() as con:
        if new_id and new_id != instructor_id:
            con.execute("UPDATE instructors SET instructor_id=? WHERE instructor_id=?", (new_id, instructor_id))
            con.execute("UPDATE courses SET instructor_id=? WHERE instructor_id=?", (new_id, instructor_id))
            instructor_id = new_id
        con.execute("UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
                    (name.strip(), age, email.strip(), instructor_id))


def delete_instructor(instructor_id: str) -> None:
    """Delete an instructor and unassign from their courses.

    :param instructor_id: ID of the instructor to delete
    :type instructor_id: str
    """
    with connect() as con:
        con.execute("UPDATE courses SET instructor_id=NULL WHERE instructor_id=?", (instructor_id.strip(),))
        con.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id.strip(),))

# ----------------------------------------------------------------------
# COURSES
# ----------------------------------------------------------------------

def create_course(course_id: str, course_name: str) -> None:
    """Insert a new course.

    :param course_id: Unique identifier for the course
    :type course_id: str
    :param course_name: Course name
    :type course_name: str
    """
    with connect() as con:
        con.execute("INSERT INTO courses(course_id, course_name) VALUES(?,?)",
                    (course_id.strip(), course_name.strip()))


def get_courses() -> List[sqlite3.Row]:
    """Retrieve all courses and their enrolled students.

    :return: List of courses with enrolled students
    :rtype: list[sqlite3.Row]
    """
    with connect() as con:
        return list(con.execute("""
            SELECT c.*,
                   (SELECT IFNULL(GROUP_CONCAT(r.student_id, ','), '')
                      FROM registrations r
                     WHERE r.course_id = c.course_id) AS enrolled
            FROM courses c
            ORDER BY c.course_id
        """))


def update_course(course_id: str, course_name: str, new_id: Optional[str] = None) -> None:
    """Update course details, optionally changing the course ID.

    :param course_id: Current course ID
    :type course_id: str
    :param course_name: Updated course name
    :type course_name: str
    :param new_id: Optional new course ID
    :type new_id: str, optional
    """
    with connect() as con:
        if new_id and new_id != course_id:
            con.execute("UPDATE registrations SET course_id=? WHERE course_id=?", (new_id, course_id))
            con.execute("UPDATE courses SET course_id=?, course_name=? WHERE course_id=?",
                        (new_id, course_name.strip(), course_id))
        else:
            con.execute("UPDATE courses SET course_name=? WHERE course_id=?",
                        (course_name.strip(), course_id))


def delete_course(course_id: str) -> None:
    """Delete a course.

    :param course_id: ID of the course to delete
    :type course_id: str
    """
    with connect() as con:
        con.execute("DELETE FROM courses WHERE course_id=?", (course_id.strip(),))

# ----------------------------------------------------------------------
# ACTIONS
# ----------------------------------------------------------------------

def register_student(student_id: str, course_id: str) -> None:
    """Register a student into a course.

    :param student_id: ID of the student
    :type student_id: str
    :param course_id: ID of the course
    :type course_id: str
    """
    with connect() as con:
        con.execute("INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES(?,?)",
                    (student_id.strip(), course_id.strip()))


def assign_instructor(course_id: str, instructor_id: Optional[str]) -> None:
    """Assign an instructor to a course.

    :param course_id: Course ID
    :type course_id: str
    :param instructor_id: Instructor ID or None
    :type instructor_id: str | None
    """
    with connect() as con:
        con.execute("UPDATE courses SET instructor_id=? WHERE course_id=?",
                    (instructor_id.strip() if instructor_id else None, course_id.strip()))

# ----------------------------------------------------------------------
# SEARCH
# ----------------------------------------------------------------------

def search_all(term: str) -> Dict[str, List[sqlite3.Row]]:
    """Search across students, instructors, and courses.

    :param term: Search term (case-insensitive)
    :type term: str
    :return: Dictionary of search results grouped by 'students', 'instructors', and 'courses'
    :rtype: dict[str, list[sqlite3.Row]]
    """
    q = f"%{term.strip().lower()}%"
    with connect() as con:
        st = list(con.execute("""
            SELECT s.*, IFNULL(GROUP_CONCAT(r.course_id, ','), '') AS courses
            FROM students s LEFT JOIN registrations r ON r.student_id = s.student_id
            GROUP BY s.student_id
            HAVING LOWER(s.name) LIKE ? OR LOWER(s.student_id) LIKE ? OR LOWER(courses) LIKE ?
        """, (q,q,q)))
        ins = list(con.execute("""
            SELECT i.*, IFNULL(GROUP_CONCAT(c.course_id, ','), '') AS courses
            FROM instructors i LEFT JOIN courses c ON c.instructor_id = i.instructor_id
            GROUP BY i.instructor_id
            HAVING LOWER(i.name) LIKE ? OR LOWER(i.instructor_id) LIKE ? OR LOWER(courses) LIKE ?
        """, (q,q,q)))
        crs = list(con.execute("""
            SELECT c.*,
                   (SELECT IFNULL(GROUP_CONCAT(r.student_id, ','), '')
                      FROM registrations r WHERE r.course_id = c.course_id) AS enrolled
            FROM courses c
            WHERE LOWER(c.course_id) LIKE ? OR LOWER(c.course_name) LIKE ? OR LOWER(IFNULL(c.instructor_id,'')) LIKE ?
        """, (q,q,q)))
    return {"students": st, "instructors": ins, "courses": crs}

# ----------------------------------------------------------------------
# BACKUP
# ----------------------------------------------------------------------

def backup(to_path: str, db_path: str = DB_PATH) -> None:
    """Backup the database to a given path.

    :param to_path: Destination file path
    :type to_path: str
    :param db_path: Path to current database, defaults to DB_PATH
    :type db_path: str, optional
    """
    os.makedirs(os.path.dirname(to_path) or ".", exist_ok=True)
    shutil.copy2(db_path, to_path)

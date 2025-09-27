"""
School Management System - Lab 2 Project
========================================
Authors: Hilda Awada
Project: School Management System (PyQt GUI)
Copyright: 2025, Hilda Awada
Version: 1.0.0

This project implements a simple School Management System GUI
that allows managing students, instructors, and courses
using a local SQLite database.

The project demonstrates:
- GUI development (PyQt)
- Database integration
- Use of Sphinx-style docstrings for documentation
"""

import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt
import db  # SQLite helpers

# Initialize database
db.init_db()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def show_error(title, msg):
    """Display an error message dialog.

    :param title: The title of the error dialog
    :type title: str
    :param msg: The error message to display
    :type msg: str
    """
    QMessageBox.critical(None, title, msg)


class SchoolApp(QMainWindow):
    """Main application window for the School Management System."""

    def __init__(self):
        """Initialize the GUI and set up tabs."""
        super().__init__()
        self.setWindowTitle("School Management System")
        self.resize(800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._init_students_tab()
        self._init_instructors_tab()
        self._init_courses_tab()

    def _init_students_tab(self):
        """Initialize the Students tab with input fields and a table."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.student_id = QLineEdit()
        self.student_name = QLineEdit()
        self.student_age = QLineEdit()
        self.student_email = QLineEdit()
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)

        self.student_table = QTableWidget(0, 4)
        self.student_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Email"])

        layout.addWidget(QLabel("Student ID"))
        layout.addWidget(self.student_id)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.student_name)
        layout.addWidget(QLabel("Age"))
        layout.addWidget(self.student_age)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.student_email)
        layout.addWidget(add_btn)
        layout.addWidget(self.student_table)

        self.tabs.addTab(widget, "Students")
        self.refresh_students()

    def _init_instructors_tab(self):
        """Initialize the Instructors tab with input fields and a table."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.instructor_id = QLineEdit()
        self.instructor_name = QLineEdit()
        self.instructor_age = QLineEdit()
        self.instructor_email = QLineEdit()
        add_btn = QPushButton("Add Instructor")
        add_btn.clicked.connect(self.add_instructor)

        self.instructor_table = QTableWidget(0, 4)
        self.instructor_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Email"])

        layout.addWidget(QLabel("Instructor ID"))
        layout.addWidget(self.instructor_id)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.instructor_name)
        layout.addWidget(QLabel("Age"))
        layout.addWidget(self.instructor_age)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.instructor_email)
        layout.addWidget(add_btn)
        layout.addWidget(self.instructor_table)

        self.tabs.addTab(widget, "Instructors")
        self.refresh_instructors()

    def _init_courses_tab(self):
        """Initialize the Courses tab with input fields and a table."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.course_id = QLineEdit()
        self.course_name = QLineEdit()
        add_btn = QPushButton("Add Course")
        add_btn.clicked.connect(self.add_course)

        self.course_table = QTableWidget(0, 2)
        self.course_table.setHorizontalHeaderLabels(["Course ID", "Course Name"])

        layout.addWidget(QLabel("Course ID"))
        layout.addWidget(self.course_id)
        layout.addWidget(QLabel("Course Name"))
        layout.addWidget(self.course_name)
        layout.addWidget(add_btn)
        layout.addWidget(self.course_table)

        self.tabs.addTab(widget, "Courses")
        self.refresh_courses()

    def add_student(self):
        """Add a student to the database from the input fields.

        :raises ValueError: If email is invalid
        """
        try:
            sid = self.student_id.text().strip()
            name = self.student_name.text().strip()
            age = int(self.student_age.text().strip())
            email = self.student_email.text().strip()
            if not EMAIL_RE.match(email):
                raise ValueError("Invalid email format")
            db.create_student(sid, name, age, email)
            self.refresh_students()
        except Exception as ex:
            show_error("Error", str(ex))

    def refresh_students(self):
        """Refresh the student table with database records."""
        self.student_table.setRowCount(0)
        for row in db.get_students():
            r = self.student_table.rowCount()
            self.student_table.insertRow(r)
            for c, val in enumerate(row):
                self.student_table.setItem(r, c, QTableWidgetItem(str(val)))

    def add_instructor(self):
        """Add an instructor to the database from the input fields."""
        try:
            iid = self.instructor_id.text().strip()
            name = self.instructor_name.text().strip()
            age = int(self.instructor_age.text().strip())
            email = self.instructor_email.text().strip()
            db.create_instructor(iid, name, age, email)
            self.refresh_instructors()
        except Exception as ex:
            show_error("Error", str(ex))

    def refresh_instructors(self):
        """Refresh the instructor table with database records."""
        self.instructor_table.setRowCount(0)
        for row in db.get_instructors():
            r = self.instructor_table.rowCount()
            self.instructor_table.insertRow(r)
            for c, val in enumerate(row):
                self.instructor_table.setItem(r, c, QTableWidgetItem(str(val)))

    def add_course(self):
        """Add a course to the database from the input fields."""
        try:
            cid = self.course_id.text().strip()
            name = self.course_name.text().strip()
            db.create_course(cid, name)
            self.refresh_courses()
        except Exception as ex:
            show_error("Error", str(ex))

    def refresh_courses(self):
        """Refresh the course table with database records."""
        self.course_table.setRowCount(0)
        for row in db.get_courses():
            r = self.course_table.rowCount()
            self.course_table.insertRow(r)
            for c, val in enumerate(row):
                self.course_table.setItem(r, c, QTableWidgetItem(str(val)))


if __name__ == "__main__":
    """Entry point of the application."""
    app = QApplication(sys.argv)
    win = SchoolApp()
    win.show()
    sys.exit(app.exec_())

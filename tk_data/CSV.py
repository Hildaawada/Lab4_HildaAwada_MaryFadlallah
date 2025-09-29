"""
CSV utilities for the School Management System
==============================================

This module provides import/export helpers for Students, Instructors, and Courses.

Author: Hilda Awada
"""

import csv, os
import db


def export_all(folder: str):
    """
    Export all data to CSV files.

    :param folder: Target directory
    :type folder: str
    """
    # similar to save_all_csv from Tkinter


def import_all(folder: str):
    """
    Import all data from CSV files and reset DB.

    :param folder: Directory containing students.csv, instructors.csv, courses.csv
    :type folder: str
    """
    # similar to load_all_csv from Tkinter

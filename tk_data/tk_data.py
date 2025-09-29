"""
Tkinter GUI (SQLite-backed) for School Management System.

This module provides a Tkinter-based graphical user interface to manage
students, instructors, and courses stored in an SQLite database.
It integrates with :mod:`db` for persistence and supports CSV import/export,
searching, and live updates.

Author: Your Name
Version: 1.0
"""

import os, csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import db
db.init_db()  # ensure tables exist

# ---------- Helpers ----------
def clear_entries(*entries: ttk.Entry):
    """
    Clear the contents of multiple Tkinter entry widgets.

    :param entries: Tkinter Entry widgets
    :type entries: ttk.Entry
    """
    for e in entries:
        e.delete(0, tk.END)


def students_table():
    """
    Refresh and display all students in the students Treeview.
    """
    tv_students.delete(*tv_students.get_children())
    for r in db.list_students():
        tv_students.insert("", tk.END, values=(r["student_id"], r["name"], r["age"], r["email"], r["courses"]))


def instructors_table():
    """
    Refresh and display all instructors in the instructors Treeview.
    """
    tv_instructors.delete(*tv_instructors.get_children())
    for r in db.list_instructors():
        tv_instructors.insert("", tk.END, values=(r["instructor_id"], r["name"], r["age"], r["email"], r["courses"]))


def courses_table():
    """
    Refresh and display all courses in the courses Treeview.
    """
    tv_courses.delete(*tv_courses.get_children())
    for r in db.list_courses():
        tv_courses.insert("", tk.END, values=(r["course_id"], r["course_name"], r["instructor_id"] or "", r["enrolled"]))


def refresh_all_tables():
    """
    Refresh all GUI tables (students, instructors, courses) and update comboboxes.
    """
    students_table()
    instructors_table()
    courses_table()
    update_course_cmbboxes()


def update_course_cmbboxes():
    """
    Update course combobox values for student and instructor forms.
    """
    vals = [r["course_id"] for r in db.list_courses()]
    cmb_stu_course["values"] = vals
    cmb_ins_course["values"] = vals


# ---------- CSV Export/Import (from DB) ----------
def save_all_csv():
    """
    Export all students, instructors, and courses from the database to CSV files.

    Saves three files: ``students.csv``, ``instructors.csv``, and ``courses.csv``.
    """
    folder = filedialog.askdirectory(title="Pick folder to save as CSV")
    if not folder: return
    try:
        with open(os.path.join(folder, "students.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["student_id","name","age","email","registered_courses"])
            for r in db.list_students():
                w.writerow([r["student_id"], r["name"], r["age"], r["email"], r["courses"]])

        with open(os.path.join(folder, "instructors.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["instructor_id","name","age","email","assigned_courses"])
            for r in db.list_instructors():
                w.writerow([r["instructor_id"], r["name"], r["age"], r["email"], r["courses"]])

        with open(os.path.join(folder, "courses.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["course_id","course_name","instructor_id","enrolled_students"])
            for r in db.list_courses():
                w.writerow([r["course_id"], r["course_name"], r["instructor_id"] or "", r["enrolled"]])

        messagebox.showinfo("Saved", f"Saved CSV files in:\n{folder}")
    except Exception as e:
        messagebox.showerror("Save error", str(e))


def load_all_csv():
    """
    Import students, instructors, and courses from CSV files into the database.

    Expects ``students.csv``, ``instructors.csv``, and ``courses.csv`` in the selected folder.
    """
    folder = filedialog.askdirectory(title="Pick a folder to load CSV files from")
    if not folder: return
    try:
        courses_path = os.path.join(folder, "courses.csv")
        instructors_path = os.path.join(folder, "instructors.csv")
        students_path = os.path.join(folder, "students.csv")

        # Reset DB for a clean import
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
        db.init_db()

        # Courses
        if os.path.exists(courses_path):
            with open(courses_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    cid = row["course_id"].strip()
                    cname = row["course_name"].strip()
                    iid = (row.get("instructor_id") or "").strip() or None
                    db.create_course(cid, cname)
                    if iid:
                        db.assign_instructor(cid, iid)

        # Instructors
        if os.path.exists(instructors_path):
            with open(instructors_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    db.create_instructor(
                        row["instructor_id"].strip(),
                        row["name"].strip(),
                        int(row["age"]),
                        row["email"].strip()
                    )
                    assigned = row.get("assigned_courses","").replace(";", ",").split(",") if row.get("assigned_courses") else []
                    for cid in [x.strip() for x in assigned if x.strip()]:
                        db.assign_instructor(cid, row["instructor_id"].strip())

        # Students
        if os.path.exists(students_path):
            with open(students_path, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    db.create_student(
                        row["student_id"].strip(),
                        row["name"].strip(),
                        int(row["age"]),
                        row["email"].strip()
                    )
                    registered = row.get("registered_courses","").replace(";", ",").split(",") if row.get("registered_courses") else []
                    for cid in [x.strip() for x in registered if x.strip()]:
                        db.register_student(row["student_id"].strip(), cid)

        refresh_all_tables()
        messagebox.showinfo("Loaded", f"Loaded CSV files from:\n{folder}")
    except Exception as e:
        messagebox.showerror("Load error", str(e))


def backup_db():
    """
    Create a backup of the SQLite database.

    Prompts the user to select a filename for saving the backup copy.
    """
    to = filedialog.asksaveasfilename(
        title="Save DB Backup As",
        defaultextension=".db",
        filetypes=[("SQLite DB","*.db"), ("All files","*.*")]
    )
    if not to: return
    try:
        db.backup(to)
        messagebox.showinfo("Backup", f"Database copied to:\n{to}")
    except Exception as e:
        messagebox.showerror("Backup error", str(e))


# ---------- Search ----------
def search_all():
    """
    Search across students, instructors, and courses for a given term.

    Updates all Treeviews with matching results.
    """
    term = ent_search.get().strip()
    if not term:
        refresh_all_tables(); return
    res = db.search_all(term)

    tv_students.delete(*tv_students.get_children())
    for r in res["students"]:
        tv_students.insert("", tk.END, values=(r["student_id"], r["name"], r["age"], r["email"], r["courses"]))

    tv_instructors.delete(*tv_instructors.get_children())
    for r in res["instructors"]:
        tv_instructors.insert("", tk.END, values=(r["instructor_id"], r["name"], r["age"], r["email"], r["courses"]))

    tv_courses.delete(*tv_courses.get_children())
    for r in res["courses"]:
        tv_courses.insert("", tk.END, values=(r["course_id"], r["course_name"], r["instructor_id"] or "", r["enrolled"]))


def clear_search():
    """
    Clear the search box and refresh all tables.
    """
    ent_search.delete(0, tk.END)
    refresh_all_tables()


# ---------- UI ----------
root = tk.Tk()
root.title("School Management System")
root.geometry("1200x680")

# Top bar
frm_top = ttk.Frame(root); frm_top.pack(fill="x", padx=10, pady=8)
ent_search = ttk.Entry(frm_top, width=60); ent_search.pack(side="left")
ttk.Button(frm_top, text="Search", command=search_all).pack(side="left", padx=5)
ttk.Button(frm_top, text="Clear", command=clear_search).pack(side="left", padx=5)
ttk.Button(frm_top, text="Save All (CSV)", command=save_all_csv).pack(side="right", padx=5)
ttk.Button(frm_top, text="Load All (CSV)", command=load_all_csv).pack(side="right", padx=5)
ttk.Button(frm_top, text="Backup DB", command=backup_db).pack(side="right", padx=5)

# Tabs
nb = ttk.Notebook(root); nb.pack(fill="both", expand=True, padx=10, pady=8)

# Students Tab
tab_stu = ttk.Frame(nb); nb.add(tab_stu, text="Students")
lf_stu = ttk.LabelFrame(tab_stu, text="Student Form"); lf_stu.pack(side="left", fill="y", padx=8, pady=8)
ent_stu_name = ttk.Entry(lf_stu, width=28); ent_stu_name.grid(row=0, column=1, padx=5, pady=4)
ent_stu_age = ttk.Entry(lf_stu, width=28); ent_stu_age.grid(row=1, column=1, padx=5, pady=4)
ent_stu_email = ttk.Entry(lf_stu, width=28); ent_stu_email.grid(row=2, column=1, padx=5, pady=4)
ent_stu_id = ttk.Entry(lf_stu, width=28); ent_stu_id.grid(row=3, column=1, padx=5, pady=4)
cmb_stu_course = ttk.Combobox(lf_stu, values=[], state="readonly", width=25); cmb_stu_course.grid(row=4, column=1, padx=5, pady=4)
lf_stu_tbl = ttk.LabelFrame(tab_stu, text="Students"); lf_stu_tbl.pack(side="left", fill="both", expand=True, padx=8, pady=8)
tv_students = ttk.Treeview(lf_stu_tbl, columns=("id","name","age","email","courses"), show="headings", height=18)
for col, w in (("id",120),("name",180),("age",60),("email",240),("courses",260)):
    tv_students.heading(col, text=col.capitalize()); tv_students.column(col, width=w, anchor="w")
tv_students.pack(fill="both", expand=True)

# Instructors Tab
tab_ins = ttk.Frame(nb); nb.add(tab_ins, text="Instructors")
lf_ins = ttk.LabelFrame(tab_ins, text="Instructor Form"); lf_ins.pack(side="left", fill="y", padx=8, pady=8)
ent_ins_name = ttk.Entry(lf_ins, width=28); ent_ins_name.grid(row=0, column=1, padx=5, pady=4)
ent_ins_age = ttk.Entry(lf_ins, width=28); ent_ins_age.grid(row=1, column=1, padx=5, pady=4)
ent_ins_email = ttk.Entry(lf_ins, width=28); ent_ins_email.grid(row=2, column=1, padx=5, pady=4)
ent_ins_id = ttk.Entry(lf_ins, width=28); ent_ins_id.grid(row=3, column=1, padx=5, pady=4)
cmb_ins_course = ttk.Combobox(lf_ins, values=[], state="readonly", width=25); cmb_ins_course.grid(row=4, column=1, padx=5, pady=4)
lf_ins_tbl = ttk.LabelFrame(tab_ins, text="Instructors"); lf_ins_tbl.pack(side="left", fill="both", expand=True, padx=8, pady=8)
tv_instructors = ttk.Treeview(lf_ins_tbl, columns=("id","name","age","email","courses"), show="headings", height=18)
for col, w in (("id",120),("name",180),("age",60),("email",240),("courses",260)):
    tv_instructors.heading(col, text=col.capitalize()); tv_instructors.column(col, width=w, anchor="w")
tv_instructors.pack(fill="both", expand=True)

# Courses Tab
tab_crs = ttk.Frame(nb); nb.add(tab_crs, text="Courses")
lf_crs = ttk.LabelFrame(tab_crs, text="Course Form"); lf_crs.pack(side="left", fill="y", padx=8, pady=8)
ent_crs_id = ttk.Entry(lf_crs, width=28); ent_crs_id.grid(row=0, column=1, padx=5, pady=4)
ent_crs_name = ttk.Entry(lf_crs, width=28); ent_crs_name.grid(row=1, column=1, padx=5, pady=4)
lf_crs_tbl = ttk.LabelFrame(tab_crs, text="Courses"); lf_crs_tbl.pack(side="left", fill="both", expand=True, padx=8, pady=8)
tv_courses = ttk.Treeview(lf_crs_tbl, columns=("id","name","instructor","enrolled"), show="headings", height=18)
for col, w in (("id",120),("name",220),("instructor",160),("enrolled",280)):
    tv_courses.heading(col, text=col.capitalize()); tv_courses.column(col, width=w, anchor="w")
tv_courses.pack(fill="both", expand=True)

# ✅ Refresh after widgets exist
refresh_all_tables()
root.mainloop()

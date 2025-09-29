# db.py
import sqlite3, shutil, os

DB_PATH = "school.db"

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            age          INTEGER NOT NULL,
            email        TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name          TEXT NOT NULL,
            age           INTEGER NOT NULL,
            email         TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS courses (
            course_id     TEXT PRIMARY KEY,
            course_name   TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS registrations (
            student_id TEXT,
            course_id  TEXT,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        );
        """)

# ------------------ Students ------------------
def create_student(sid, name, age, email):
    with connect() as con:
        con.execute("INSERT INTO students (student_id,name,age,email) VALUES (?,?,?,?)",
                    (sid, name, age, email))

def update_student(old_sid, name, age, email, new_id=None):
    with connect() as con:
        if new_id and new_id != old_sid:
            con.execute("UPDATE students SET student_id=?, name=?, age=?, email=? WHERE student_id=?",
                        (new_id, name, age, email, old_sid))
        else:
            con.execute("UPDATE students SET name=?, age=?, email=? WHERE student_id=?",
                        (name, age, email, old_sid))

def delete_student(sid):
    with connect() as con:
        con.execute("DELETE FROM students WHERE student_id=?", (sid,))

def list_students():
    with connect() as con:
        cur = con.execute("""
            SELECT s.student_id, s.name, s.age, s.email,
                   COALESCE(GROUP_CONCAT(c.course_id), '') AS courses
            FROM students s
            LEFT JOIN registrations r ON r.student_id=s.student_id
            LEFT JOIN courses c ON c.course_id=r.course_id
            GROUP BY s.student_id
        """)
        return cur.fetchall()

def register_student(sid, cid):
    with connect() as con:
        con.execute("INSERT OR IGNORE INTO registrations (student_id,course_id) VALUES (?,?)", (sid, cid))

# ------------------ Instructors ------------------
def create_instructor(iid, name, age, email):
    with connect() as con:
        con.execute("INSERT INTO instructors (instructor_id,name,age,email) VALUES (?,?,?,?)",
                    (iid, name, age, email))

def update_instructor(old_iid, name, age, email, new_id=None):
    with connect() as con:
        if new_id and new_id != old_iid:
            con.execute("UPDATE instructors SET instructor_id=?, name=?, age=?, email=? WHERE instructor_id=?",
                        (new_id, name, age, email, old_iid))
        else:
            con.execute("UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?",
                        (name, age, email, old_iid))

def delete_instructor(iid):
    with connect() as con:
        con.execute("DELETE FROM instructors WHERE instructor_id=?", (iid,))

def list_instructors():
    with connect() as con:
        cur = con.execute("""
            SELECT i.instructor_id, i.name, i.age, i.email,
                   COALESCE(GROUP_CONCAT(c.course_id), '') AS courses
            FROM instructors i
            LEFT JOIN courses c ON c.instructor_id=i.instructor_id
            GROUP BY i.instructor_id
        """)
        return cur.fetchall()

def assign_instructor(cid, iid):
    with connect() as con:
        con.execute("UPDATE courses SET instructor_id=? WHERE course_id=?", (iid, cid))

# ------------------ Courses ------------------
def create_course(cid, cname):
    with connect() as con:
        con.execute("INSERT INTO courses (course_id,course_name) VALUES (?,?)", (cid, cname))

def update_course(old_cid, name, new_id=None):
    with connect() as con:
        if new_id and new_id != old_cid:
            con.execute("UPDATE courses SET course_id=?, course_name=? WHERE course_id=?",
                        (new_id, name, old_cid))
        else:
            con.execute("UPDATE courses SET course_name=? WHERE course_id=?",
                        (name, old_cid))

def delete_course(cid):
    with connect() as con:
        con.execute("DELETE FROM courses WHERE course_id=?", (cid,))

def list_courses():
    with connect() as con:
        cur = con.execute("""
            SELECT c.course_id, c.course_name, c.instructor_id,
                   COUNT(r.student_id) AS enrolled
            FROM courses c
            LEFT JOIN registrations r ON r.course_id=c.course_id
            GROUP BY c.course_id
        """)
        return cur.fetchall()

# ------------------ Search ------------------
def search_all(term):
    like = f"%{term}%"
    with connect() as con:
        return {
            "students": con.execute("SELECT student_id, name, age, email, '' as courses FROM students WHERE name LIKE ? OR student_id LIKE ?", (like, like)).fetchall(),
            "instructors": con.execute("SELECT instructor_id, name, age, email, '' as courses FROM instructors WHERE name LIKE ? OR instructor_id LIKE ?", (like, like)).fetchall(),
            "courses": con.execute("SELECT course_id, course_name, instructor_id, '' as enrolled FROM courses WHERE course_name LIKE ? OR course_id LIKE ?", (like, like)).fetchall()
        }

# ------------------ Backup ------------------
def backup(path):
    shutil.copy(DB_PATH, path)

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("lab.db")


SCHEMA_SQL = """
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    score REAL NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    level TEXT NOT NULL
);

CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);
"""


SEED_SQL = """
INSERT INTO students (name, cohort, score) VALUES
    ('An Nguyen', 'A1', 91.5),
    ('Binh Tran', 'A1', 84.0),
    ('Chi Pham', 'B2', 76.5),
    ('Dung Le', 'B2', 88.0),
    ('Eva Vo', 'A1', 95.0);

INSERT INTO courses (title, level) VALUES
    ('Intro to MCP', 'beginner'),
    ('SQLite for AI Tools', 'beginner'),
    ('Safe SQL Patterns', 'intermediate');

INSERT INTO enrollments (student_id, course_id, status) VALUES
    (1, 1, 'active'),
    (1, 2, 'active'),
    (2, 1, 'active'),
    (3, 2, 'completed'),
    (4, 3, 'active'),
    (5, 1, 'active'),
    (5, 3, 'active');
"""


def create_database(db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.executescript(SEED_SQL)
        conn.commit()
    finally:
        conn.close()

    return db_path


if __name__ == "__main__":
    path = create_database()
    print(f"Created database at {path}")

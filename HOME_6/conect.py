from datetime import datetime, date, timedelta
from random import randint
import sqlite3

from faker import Faker

fake = Faker('uk-UA')

subject = [
    "Основи програмування",
    "Математичний аналіз",
    "Численні методи",
    "Культурологія",
    "Філософія",
    "Теорія ймовірності",
    "Web програмування",
    "Механіка рідини і газу",
    "Фізика",
]

groups = ["FF-11", "GoIt-12", "em-10"]

NUMBERS_TEACHERS = 5
NUMBERS_STUDENT = 60

connect = sqlite3.connect('home_6_Web.db')
cursor = connect.cursor()

def seed_teacher():
    teacher = [fake.name() for _ in range(NUMBERS_TEACHERS)]
    sql = "INSERT INTO teacher (fullname) VALUES (?);"
    cursor.executemany(sql, zip(teacher,))

def seed_groups():
    sql = "INSERT INTO groups (group_name) VALUES (?);"
    cursor.executemany(sql, zip(groups,))

def seed_students():
    students = [fake.name() for _ in range(NUMBERS_STUDENT)]
    list_group_id = [randint(1, len(groups)) for _ in range(NUMBERS_STUDENT)]
    sql = "INSERT INTO students (fullname, group_id) VALUES (?, ?);"
    cursor.executemany(sql, zip(students, list_group_id))

def seed_subject():
    list_teacher_id = [randint(1, NUMBERS_TEACHERS) for _ in range(len(subject))]
    sql = "INSERT INTO subject (subject_name, teacher_id) VALUES (?, ?);"
    cursor.executemany(sql, zip(subject, list_teacher_id))

def seed_grades():
    start_date = datetime.strptime("2022-09-01", "%Y-%m-%d")
    finish_date = datetime.strptime("2023-05-31", "%Y-%m-%d")
    sql = "INSERT INTO grades (student_id, subject_id, grade, date_of) VALUES (?, ?, ?, ?);"

    def get_list_date(start_date, finish_date) -> list[date]:
        result = []
        current_day: date = start_date.date()
        while current_day < finish_date.date():
            if current_day.isoweekday() < 6:
                result.append(current_day)
            current_day += timedelta(days=1)
        return result

    list_date = get_list_date(start_date, finish_date)

    grades = []
    for day in list_date:
        random_subject = randint(1, len(subject))
        random_student = [randint(1, NUMBERS_STUDENT) for _ in range(7)]
        for student in random_student:
            grades.append((student, random_subject, randint(1, 12), day))

    cursor.executemany(sql, grades)


if __name__ == "__main__":
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("DROP TABLE IF EXISTS grades;")
    cursor.execute("DROP TABLE IF EXISTS subject;")
    cursor.execute("DROP TABLE IF EXISTS students;")
    cursor.execute("DROP TABLE IF EXISTS groups;")
    cursor.execute("DROP TABLE IF EXISTS teacher;")

    cursor.execute("""
        CREATE TABLE teacher (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            group_id INTEGER,
            FOREIGN KEY (group_id) REFERENCES groups (id)
        );
    """)

    cursor.execute("""
        CREATE TABLE subject (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teacher (id)
        );
    """)

    cursor.execute("""
        CREATE TABLE grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            grade INTEGER,
            date_of DATE,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (subject_id) REFERENCES subject (id)
        );
    """)

    seed_teacher()
    seed_groups()
    seed_students()
    seed_subject()
    seed_grades()

    connect.commit()
    cursor.close()
    connect.close()

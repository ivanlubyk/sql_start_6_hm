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
    cursor.executemany(sql, zip(teacher, ))


def seed_groups():
    sql = "INSERT INTO groups (group_name) VALUES (?);"
    cursor.executemany(sql, zip(groups, ))


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

    # Початок циклу while
    while True:
        print("Оберіть номер запиту:")
        print("1. Знайти 5 студентів із найбільшим середнім балом з усіх предметів.")
        print("2. Знайти студента із найвищим середнім балом з певного предмета.")
        print("3. Знайти середній бал у групах з певного предмета.")
        print("4. Знайти середній бал на потоці (по всій таблиці оцінок).")
        print("5. Знайти, які курси читає певний викладач.")
        print("6. Знайти список студентів у певній групі.")
        print("7. Знайти оцінки студентів в окремій групі з певного предмета.")
        print("8. Знайти середній бал, який ставить певний викладач зі своїх предметів.")
        print("9. Знайти список курсів, які відвідує студент.")
        print("10. Список курсів, які певному студенту читає певний викладач.")
        print("0. Вийти з програми.")
        choice = input("Введіть номер запиту: ")

        if choice == "0":
            break

        try:
            choice = int(choice)
            if choice == 1:
                query = "SELECT students.fullname, AVG(grades.grade) AS average_grade FROM students JOIN grades ON students.id = grades.student_id GROUP BY students.id ORDER BY average_grade DESC LIMIT 5;"
            elif choice == 2:
                subject_name = input("Введіть назву предмета: ")
                query = f"SELECT students.fullname, AVG(grades.grade) AS average_grade FROM students JOIN grades ON students.id = grades.student_id JOIN subject ON grades.subject_id = subject.id WHERE subject.subject_name = '{subject_name}' GROUP BY students.id ORDER BY average_grade DESC LIMIT 1;"
            elif choice == 3:
                subject_name = input("Введіть назву предмета: ")
                query = f"SELECT groups.group_name, AVG(grades.grade) AS average_grade FROM groups JOIN students ON groups.id = students.group_id JOIN grades ON students.id = grades.student_id JOIN subject ON grades.subject_id = subject.id WHERE subject.subject_name = '{subject_name}' GROUP BY groups.id;"
            elif choice == 4:
                query = "SELECT AVG(grades.grade) AS average_grade FROM grades;"
            elif choice == 5:
                teacher_name = input("Введіть повне ім'я викладача: ")
                query = f"SELECT subject.subject_name FROM subject JOIN teacher ON subject.teacher_id = teacher.id WHERE teacher.fullname = '{teacher_name}';"
            elif choice == 6:
                group_name = input("Введіть назву групи: ")
                query = f"SELECT students.fullname FROM students JOIN groups ON students.group_id = groups.id WHERE groups.group_name = '{group_name}';"
            elif choice == 7:
                group_name = input("Введіть назву групи: ")
                subject_name = input("Введіть назву предмета: ")
                query = f"SELECT students.fullname, grades.grade FROM students JOIN groups ON students.group_id = groups.id JOIN grades ON students.id = grades.student_id JOIN subject ON grades.subject_id = subject.id WHERE groups.group_name = '{group_name}' AND subject.subject_name = '{subject_name}';"
            elif choice == 8:
                teacher_name = input("Введіть повне ім'я викладача: ")
                query = f"SELECT AVG(grades.grade) AS average_grade FROM grades JOIN subject ON grades.subject_id = subject.id JOIN teacher ON subject.teacher_id = teacher.id WHERE teacher.fullname = '{teacher_name}';"
            elif choice == 9:
                student_name = input("Введіть повне ім'я студента: ")
                query = f"SELECT subject.subject_name FROM subject JOIN grades ON subject.id = grades.subject_id JOIN students ON grades.student_id = students.id WHERE students.fullname = '{student_name}';"
            elif choice == 10:
                student_name = input("Введіть повне ім'я студента: ")
                teacher_name = input("Введіть повне ім'я викладача: ")
                query = f"SELECT subject.subject_name FROM subject JOIN grades ON subject.id = grades.subject_id JOIN students ON grades.student_id = students.id JOIN teacher ON subject.teacher_id = teacher.id WHERE students.fullname = '{student_name}' AND teacher.fullname = '{teacher_name}';"
            else:
                print("Неправильний номер запиту.")
                continue

            cursor.execute(query)
            result = cursor.fetchall()

            if result:
                print("Результат запиту:")
                for row in result:
                    print(row)
            else:
                print("За вашим запитом нічого не знайдено.")

        except ValueError:
            print("Будь ласка, введіть номер запиту у числовому форматі.")

    cursor.close()
    connect.close()
import os, csv
from login import LoginCredential
from student import Student
from professor import Professor
from course import Course
from grade_scale import GradeScale
from user import User

######## FILES #################
login_file = 'login.csv'
student_file = 'students.csv'
professor_file = 'professors.csv'
course_file = 'courses.csv'

# Login details
if not os.path.exists(login_file):
    with open(login_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Password","Salt","Role"])

# Student
students_file = "students.csv"
if not os.path.exists(students_file):
    with open(students_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "email_address", "first_name", "last_name", "courses", "grade", "marks"])

# Professors
professors_file = "professors.csv"
if not os.path.exists(professors_file):
    with open(professors_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["professor_id", "email_address", "first_name", "last_name", "course_id", "rank"])

# Courses
courses_file = "courses.csv"
if not os.path.exists(courses_file):
    with open(courses_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["course_id", "course_name", "credits", "description"])

################## MENUS ################################
def menu_admin(students: Student, profs: Professor, courses: Course, grades: GradeScale):
    while True:
            print(
                "\n[ADMIN MENU]\n"
                "1) List students\n"
                "2) Add student\n"
                "3) Delete student\n"
                "4) Update student\n"
                "5) List professors\n"
                "6) Add professor\n"
                "7) Delete professor\n"
                "8) Modify professor\n"
                "9) List courses\n"
                "10) Add course\n"
                "11) Delete course\n"
                "12) Show grade scale\n"
                "13) Add grade\n"
                "14) Delete grade\n"
                "15) Modify grade\n"
                "0) Logout\n"
            )
            #-------STUDENT---------------------
            choice = input("Choose: ").strip()
            if choice == "1":
                students.display_records()
            elif choice == "2":
                id = input("Enter student id: ").strip()
                first = input("Enter first name: ").strip()
                last = input("Enter last name: ").strip()
                email = input("Enter email address: ").strip()
                pw = input("Create Password: ").strip()
                courses = input("Enter Course ID: ").strip()
                grade = input("Enter grade if any: ").strip() or None
                marks_raw = input("Enter marks if any (press Enter to skip): ").strip()
                marks = int(marks_raw) if marks_raw else None
                u = User(user_id=id, email_address=email, first_name=first, last_name=last, role="student")
                students.add_new_student(u,login_file,  pw, grade=grade, marks=marks)
            elif choice == "3":
                id = input("Enter id of student to delete: ")
                students.delete_new_student(id)
            elif choice == "4":
                id = input("Enter student_id to update: ")
                first = input("Enter student first name: ").strip()
                last = input("Enter last name: ")
                email = input("Enter email address: ").strip()
                grade = input("Enter grade if any: ").strip()
                marks = input("Enter marks (leave blank to keep): ").strip()
                u = User(user_id=id,email_address=email,first_name=first,last_name=last,role="student")

                grade = grade if grade else None
                marks = int(marks) if marks else None

                students.update_student_record(u, grade=grade, marks=marks)
            # -----------------------------PROFESSOR --------------------------
            elif choice == "5":
                profs.display_professors()
            elif choice == "6":
                id = input("Enter Professor id: ").strip()
                first = input("Enter first name: ").strip()
                last = input("Enter last name: ").strip()
                email = input("Enter email address: ").strip()
                pw = input("Create Password: ").strip()
                c_id = input("Enter course_id").strip()
                rank = input("Enter rank: ").strip()
                u = User(user_id=id,email_address=email,first_name=first,last_name=last,role="professor")
                profs.add_new_professor(login_file, u, pw, c_id, rank)
            elif choice == "7":
                id = input("Enter id of Professor to delete: ")
                profs.delete_professor(id)
            elif choice == "8":
                id = input("Enter Professor id: ").strip()
                first = input("Enter first name: ").strip()
                last = input("Enter last name: ").strip()
                email = input("Enter email address: ").strip()
                rank = input("Enter rank: ").strip()
                u = User(user_id=id,email_address=email,first_name=first,last_name=last,role="professor")
                profs.modify_professor_details(u, rank=rank)

            # ---------- COURSES --------------------------------------
            elif choice == "9":
                courses.display_courses()
            elif choice == "10":
                id = input("Enter course id: ").strip()
                name = input("Enter course name: ").strip()
                credits = input("Enter number of credits for this course: ").strip()
                description = input("Enter a short description of the course (if any): ").strip()
                courses.add_new_course(id, name, credits, description)
            elif choice == "11":
                id = input("Enter course id to delete: ").strip()
                courses.delete_new_course(id)

            # ---------- Grades -----------------------------------
            elif choice == "12":
                order = input("View report grouped by:\n1. student_id\n2. course\nChoose 1 or 2: ").strip()
                if order == "1":
                    sort = "student_id"
                elif order == "2":
                    sort = "course"
                else:
                    print("Invalid choice. Defaulting to student_id.")
                    sort = "student_id"
                grades.display_grade_report(sort)

            elif choice == "13":
                student_id = input("Enter student ID: ").strip()
                course = input("Enter course name/code: ").strip()
                try:
                    grade = float(input("Enter grade (number): ").strip())
                except ValueError:
                    print("Invalid grade. Must be a number.")
                else:
                    grades.add_grade(student_id, course, grade)
                    print("Grade added.")

            elif choice == "14":
                student_id = input("Enter student ID to delete: ").strip()
                course = input("Enter course name/code: ").strip()
                grades.delete_grade(student_id, course)
                print("Deleted if it existed.")

            elif choice == "15":
                student_id = input("Enter student ID to modify: ").strip()
                course = input("Enter course name/code: ").strip()
                try:
                    new_grade = float(input("Enter new grade (number): ").strip())
                except ValueError:
                    print("Invalid grade. Must be a number.")
                else:
                    if grades.modify_grade(student_id, course, new_grade):
                        print("Grade updated.")
                    
            elif choice == "0":
                return
            #     login.logout()
            else:
                print("Invalid choice.")

def menu_student(students: Student):
    while True:
        print(
            "\n[STUDENT MENU]\n"
            "1) My grades (letters)\n"
            "2) My marks (numeric)\n"
            "0) Logout\n"
        )
        choice = input("Choose: ").strip()
        if choice == "1":
            students.check_my_grades(id)
        elif choice == "2":
            students.check_my_marks(id)
        elif choice == "0":
            return
        else:
            print("Invalid choice.")

def menu_professor(profs: Professor, courses: Course):
    while True:
        print(
            "\n[PROFESSOR MENU]\n"
            "1) My course details\n"
            "2) List all courses\n"
            "0) Logout\n"
        )
        choice = input("Choose: ").strip()
        if choice == "1":
            p_id = input("Enter Professor ID to search: ").strip()
            profs.show_course_details_by_professor(professors_file, course_file, p_id)
        elif choice == "2":
            courses.display_courses()
        elif choice == "0":
            return
        else:
            print("Invalid choice.")

############## MAIN #################################
def main():
    login = LoginCredential(login_file)
    students = Student(student_file)
    profs = Professor(professor_file)
    courses = Course(course_file)
    grades = GradeScale()

    while True:
        print("=== Welcome ===")
        role_input = input("Role (1.admin/2.student/3.professor): ").strip().lower()
        if role_input == "1":
            print("Logged in as: admin")
            menu_admin(students, profs, courses, grades)
            return
        if role_input not in ("2", "3"):
            print("Invalid role.")
            return
        
        email = input("Email: ").strip()
        password = input("Password: ").strip()

        role = login.login(email, password)
        if not role:
            print("Invalid credentials.")
        else:
            print("Logged in as:", role)

        if role == "admin":
            menu_admin(students, profs, courses, grades)
        elif role == "student":
            menu_student(students)
        elif role == "professor":
            menu_professor(profs, courses)
        else:
            menu_student(students)

        login.logout()

if __name__ == "__main__":
    main()
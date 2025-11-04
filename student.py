import csv, os
from user import User
from login import LoginCredential

class Student:
    def __init__(self, file_path):
            self.file = file_path

    def display_records(self):
            with open(self.file, 'r', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                            print(row)
    
    def add_new_student(self, login_csv, u:User, password, courses=None,grade=None, marks=None):
            exists = False
            with open(self.file, "r", newline="", encoding="utf-8") as f:
                  reader = csv.reader(f)
                  header = next(reader, None)

                  id_idx = 0
                  if header and "student_id" in header:
                        id_idx = header.index("student_id")

                  for row in reader:
                        if row and row[id_idx] == str(u.user_id):
                              exists = True
                              break

            if exists:
                  print(f"Student ID {u.user_id} already exists. No record added.")
                  return False
            with open(self.file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([u.user_id, u.email_address, u.first_name, u.last_name, courses if courses is not None else "", grade or "", marks if marks is not None else ""])
                        print(f"{u.first_name} added successfully!")
            if not os.path.exists(self.file) or os.path.getsize(self.file) == 0:
                  with open(self.file, "w", newline="", encoding="utf-8") as f:
                        csv.writer(f).writerow(["Email", "Password", "Salt", "Role"])

            # encrypt using LoginCredential
            salt_hex = os.urandom(16).hex()
            lc = LoginCredential(self.file)  # we just need its encrypt_password method
            pwd_hash = lc.encrypt_password(password, salt_hex)

            # append to login.csv
            with open(login_csv, "a", newline="", encoding="utf-8") as f:
                  writer = csv.DictWriter(f, fieldnames=["Email", "Password", "Salt", "Role"])
                  writer.writerow({
                        "Email": u.email_address,
                        "Password": pwd_hash,
                        "Salt": salt_hex,
                        "Role": "student"
                  })
            print(f"{u.first_name} added successfully!")
            return True
        
    
    def delete_new_student(self, student_id):
        rows = []
        with open(self.file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                        if row[0] != student_id:
                                rows.append(row)
        with open(self.file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"Student deleted successfully!")
        
    
    def update_student_record(self, u:User, courses=None, grade=None, marks=None):
        rows = []
        with open(self.file, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                  if row and row[0] == u.user_id:
                        row[1] = u.email_address or row[1]
                        row[2] = u.first_name or row[2]
                        row[3] = u.last_name or row[3]
                        if courses is not None:
                              row[4] = courses
                        if grade is not None:
                              row[5] = grade
                        if marks is not None:
                              row[6] = marks
                  rows.append(row)
            with open(self.file, 'w', newline='') as f:
                  writer = csv.writer(f)
                  writer.writerows(rows)
            print("Student record updated successfully!")
    
    def check_my_grades(self, student_id):
          with open(self.file, 'r', newline='') as f:
            reader = csv.DictReader(f)  # columns: student_id,email_address,first_name,last_name,courses,grade,marks
            found = False
            for row in reader:
                  if str(row.get("student_id", "")).strip() == str(student_id):
                  # Show grade (letter) for this student (optionally include course)
                        print(f"Grade for {row['first_name']} {row['last_name']} ({row['courses']}): {row['grade']}")
                  found = True
            if not found:
                  print("Student record not found")

    def check_my_marks(self, student_id):
          with open(self.file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            found = False
            for row in reader:
                  if str(row.get("student_id", "")).strip() == str(student_id):
                        print(f"Marks for {row['first_name']} {row['last_name']} ({row['courses']}): {row['marks']}")
                  found = True
            if not found:
                  print("Student not found.")
                        
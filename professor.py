import csv, os, json
from user import User
from login import LoginCredential

class Professor:
    def __init__(self, file_path):
        self.file = file_path

    def csv_to_json(self, csv_file):
        with open(csv_file, "r", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def display_professors(self):
        with open(self.file, 'r', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                            print(row)

    def add_new_professor(self, login_csv, user: User, password, c_id, rank = None):
        exists = False
        with open(self.file, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)

                id_idx = 0
                if header and "professor_id" in header:
                    id_idx = header.index("professor_id")

                for row in reader:
                    if row and row[id_idx] == str(user.user_id):
                            exists = True
                            break
                    
        if exists:
                print(f"Professor ID {user.user_id} already exists. No record added.")
                return False
        with open(self.file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([user.user_id, user.email_address, user.first_name, user.last_name, c_id, rank if rank is not None else ""])
                    print(f"Professor {user.first_name} added successfully!")

        salt_hex = os.urandom(16).hex()
        lc = LoginCredential(login_csv)
        pwd_hash = lc.encrypt_password(password, salt_hex)

        with open(login_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Email", "Password", "Salt", "Role"])
            writer.writerow({
                "Email": user.email_address,
                "Password": pwd_hash,
                "Salt": salt_hex,
                "Role": "professor"
            })

        print(f"Professor {user.first_name} added successfully!")
        return True

    def delete_professor(self, professor_id):
        with open(self.file, 'r', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        idx_to_delete = None
        for i in range(1, len(rows)):
            if rows[i] and rows[i][0] == str(professor_id):
                idx_to_delete = i
                break

        if idx_to_delete is None:
            print(f"No professor found with ID {professor_id}. Delete aborted.")
            return False 

        # Remove the row and write back
        del rows[idx_to_delete]
        with open(self.file, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(rows)

        print("Professor deleted successfully!")
        return True

    def modify_professor_details(self, user: User, c_id= None, rank=None):
        rows = []
        found = False

        with open(self.file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == "professor_id":
                    rows.append(row)
                    continue

                if row and row[0] == str(user.user_id):
                    row[1] = user.email_address or row[1]
                    row[2] = user.first_name or row[2]
                    row[3] = user.last_name or row[3]
                    if c_id is not None:
                        row[4] = c_id       
                    if rank is not None:
                        row[5] = rank  
                    found = True

                rows.append(row)

        if not found:
            print(f"No professor found with ID {user.user_id}. Update skipped.")
            return False

        with open(self.file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        print("Professor record updated successfully!")
        return True

    def show_course_details_by_professor(self, professors_csv, courses_csv, professor_id):
        profs   = self.csv_to_json(professors_csv)
        courses = self.csv_to_json(courses_csv)

        course_by_id = {}
        for c in courses:
            key = c.get("course_id")
            if key is not None:
                course_by_id[key] = c

        prof = None
        for p in profs:
            if p.get("professor_id") == str(professor_id):
                prof = p
                break

        if prof is None:
            print(f"No professor found with ID {professor_id}.")
            return False

        print("Professor details:")
        print(json.dumps(prof, indent=2))
        print()

        cid = (prof.get("course_id") or "").strip()
        print("Matching course:")
        if cid and cid in course_by_id:
            print(json.dumps(course_by_id[cid], indent=2))
        elif cid:
            print(f"No course found with course_id = {cid}")
        else:
            print("Professor has no course id.")
        return True
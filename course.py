import csv

class Course:
    def __init__(self, file_path):
        self.file = file_path

    def display_courses(self):
        with open(self.file, 'r', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                            print(row)

    def add_new_course(self, course_id, name, credits, desc=None):
        exists = False
        with open(self.file, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)

                id_idx = 0
                if header and "course_id" in header:
                    id_idx = header.index("course_id")

                for row in reader:
                    if row and row[id_idx] == str(course_id):
                            exists = True
                            break
                    
        if exists:
                print(f"Course with ID: {course_id} already exists. No record added.")
                return False
        with open(self.file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([course_id, name, credits, desc if desc is not None else ""])
                    print(f"Course: {name} added successfully!")

    def delete_new_course(self, course_id):
         with open(self.file, 'r', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

            idx_to_delete = None
            for i in range(1, len(rows)):
                if rows[i] and rows[i][0] == str(course_id):
                    idx_to_delete = i
                    break

            if idx_to_delete is None:
                print(f"No course found with ID {course_id}. Delete aborted.")
                return False 

            # Remove the row and write back
            del rows[idx_to_delete]
            with open(self.file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(rows)

            print("Course deleted successfully!")
            return True
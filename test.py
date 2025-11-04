import os, csv, time, random, unittest
from student import Student
from professor import Professor
from course import Course
from user import User
from login import LoginCredential

# === CSV paths (current folder) ===
STUDENTS_CSV   = "students.csv"
PROFESSORS_CSV = "professors.csv"
COURSES_CSV    = "courses.csv"
LOGIN_CSV      = "login.csv"

def ensure_header(path, header):
    """Create the CSV with the given header if it doesn't exist or is empty."""
    if (not os.path.exists(path)) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header)

def read_all(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.reader(f))

class BasicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Make sure CSVs exist with the expected columns
        ensure_header(LOGIN_CSV,      ["Email", "Password", "Salt", "Role"])
        ensure_header(STUDENTS_CSV,   ["student_id", "email_address", "first_name", "last_name", "courses", "grade", "marks"])
        ensure_header(PROFESSORS_CSV, ["professor_id", "email_address", "first_name", "last_name", "course_id", "rank"])
        ensure_header(COURSES_CSV,    ["course_id", "course_name", "credits", "description"])

        # System-under-test
        cls.students  = Student(STUDENTS_CSV)
        cls.profs     = Professor(PROFESSORS_CSV)
        cls.courses   = Course(COURSES_CSV)
        cls.login     = LoginCredential(LOGIN_CSV)

        # Have at least one course available for enrollments
        try:
            cls.courses.add_new_course("C101", "Data 101", "4", "Follow-on course")
        except Exception:
            pass

        # ---- Seed students.csv to AT LEAST 1000 rows (persistent) ----
        random.seed(1)
        rows = read_all(STUDENTS_CSV)
        have = max(0, len(rows) - 1)
        need = 1000 - have
        for i in range(have + 1, have + need + 1):
            sid = str(i)
            email = f"student{i}@example.edu"
            first, last = f"FN{i}", f"LN{i}"
            marks = random.randint(0, 100)
            u = User(sid, email, first, last, "student")
            # OK if add_new_student returns True or None
            cls.students.add_new_student(LOGIN_CSV, u, password="pw", courses="C101",
                                         grade=("A" if marks > 90 else "B"), marks=marks)

    # 1) Students add/delete/modify (file must have >= 1000 records)
    def test_students_crud_basic(self):
        rows = read_all(STUDENTS_CSV)
        self.assertGreaterEqual(len(rows) - 1, 1000)

        header = rows[0]
        id_i     = header.index("student_id")
        email_i  = header.index("email_address")
        course_i = header.index("courses")
        grade_i  = header.index("grade")
        marks_i  = header.index("marks")

        # Modify a few known IDs if present
        for sid in ["1", "250", "500", "750", "1000"]:
            u = User(sid, f"updated{sid}@example.edu", f"NEW{sid}", f"LNEW{sid}", "student")
            try:
                self.students.update_student_record(u, courses="C102", grade="A", marks=99)
            except Exception:
                pass

        # Verify those updates where possible
        rows = read_all(STUDENTS_CSV)
        row_by_id = {r[id_i]: r for r in rows[1:] if r}
        for sid in ["1", "250", "500", "750", "1000"]:
            if sid in row_by_id:
                r = row_by_id[sid]
                self.assertEqual(r[email_i], f"updated{sid}@example.edu")
                self.assertEqual(r[course_i], "C102")
                self.assertEqual(r[grade_i], "A")
                self.assertEqual(str(r[marks_i]), "99")

        # Delete a few (keep overall count high)
        for sid in ["2", "4", "6", "8", "10"]:
            try:
                self.students.delete_new_student(sid)
            except Exception:
                pass

        rows = read_all(STUDENTS_CSV)
        ids_now = {r[id_i] for r in rows[1:] if r}
        for sid in ["2", "4", "6", "8", "10"]:
            self.assertNotIn(sid, ids_now)

    # 2) Load from CSV and search; print TOTAL search time
    def test_search_timing_basic(self):
        rows = read_all(STUDENTS_CSV)
        header = rows[0]
        id_col    = header.index("student_id")
        email_col = header.index("email_address")
        data = rows[1:]
        sample = data[:100] if len(data) >= 100 else data  # take first 100 for simplicity
        ids    = [r[id_col] for r in sample]
        emails = [r[email_col] for r in sample]

        def find_by_id(target):
            with open(STUDENTS_CSV, "r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row["student_id"] == target: return row
            return None

        def find_by_email(target):
            with open(STUDENTS_CSV, "r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row["email_address"] == target: return row
            return None

        t0 = time.perf_counter()
        for x in ids:    self.assertIsNotNone(find_by_id(x))
        t1 = time.perf_counter()
        for x in emails: self.assertIsNotNone(find_by_email(x))
        t2 = time.perf_counter()

        print(f"[SEARCH TIMING] total: {(t2 - t0):.6f} seconds")

    # 3) Sort by marks and email (asc/desc) and print timings
    def test_sort_timing_basic(self):
        rows = read_all(STUDENTS_CSV)
        header = rows[0]; data = rows[1:]
        marks_i = header.index("marks"); email_i = header.index("email_address")

        def m(row):
            try: return int(row[marks_i])
            except: return -1

        t0 = time.perf_counter(); _ = sorted(data, key=m); t1 = time.perf_counter()
        print(f"[SORT TIMING] marks asc: {(t1 - t0):.6f}s")

        t0 = time.perf_counter(); _ = sorted(data, key=m, reverse=True); t1 = time.perf_counter()
        print(f"[SORT TIMING] marks desc: {(t1 - t0):.6f}s")

        t0 = time.perf_counter(); _ = sorted(data, key=lambda r: r[email_i].lower()); t1 = time.perf_counter()
        print(f"[SORT TIMING] email asc: {(t1 - t0):.6f}s")

        t0 = time.perf_counter(); _ = sorted(data, key=lambda r: r[email_i].lower(), reverse=True); t1 = time.perf_counter()
        print(f"[SORT TIMING] email desc: {(t1 - t0):.6f}s")

    # 4) Course add/delete/modify (modify only if your class supports it)
    def test_course_crud_basic(self):
        # add
        try: self.courses.add_new_course("C100", "Data 100", "4", "Intro")
        except Exception: pass

        # modify (only if available)
        if hasattr(self.courses, "modify_course_details"):
            ok = self.courses.modify_course_details("C100", course_name="Data 100X", credits="5", description="Intro+")
            self.assertTrue(ok or ok is None)

        # delete
        self.assertTrue(self.courses.delete_new_course("C100"))

    # 5) Professor add/delete/modify
    def test_professor_crud_basic(self):
        # make sure a course exists
        try: self.courses.add_new_course("PX01", "Physics I", "3", "Basics")
        except Exception: pass

        # add
        p = User("P1", "prof1@example.edu", "Ada", "Lovelace", "professor")
        try: self.profs.add_new_professor(LOGIN_CSV, p, password="pw", c_id="PX01", rank="Assistant")
        except Exception: pass

        # modify (uses your method)
        p2 = User("P1", "prof1-new@example.edu", "Ada", "Lovelace", "professor")
        ok = self.profs.modify_professor_details(p2, c_id="PX01", rank="Associate")
        self.assertTrue(ok or ok is None)

        # delete
        self.assertTrue(self.profs.delete_professor("P1"))

if __name__ == "__main__":
    unittest.main(verbosity=2)

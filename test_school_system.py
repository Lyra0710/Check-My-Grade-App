import os
import csv
import time
import random
import unittest
from typing import List, Tuple

# ---- Your project modules ----
from student import Student
from professor import Professor
from course import Course
from user import User
from login import LoginCredential


# =============================
# Config / CSV paths (CWD)
# =============================
STUDENTS_CSV   = os.path.join(os.getcwd(), "students.csv")
PROFESSORS_CSV = os.path.join(os.getcwd(), "professors.csv")
COURSES_CSV    = os.path.join(os.getcwd(), "courses.csv")
LOGIN_CSV      = os.path.join(os.getcwd(), "login.csv")


# =============================
# Utilities
# =============================
def write_headers_if_missing(path: str, headers: List[str]) -> None:
    """Create CSV with headers if it doesn't exist or is empty."""
    needs_header = (not os.path.exists(path)) or os.path.getsize(path) == 0
    if needs_header:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)

def read_rows(path: str) -> list[list[str]]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.reader(f))

def index_by_header(header: List[str], name: str, default: int = 0) -> int:
    return header.index(name) if header and name in header else default

def gen_email(i: int) -> str:
    return f"student{i}@example.edu"

def gen_name(prefix: str, i: int) -> Tuple[str, str]:
    return f"{prefix}{i}", f"LN{i}"


# =============================
# Test Suite
# =============================
class SchoolSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """One-time setup: ensure headers, create SUTs, seed ≥1000 students."""
        random.seed(42)

        # Headers that match your implementations
        write_headers_if_missing(LOGIN_CSV,      ["Email", "Password", "Salt", "Role"])
        write_headers_if_missing(STUDENTS_CSV,   ["student_id", "email_address", "first_name", "last_name", "courses", "grade", "marks"])
        write_headers_if_missing(PROFESSORS_CSV, ["professor_id", "email_address", "first_name", "last_name", "course_id", "rank"])
        write_headers_if_missing(COURSES_CSV,    ["course_id", "course_name", "credits", "description"])

        # System-Under-Test instances
        cls.students  = Student(STUDENTS_CSV)
        cls.profs     = Professor(PROFESSORS_CSV)
        cls.courses   = Course(COURSES_CSV)
        cls.login     = LoginCredential(LOGIN_CSV)

        # Ensure at least one base course exists (used for enrollments)
        try:
            cls.courses.add_new_course("C101", "Data 101", "4", "Follow-on course")
        except Exception:
            # If your method dedupes internally or raises on duplicate, ignore.
            pass

        # -------- Seed to at least 1000 student rows (PERSISTENT) --------
        existing = read_rows(STUDENTS_CSV)
        current_n = max(0, len(existing) - 1)  # minus header
        target = 1000
        if current_n < target:
            start = current_n + 1
            for i in range(start, target + 1):
                sid = str(i)
                first, last = gen_name("FN", i)
                email = gen_email(i)
                marks = random.randint(0, 100)
                u = User(user_id=sid, email_address=email, first_name=first, last_name=last, role="student")
                # Be tolerant of different return conventions (True/None)
                try:
                    _ = cls.students.add_new_student(
                        LOGIN_CSV, u, password="p@ssw0rd", courses="C101",
                        grade=("A" if marks > 90 else "B"), marks=marks
                    )
                except Exception as e:
                    raise AssertionError(f"Failed to seed student {sid}: {e}") from e

    # --------------------------------------------------------------
    # 1) Students: add / delete / modify (with ≥1000 records)
    # --------------------------------------------------------------
    def test_students_crud_with_bulk_records(self):
        rows = read_rows(STUDENTS_CSV)
        self.assertGreaterEqual(len(rows) - 1, 1000, "students.csv must have at least 1000 records")

        header = rows[0]
        id_idx     = index_by_header(header, "student_id", 0)
        email_idx  = index_by_header(header, "email_address", 1)
        course_idx = index_by_header(header, "courses", 4)
        grade_idx  = index_by_header(header, "grade", 5)
        marks_idx  = index_by_header(header, "marks", 6)

        # --- Modify a handful of known IDs if present ---
        target_ids = ["1", "250", "500", "750", "1000"]
        present_ids = {r[id_idx] for r in rows[1:] if r}
        to_modify = [sid for sid in target_ids if sid in present_ids]
        for sid in to_modify:
            u = User(user_id=sid,
                     email_address=f"updated{sid}@example.edu",
                     first_name=f"NEW{sid}",
                     last_name=f"LNEW{sid}",
                     role="student")
            # Accept implementations that return True/None
            _ = self.students.update_student_record(u, courses="C102", grade="A", marks=99)

        # Verify modifications
        rows = read_rows(STUDENTS_CSV)
        row_map = {r[id_idx]: r for r in rows[1:] if r}
        for sid in to_modify:
            r = row_map[sid]
            self.assertEqual(r[email_idx], f"updated{sid}@example.edu")
            self.assertEqual(r[course_idx], "C102")
            self.assertEqual(r[grade_idx], "A")
            self.assertEqual(str(r[marks_idx]), "99")

        # --- Delete a few (keep overall count ≥1000) ---
        to_delete = ["2", "4", "6", "8", "10"]
        for sid in to_delete:
            try:
                _ = self.students.delete_new_student(sid)
            except Exception as e:
                self.fail(f"delete_new_student({sid}) raised: {e}")

        rows = read_rows(STUDENTS_CSV)
        ids = {r[id_idx] for r in rows[1:] if r}
        for sid in to_delete:
            self.assertNotIn(sid, ids)

    # ------------------------------------------------------------------
    # 2) Load data from CSV & search timing; print total search time
    # ------------------------------------------------------------------
    def test_load_and_search_timing(self):
        rows = read_rows(STUDENTS_CSV)
        self.assertGreater(len(rows), 1, "Need student rows to search")

        header = rows[0]
        id_idx    = index_by_header(header, "student_id", 0)
        email_idx = index_by_header(header, "email_address", 1)

        # Random sample of up to 100 rows
        data = rows[1:]
        sample = random.sample(data, min(100, len(data)))

        targets_by_id = [r[id_idx] for r in sample]
        targets_by_email = [r[email_idx] for r in sample]

        # Simple CSV scan search (matches “load previous runs” requirement)
        def find_by_id(target):
            with open(STUDENTS_CSV, "r", newline="", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                for row in rdr:
                    if row.get("student_id") == str(target):
                        return row
            return None

        def find_by_email(target):
            with open(STUDENTS_CSV, "r", newline="", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                for row in rdr:
                    if row.get("email_address") == target:
                        return row
            return None

        t0 = time.perf_counter()
        for t in targets_by_id:
            self.assertIsNotNone(find_by_id(t))
        t1 = time.perf_counter()
        for t in targets_by_email:
            self.assertIsNotNone(find_by_email(t))
        t2 = time.perf_counter()

        total_search_time = (t1 - t0) + (t2 - t1)
        # Printed timing = part of your “report”
        print(f"[SEARCH TIMING] Total for {len(targets_by_id)+len(targets_by_email)} searches: {total_search_time:.6f} seconds")

    # -----------------------------------------------------------------------
    # 3) Sort students by marks/email (asc/desc) and print timings
    # -----------------------------------------------------------------------
    def test_sort_students_by_marks_and_email_with_timing(self):
        rows = read_rows(STUDENTS_CSV)
        self.assertGreater(len(rows), 1, "Need student rows to sort")

        header = rows[0]
        data = rows[1:]
        marks_idx = index_by_header(header, "marks", 6)
        email_idx = index_by_header(header, "email_address", 1)

        def safe_mark(x):
            try:
                return int(x[marks_idx])
            except Exception:
                return -1

        # marks ascending
        t0 = time.perf_counter()
        by_marks_asc = sorted(data, key=safe_mark)
        t1 = time.perf_counter()
        print(f"[SORT TIMING] Marks ascending: {t1 - t0:.6f} seconds")

        # marks descending
        t2 = time.perf_counter()
        by_marks_desc = sorted(data, key=safe_mark, reverse=True)
        t3 = time.perf_counter()
        print(f"[SORT TIMING] Marks descending: {t3 - t2:.6f} seconds")

        # email ascending
        t4 = time.perf_counter()
        by_email_asc = sorted(data, key=lambda r: r[email_idx].lower())
        t5 = time.perf_counter()
        print(f"[SORT TIMING] Email ascending: {t5 - t4:.6f} seconds")

        # email descending
        t6 = time.perf_counter()
        by_email_desc = sorted(data, key=lambda r: r[email_idx].lower(), reverse=True)
        t7 = time.perf_counter()
        print(f"[SORT TIMING] Email descending: {t7 - t6:.6f} seconds")

        # sanity
        self.assertEqual(len(by_marks_asc), len(data))
        self.assertEqual(len(by_email_desc), len(data))

    # --------------------------------------------------------------
    # 4) Courses: add / delete / modify (if available)
    # --------------------------------------------------------------
    def test_courses_crud(self):
        # add
        add1 = self.courses.add_new_course("C100", "Data 100", "4", "Intro course")
        add2 = self.courses.add_new_course("C200", "Data 200", "4", "Advanced course")
        _ = (add1, add2)  # tolerate True/None returns

        # verify added
        rows = read_rows(COURSES_CSV)
        ids = {r[0] for r in rows[1:] if r}
        self.assertIn("C100", ids)
        self.assertIn("C200", ids)

        # modify (only if your Course exposes a modify API)
        if hasattr(self.courses, "modify_course_details"):
            ok = self.courses.modify_course_details("C200", course_name="Data 200X", credits="5", description="Advanced+")
            self.assertTrue(ok or ok is None)
            rows = read_rows(COURSES_CSV)
            row_map = {r[0]: r for r in rows[1:] if r}
            self.assertIn("C200", row_map)
        else:
            # If no modify method exists, at least assert idempotent re-add/delete works.
            pass

        # delete
        self.assertTrue(self._truthy(self.courses.delete_new_course("C100")))
        rows = read_rows(COURSES_CSV)
        ids = {r[0] for r in rows[1:] if r}
        self.assertNotIn("C100", ids)

    # --------------------------------------------------------------
    # 5) Professors: add / delete / modify
    # --------------------------------------------------------------
    def test_professors_crud(self):
        # ensure course exists for FK-like link
        try:
            self.courses.add_new_course("PX01", "Physics I", "3", "Basics")
        except Exception:
            pass

        # add
        u = User("P1", "prof1@example.edu", "Ada", "Lovelace", "professor")
        _ = self.profs.add_new_professor(LOGIN_CSV, u, password="s3cret", c_id="PX01", rank="Assistant")

        # modify
        u2 = User("P1", "prof1-new@example.edu", "Ada", "Lovelace", "professor")
        ok = self.profs.modify_professor_details(u2, c_id="PX01", rank="Associate")
        self.assertTrue(ok or ok is None)

        # verify modification
        rows = read_rows(PROFESSORS_CSV)
        header = rows[0]
        email_idx = index_by_header(header, "email_address", 1)
        rank_idx  = index_by_header(header, "rank", 5)
        row_map = {r[0]: r for r in rows[1:] if r}
        self.assertEqual(row_map["P1"][email_idx], "prof1-new@example.edu")
        self.assertEqual(row_map["P1"][rank_idx], "Associate")

        # delete
        self.assertTrue(self._truthy(self.profs.delete_professor("P1")))
        rows = read_rows(PROFESSORS_CSV)
        ids = {r[0] for r in rows[1:] if r}
        self.assertNotIn("P1", ids)

    # ----------------
    # small helper
    # ----------------
    @staticmethod
    def _truthy(val):
        """Some of your methods may return None instead of True; treat None as success in tests that don’t fail."""
        return True if (val is True or val is None) else bool(val)


if __name__ == "__main__":
    unittest.main(verbosity=2)

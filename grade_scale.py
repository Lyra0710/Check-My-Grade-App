from statistics import mean, median

class GradeScale:
    def __init__(self):
        self.records = []

    # ---- CRUD ----
    def add_grade(self, student_id, course, grade):
        self.records.append({"student_id": student_id, "course": course, "grade": grade})

    def delete_grade(self, student_id, course):
        self.records = [
            r for r in self.records
            if not (r["student_id"] == student_id and r["course"] == course)
        ]

    def modify_grade(self, student_id, course, new_grade):
        for r in self.records:
            if r["student_id"] == student_id and r["course"] == course:
                r["grade"] = new_grade
                return True
        print(f"'{student_id} - {course}' not found.")
        return False

    # ---- Stats ----
    def avg(self, course=None):
        g = [r["grade"] for r in self.records if course is None or r["course"] == course]
        return round(mean(g), 2) if g else None

    def med(self, course=None):
        g = [r["grade"] for r in self.records if course is None or r["course"] == course]
        return round(median(g), 2) if g else None

    # ---- Reports ----
    def _group(self, by): 
        if by == "student":
            by = "student_id"
        if by not in {"student_id", "course"}:
            raise ValueError("Group by must be 'student_id' or 'course'")
        groups = {}
        for r in self.records:
            groups.setdefault(r[by], []).append(r)
        return groups

    def display_grade_report(self, by="student_id"): 
        if by == "student":
            by = "student_id"

        if not self.records:
            print("=== Grade Report ===")
            print("(no records)")
            return

        groups = self._group(by)
        print(f"=== Grade Report (by {by}) ===")

        for key in sorted(groups, key=lambda k: (str(k).lower(), str(k))):
            rows = groups[key]
            grades = [r["grade"] for r in rows]
            a = round(mean(grades), 2)
            m = round(median(grades), 2)
            print(f"{key} -> avg: {a}, med: {m}")
            for r in sorted(rows, key=lambda x: (str(x["student_id"]).lower(), x["course"].lower())):
                print(f"  {r['student_id']} | {r['course']} | {r['grade']}")
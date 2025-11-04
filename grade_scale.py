from statistics import mean, median
'''The following code implements the required functionality for reports. 
It stores all the grades in a list of dictionaries (basically a memory table). 
It performs the CRUD operations like add, delete and modify grade. 
The statistics considered for the report are average, and median. 
The class also has a helper function '_groupby' (internal method) that groups student_id and course, and validates. 
Finally, the report is generated consisting of the stats (mean and median), and each row in the group. '''
class GradeScale:
    def __init__(self):
        self.records = []

    # ---- CRUD ----
    def add_grade(self, student_id, course, grade):
        self.records.append({"student_id": student_id, "course": course, "grade": grade})

    # basically rebuilding the records, excluding the matched record
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
        if by == "student": # Just in case there are any aliases
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
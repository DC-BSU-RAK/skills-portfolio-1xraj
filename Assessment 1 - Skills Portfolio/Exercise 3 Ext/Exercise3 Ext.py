import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from dataclasses import dataclass


# ------------------ Student ------------------
@dataclass
class Student:
    code: int
    name: str
    c1: int
    c2: int
    c3: int
    exam: int

    def cw(self) -> int:
        return self.c1 + self.c2 + self.c3

    def total(self) -> int:
        return self.cw() + self.exam

    def pct(self) -> float:
        return round((self.total() / 160) * 100, 2)

    def grade(self) -> str:
        p = self.pct()
        if p >= 70:
            return "A"
        if p >= 60:
            return "B"
        if p >= 50:
            return "C"
        if p >= 40:
            return "D"
        return "F"

    def to_line(self) -> str:
        return f"{self.code},{self.name},{self.c1},{self.c2},{self.c3},{self.exam}"


# ------------------ Store / Manager ------------------
class StudentStore:
    def __init__(self, path: str):
        self.path = path
        self.students: list[Student] = []
        self.by_code: dict[int, Student] = {}
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.path):
            open(self.path, "w", encoding="utf-8").close()

        with open(self.path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if lines and lines[0].isdigit():
            lines = lines[1:]

        parsed: list[Student] = []
        for ln in lines:
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) != 6:
                continue
            try:
                code, name, c1, c2, c3, exam = parts
                parsed.append(Student(int(code), name, int(c1), int(c2), int(c3), int(exam)))
            except ValueError:
                continue

        self.students = parsed
        self.by_code = {s.code: s for s in self.students}

    def save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(str(len(self.students)) + "\n")
            for s in self.students:
                f.write(s.to_line() + "\n")

    def add(self, s: Student) -> bool:
        if s.code in self.by_code:
            return False
        self.students.append(s)
        self.by_code[s.code] = s
        return True

    def delete(self, code: int) -> bool:
        s = self.by_code.get(code)
        if not s:
            return False
        self.students.remove(s)
        del self.by_code[code]
        return True


# ------------------ Add Student Popup ------------------
class AddStudentDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, on_submit):
        super().__init__(parent)
        self.title("Add Student")
        self.geometry("320x360")
        self.resizable(False, False)

        self.on_submit = on_submit
        self.entries: dict[str, tk.Entry] = {}

        fields = [("Code", True), ("Name", False), ("CW1", True), ("CW2", True), ("CW3", True), ("Exam", True)]
        for label, numeric in fields:
            row = tk.Frame(self)
            row.pack(fill="x", padx=12, pady=6)

            tk.Label(row, text=label, width=8, anchor="w", font=("Segoe UI", 10)).pack(side="left")
            e = tk.Entry(row, font=("Segoe UI", 10))
            e.pack(side="left", fill="x", expand=True)
            self.entries[label] = e

        tk.Button(
            self, text="Submit",
            bg="#4c57ff", fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.submit
        ).pack(pady=12)

        self.entries["Code"].focus()

    def submit(self):
        try:
            code = int(self.entries["Code"].get().strip())
            name = self.entries["Name"].get().strip()
            c1 = int(self.entries["CW1"].get().strip())
            c2 = int(self.entries["CW2"].get().strip())
            c3 = int(self.entries["CW3"].get().strip())
            exam = int(self.entries["Exam"].get().strip())

            if not name:
                messagebox.showerror("Error", "Name cannot be empty.")
                return

            if not (0 <= c1 <= 20 and 0 <= c2 <= 20 and 0 <= c3 <= 20 and 0 <= exam <= 100):
                messagebox.showerror("Error", "CW must be 0–20 each, Exam must be 0–100.")
                return

            self.on_submit(code, name, c1, c2, c3, exam)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")


# ------------------ App ------------------
class App(tk.Tk):
    def __init__(self, store: StudentStore):
        super().__init__()
        self.store = store
        self.sort_asc = True

        self.title("Student Manager - Table Edition")
        self.geometry("950x520")
        self.configure(bg="#f2f2f2")

        # Header
        tk.Label(
            self, text="Student Manager",
            bg="#4c57ff", fg="white",
            font=("Segoe UI", 18, "bold"),
            pady=10
        ).pack(fill="x")

        main = tk.Frame(self, bg="#f2f2f2")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT: Treeview table
        left = tk.Frame(main, bg="#f2f2f2")
        left.pack(side="left", fill="both", expand=True)

        cols = ("code", "name", "total", "pct", "grade")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
        self.tree.heading("code", text="Code")
        self.tree.heading("name", text="Name")
        self.tree.heading("total", text="Total /160")
        self.tree.heading("pct", text="%")
        self.tree.heading("grade", text="Grade")

        self.tree.column("code", width=80, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("total", width=100, anchor="center")
        self.tree.column("pct", width=80, anchor="center")
        self.tree.column("grade", width=80, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # RIGHT: Details panel
        right = tk.Frame(main, bg="white", bd=1, relief="solid")
        right.pack(side="right", fill="y", padx=(10, 0))

        tk.Label(right, text="Details", bg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        self.detail_vars = {k: tk.StringVar(value="") for k in ["Name", "Code", "Coursework", "Exam", "Total", "Percentage", "Grade"]}
        for k in ["Name", "Code", "Coursework", "Exam", "Total", "Percentage", "Grade"]:
            line = tk.Frame(right, bg="white")
            line.pack(fill="x", padx=12, pady=4)
            tk.Label(line, text=f"{k}:", bg="white", width=12, anchor="w", font=("Segoe UI", 10, "bold")).pack(side="left")
            tk.Label(line, textvariable=self.detail_vars[k], bg="white", anchor="w", font=("Segoe UI", 10)).pack(side="left")

        # Buttons row
        buttons = tk.Frame(self, bg="#f2f2f2")
        buttons.pack(fill="x", padx=10, pady=(0, 10))

        btn = dict(bg="#4c57ff", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=6)

        tk.Button(buttons, text="View All Summary", command=self.view_all_summary, **btn).pack(side="left", padx=4)
        tk.Button(buttons, text="Highest", command=self.show_highest, **btn).pack(side="left", padx=4)
        tk.Button(buttons, text="Lowest", command=self.show_lowest, **btn).pack(side="left", padx=4)
        tk.Button(buttons, text="Sort by Total", command=self.sort_by_total, **btn).pack(side="left", padx=4)
        tk.Button(buttons, text="Add Student", command=self.add_student, **btn).pack(side="left", padx=4)
        tk.Button(buttons, text="Delete Selected", command=self.delete_selected, **btn).pack(side="left", padx=4)

        self.refresh_table()

    # -------------- UI helpers --------------
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in self.store.students:
            self.tree.insert("", "end", iid=str(s.code),
                             values=(s.code, s.name, s.total(), s.pct(), s.grade()))

        self.clear_details()

    def clear_details(self):
        for v in self.detail_vars.values():
            v.set("")

    def set_details(self, s: Student):
        self.detail_vars["Name"].set(s.name)
        self.detail_vars["Code"].set(str(s.code))
        self.detail_vars["Coursework"].set(f"{s.cw()}/60")
        self.detail_vars["Exam"].set(f"{s.exam}/100")
        self.detail_vars["Total"].set(f"{s.total()}/160")
        self.detail_vars["Percentage"].set(f"{s.pct()}%")
        self.detail_vars["Grade"].set(s.grade())

    # -------------- Actions --------------
    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        code = int(sel[0])
        s = self.store.by_code.get(code)
        if s:
            self.set_details(s)

    def view_all_summary(self):
        if not self.store.students:
            messagebox.showinfo("Summary", "No students available.")
            return

        avg = round(sum(s.pct() for s in self.store.students) / len(self.store.students), 2)
        messagebox.showinfo(
            "Summary",
            f"Total Students: {len(self.store.students)}\nAverage Percentage: {avg}%"
        )

    def show_highest(self):
        if not self.store.students:
            return
        s = max(self.store.students, key=lambda x: x.total())
        self.tree.selection_set(str(s.code))
        self.tree.see(str(s.code))
        self.set_details(s)

    def show_lowest(self):
        if not self.store.students:
            return
        s = min(self.store.students, key=lambda x: x.total())
        self.tree.selection_set(str(s.code))
        self.tree.see(str(s.code))
        self.set_details(s)

    def sort_by_total(self):
        self.store.students.sort(key=lambda s: s.total(), reverse=not self.sort_asc)
        self.sort_asc = not self.sort_asc
        self.store.save()
        self.refresh_table()
        order = "ascending" if self.sort_asc else "descending"
        messagebox.showinfo("Sorted", f"Sorted by total score ({order}).")

    def add_student(self):
        AddStudentDialog(self, self._add_submit)

    def _add_submit(self, code, name, c1, c2, c3, exam):
        if code in self.store.by_code:
            messagebox.showerror("Error", "Code already exists.")
            return
        s = Student(code, name, c1, c2, c3, exam)
        self.store.add(s)
        self.store.save()
        self.refresh_table()
        messagebox.showinfo("Added", "Student added successfully.")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Please select a student row first.")
            return

        code = int(sel[0])
        if messagebox.askyesno("Confirm Delete", f"Delete student with code {code}?"):
            ok = self.store.delete(code)
            if ok:
                self.store.save()
                self.refresh_table()
                messagebox.showinfo("Deleted", "Student removed.")
            else:
                messagebox.showerror("Error", "Student not found.")


# ---------------- MAIN ----------------
def main():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "studentMarks.txt")
    store = StudentStore(path)
    App(store).mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import messagebox
from dataclasses import dataclass
import os

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

    def as_lines(self) -> list[str]:
        return [
            f"Name: {self.name}",
            f"Code: {self.code}",
            f"Coursework: {self.cw()}/60",
            f"Exam: {self.exam}/100",
            f"Total: {self.total()}/160",
            f"Percentage: {self.pct()}%",
            f"Grade: {self.grade()}",
        ]


# ------------------ Data Layer ------------------
class StudentStore:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.students: list[Student] = []
        self.by_code_map: dict[int, Student] = {}
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.filepath):
            messagebox.showerror("Error", f"File not found:\n{self.filepath}")
            self.students = []
            self.by_code_map = {}
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            self.students = []
            self.by_code_map = {}
            return

        # If first line is a number, treat it as "count" and skip it
        if lines[0].isdigit():
            lines = lines[1:]

        parsed: list[Student] = []
        for ln in lines:
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) != 6:
                continue
            code, name, c1, c2, c3, exam = parts
            try:
                s = Student(int(code), name, int(c1), int(c2), int(c3), int(exam))
                parsed.append(s)
            except ValueError:
                # skip bad lines
                continue

        self.students = parsed
        self.by_code_map = {s.code: s for s in self.students}

    def get(self, code: int) -> Student | None:
        return self.by_code_map.get(code)

    def highest(self) -> Student | None:
        return max(self.students, key=lambda s: s.total(), default=None)

    def lowest(self) -> Student | None:
        return min(self.students, key=lambda s: s.total(), default=None)


# ------------------ UI ------------------
class StudentApp(tk.Tk):
    def __init__(self, store: StudentStore):
        super().__init__()
        self.store = store

        self.title("Student Manager")
        self.geometry("900x520")
        self.configure(bg="#f2f2f2")

        # Header
        header = tk.Label(
            self,
            text="Student Manager",
            bg="#4c57ff",
            fg="white",
            font=("Segoe UI", 18, "bold"),
            pady=10,
        )
        header.pack(fill="x")

        # Layout
        body = tk.Frame(self, bg="#f2f2f2")
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel
        left = tk.Frame(body, bg="#f2f2f2")
        left.pack(side="left", fill="y")

        tk.Label(left, text="Students", font=("Segoe UI", 12, "bold"), bg="#f2f2f2").pack(anchor="w")

        self.listbox = tk.Listbox(left, width=34, height=22, font=("Segoe UI", 10))
        self.listbox.pack()
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Right panel
        right = tk.Frame(body, bg="#ffffff", bd=1, relief="solid")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            right,
            text="Selected Student",
            bg="#ffffff",
            font=("Segoe UI", 12, "bold"),
            pady=8
        ).pack(anchor="w", padx=10)

        # Output as StringVars (instead of a Text widget)
        self.lines_vars = [tk.StringVar(value="") for _ in range(7)]
        for v in self.lines_vars:
            tk.Label(
                right,
                textvariable=v,
                bg="#ffffff",
                font=("Segoe UI", 11),
                anchor="w",
                justify="left"
            ).pack(fill="x", padx=12, pady=2)

        # Search + Actions bar
        actions = tk.Frame(self, bg="#f2f2f2")
        actions.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(actions, text="Find by Code:", bg="#f2f2f2", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.search_entry = tk.Entry(actions, width=12, font=("Segoe UI", 10))
        self.search_entry.pack(side="left", padx=6)

        btn_style = dict(bg="#4c57ff", fg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=6)

        tk.Button(actions, text="Search", command=self.search_code, **btn_style).pack(side="left", padx=4)
        tk.Button(actions, text="View All", command=self.view_all_popup, **btn_style).pack(side="left", padx=4)
        tk.Button(actions, text="Highest", command=self.show_highest, **btn_style).pack(side="left", padx=4)
        tk.Button(actions, text="Lowest", command=self.show_lowest, **btn_style).pack(side="left", padx=4)
        tk.Button(actions, text="Reload File", command=self.reload, **btn_style).pack(side="right", padx=4)

        self.populate_list()
        self.show_message("Select a student from the list.")

    # ---------------- Helpers ----------------
    def populate_list(self) -> None:
        self.listbox.delete(0, "end")
        for s in self.store.students:
            self.listbox.insert("end", f"{s.code} - {s.name}")

    def show_student(self, s: Student) -> None:
        lines = s.as_lines()
        for i in range(len(self.lines_vars)):
            self.lines_vars[i].set(lines[i] if i < len(lines) else "")

    def show_message(self, msg: str) -> None:
        # Put message into the first line, clear others
        self.lines_vars[0].set(msg)
        for i in range(1, len(self.lines_vars)):
            self.lines_vars[i].set("")

    # ---------------- Events / Commands ----------------
    def on_select(self, event=None) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        s = self.store.students[idx]
        self.show_student(s)

    def search_code(self) -> None:
        raw = self.search_entry.get().strip()
        if not raw:
            messagebox.showinfo("Input needed", "Please enter a student code.")
            return
        if not raw.isdigit():
            messagebox.showerror("Invalid", "Student code must be a number.")
            return

        code = int(raw)
        s = self.store.get(code)
        if not s:
            messagebox.showinfo("Not Found", "No student with that code.")
            return

        self.show_student(s)

    def show_highest(self) -> None:
        s = self.store.highest()
        if not s:
            self.show_message("No student records available.")
            return
        self.show_student(s)

    def show_lowest(self) -> None:
        s = self.store.lowest()
        if not s:
            self.show_message("No student records available.")
            return
        self.show_student(s)

    def view_all_popup(self) -> None:
        if not self.store.students:
            messagebox.showinfo("No Data", "No student records available.")
            return

        total_pct = 0.0
        parts = []
        for s in self.store.students:
            parts.append("\n".join(s.as_lines()))
            parts.append("-" * 40)
            total_pct += s.pct()

        avg = round(total_pct / len(self.store.students), 2)
        parts.append(f"Total Students: {len(self.store.students)}")
        parts.append(f"Average Percentage: {avg}%")

        text = "\n".join(parts)

        # Popup window with scrollable text
        win = tk.Toplevel(self)
        win.title("All Students")
        win.geometry("650x450")

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        box = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set)
        box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=box.yview)

        box.insert("end", text)
        box.config(state="disabled")

    def reload(self) -> None:
        self.store.load()
        self.populate_list()
        self.show_message("Reloaded. Select a student from the list.")


# ---------------- Main ----------------
def main():
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studentMarks.txt")
    store = StudentStore(filepath)
    app = StudentApp(store)
    app.mainloop()


if __name__ == "__main__":
    main()

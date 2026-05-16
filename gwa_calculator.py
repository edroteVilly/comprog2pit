"""
GWA Calculator — Philippine 1.0–5.0 Grading System
Author : Group 6
Features: Add/remove subjects, live GWA, Pass/Fail per subject
UI      : Dark mode Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox

COLORS = {
    "bg":         "#0f1117",  # main window background
    "surface":    "#1a1d27",  # right panel and header bars
    "surface2":   "#242736",  # each subject row background
    "accent":     "#6c63ff",  # purple  — headers, buttons, highlights
    "accent2":    "#ff6584",  # pink    — Clear All and remove (✕) button
    "pass_color": "#00e5a0",  # green   — PASSED row and GWA when passing
    "fail_color": "#ff4d6d",  # red     — FAILED row and GWA when failing
    "text":       "#e8eaf6",  # normal white text
    "text_dim":   "#8b8fa8",  # dimmed grey text (labels, placeholders)
    "border":     "#2e3148",  # default row border color
    "header_bg":  "#12141f",  # top header strip background
    "entry_bg":   "#1e2133",  # input field background
    "entry_fg":   "#e8eaf6",  # input field text color
}

FONTS = {
    "title":   ("Consolas", 22, "bold"),  # app title in the header
    "body":    ("Consolas", 10),          # text inside entry fields
    "small":   ("Consolas", 9),           # column headers, stat labels, buttons
    "btn":     ("Consolas", 10, "bold"),  # Add Subject / Clear All buttons
    "gwa":     ("Consolas", 36, "bold"),  # the large GWA number
    "gwa_sub": ("Consolas", 11),          # Passing / Not Passing text
}

PASSING_GRADE = 3.0 
GRADE_MIN     = 1.0 
GRADE_MAX     = 5.0 

def compute_gwa(subjects: list) -> float:
    """
    Compute the General Weighted Average.
    Formula: GWA = sum(grade × units) / sum(units)
    Example: Math 1.5 × 3 units + English 2.0 × 3 units = 10.5 / 6 = 1.75
    Returns 0.0 if no valid subjects are given.
    """
    total_weighted = 0.0
    total_units    = 0.0
    for s in subjects:
        total_weighted += s["grade"] * s["units"]
        total_units    += s["units"]
    return round(total_weighted / total_units, 4) if total_units else 0.0

def is_passing(grade: float) -> bool:
    """Return True if the grade is within the passing range (1.0 – 3.0)."""
    return GRADE_MIN <= grade <= PASSING_GRADE

def gwa_remark(gwa: float) -> str:
    """Return 'Passing' or 'Not Passing' based on the computed GWA."""
    return "Passing" if gwa <= PASSING_GRADE else "Not Passing"

class SubjectRow:
    """
    Builds and manages one subject row: row number, subject name entry,
    units entry, grade entry, status label (PASSED/FAILED), remove button.
    Uses grid() layout so every column stays aligned across all rows.
    """

    def __init__(self, parent, index: int, on_change, on_remove):
        """
        parent    — the scrollable frame to place this row inside
        index     — the row number (0-based) used for the label
        on_change — callback fired every time the user edits anything
        on_remove — callback fired when the user clicks ✕
        """
        self.index     = index
        self.on_change = on_change
        self.on_remove = on_remove
        self._build(parent)

    def _build(self, parent):
        self.frame = tk.Frame(
            parent, bg=COLORS["surface2"],
            highlightbackground=COLORS["border"], highlightthickness=1
        )
        self.frame.pack(fill="x", padx=10, pady=3)

        self.num_label = tk.Label(
            self.frame, text=f"{self.index + 1:02d}",
            bg=COLORS["surface2"], fg=COLORS["accent"],
            font=FONTS["small"], width=3
        )
        self.num_label.grid(row=0, column=0, padx=(8, 4), pady=8)

        self.name_var = tk.StringVar()
        name_entry = tk.Entry(
            self.frame, textvariable=self.name_var,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["accent"],
            relief="flat", font=FONTS["body"], width=24,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        name_entry.grid(row=0, column=1, padx=4, pady=8, sticky="w")
        self.name_var.trace_add("write", lambda *_: self.on_change())
        self._placeholder(name_entry, "optional")

        vcmd = (self.frame.register(self._validate_units), "%P")
        self.units_var = tk.StringVar()
        tk.Entry(
            self.frame, textvariable=self.units_var,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["accent"],
            relief="flat", font=FONTS["body"], width=3,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            validate="key", validatecommand=vcmd
        ).grid(row=0, column=2, padx=4, pady=8)
        self.units_var.set("3")
        self.units_var.trace_add("write", lambda *_: self.on_change())

        vcmd2 = (self.frame.register(self._validate_grade), "%P")
        self.grade_var = tk.StringVar()
        grade_entry = tk.Entry(
            self.frame, textvariable=self.grade_var,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["accent"],
            relief="flat", font=FONTS["body"], width=6,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            validate="key", validatecommand=vcmd2
        )
        grade_entry.grid(row=0, column=3, padx=4, pady=8)
        self.grade_var.trace_add("write", lambda *_: self.on_change())
        self._placeholder(grade_entry, "e.g. 1.5")

        self.status_label = tk.Label(
            self.frame, text="  —  ",
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            font=FONTS["small"], width=10, anchor="center"
        )
        self.status_label.grid(row=0, column=4, padx=8, pady=8)

        tk.Button(
            self.frame, text="✕",
            bg=COLORS["surface2"], fg=COLORS["accent2"],
            activebackground=COLORS["accent2"], activeforeground="#fff",
            relief="flat", font=FONTS["small"],
            cursor="hand2", command=self.on_remove, padx=6
        ).grid(row=0, column=5, padx=(4, 8), pady=8)

    @staticmethod
    def _validate_units(value: str) -> bool:
        """
        Called by Tkinter on every keystroke in the Units field.
        Allows only a single digit from 1–9. Blocks everything else.
        %P = the value the entry WOULD have if this keystroke is accepted.
        """
        if value == "":
            return True           
        return value.isdigit() and len(value) == 1 and value != "0"

    @staticmethod
    def _validate_grade(value: str) -> bool:
        """
        Called by Tkinter on every keystroke in the Grade field.
        Allows partial float input like '1', '1.', '1.5' as long as
        the value is within 1.0–5.0 range when complete.
        Blocks anything that can't be part of a valid grade number.
        """
        if value == "":
            return True           
        try:
            f = float(value)
            return f <= GRADE_MAX 
        except ValueError:
            return value.endswith(".") and value.count(".") == 1

    def _placeholder(self, entry: tk.Entry, text: str):
        """
        Show dimmed hint text when the entry is empty.
        Disappears when the user clicks in, reappears if left empty.
        """
        def on_focus_in(_):
            if entry.get() == text:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS["entry_fg"])

        def on_focus_out(_):
            if entry.get().strip() == "":
                entry.insert(0, text)
                entry.config(fg=COLORS["text_dim"])

        entry.insert(0, text)
        entry.config(fg=COLORS["text_dim"])
        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def get_data(self) -> dict | None:
        """
        Read this row's current entries.
        Returns a dict with 'name', 'units', 'grade' if both units and grade
        are valid numbers, or None if the row is incomplete.
        """
        PLACEHOLDERS = {"optional", "e.g. 1.5"}
        grade_str = self.grade_var.get().strip()
        units_str = self.units_var.get().strip()

        if grade_str in PLACEHOLDERS:
            grade_str = ""

        if not units_str or not grade_str:
            return None
        try:
            units = float(units_str)
            grade = float(grade_str)
            if not (GRADE_MIN <= grade <= GRADE_MAX):
                return None
        except ValueError:
            return None

        return {
            "name":  self.name_var.get().strip(),
            "units": units,
            "grade": grade,
        }

    def update_status(self):
        """
        Update the PASSED / FAILED label and the row border color
        based on the current grade. Shows '—' if grade is not yet valid.
        """
        data = self.get_data()
        if data is None:
            self.status_label.config(text="  —  ", fg=COLORS["text_dim"], bg=COLORS["surface2"])
            self.frame.config(highlightbackground=COLORS["border"])
        elif is_passing(data["grade"]):
            self.status_label.config(text=" PASSED ", fg=COLORS["pass_color"], bg="#0a2e22")
            self.frame.config(highlightbackground=COLORS["pass_color"])
        else:
            self.status_label.config(text=" FAILED ", fg=COLORS["fail_color"], bg="#2e0a14")
            self.frame.config(highlightbackground=COLORS["fail_color"])

    def set_index(self, index: int):
        """Renumber this row's label (called after a row above it is removed)."""
        self.index = index
        self.num_label.config(text=f"{index + 1:02d}")

    def destroy(self):
        """Remove this row's frame from the screen."""
        self.frame.destroy()

class GWACalculatorApp:
    """
    Owns the main window and manages all SubjectRow objects.
    Handles: building the UI, adding/removing rows, recomputing the GWA.
    """

    def __init__(self, root: tk.Tk):
        self.root         = root
        self.rows: list   = [] 
        self._setup_window()
        self._build_ui()
        self._add_row()
        self._add_row()
        self._add_row()

    def _setup_window(self):
        """Configure the main window: title, size, color, center on screen."""
        self.root.title("GWA Calculator")
        self.root.geometry("900x600")
        self.root.minsize(780, 420)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 450
        y = (self.root.winfo_screenheight() // 2) - 300
        self.root.geometry(f"780x600+{x}+{y}")

    def _build_ui(self):
        """Build the full window layout: header, left table area, right GWA panel."""

        header = tk.Frame(self.root, bg=COLORS["header_bg"], pady=14)
        header.pack(fill="x")
        tk.Label(header, text="◈  GWA CALCULATOR",
                 bg=COLORS["header_bg"], fg=COLORS["accent"],
                 font=FONTS["title"]).pack(side="left", padx=20)

        body  = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)

        left  = tk.Frame(body, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg=COLORS["surface"], width=210)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        btn_row = tk.Frame(left, bg=COLORS["bg"], pady=8)
        btn_row.pack(fill="x", padx=10, pady=(10, 0))
        self._btn(btn_row, "+ Add Subject", self._add_row,   COLORS["accent"]).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "⊘ Clear All",   self._clear_all, COLORS["accent2"]).pack(side="left")

        col_header = tk.Frame(left, bg=COLORS["surface"], pady=7)
        col_header.pack(fill="x", padx=10, pady=(6, 0))
        for text, w in [("#", 3), ("Subject Name", 22), ("Units *", 7), ("Grade (1–5) *", 12), ("Status", 10)]:
            tk.Label(col_header, text=text,
                     bg=COLORS["surface"], fg=COLORS["accent"],
                     font=FONTS["small"], width=w, anchor="w").pack(side="left", padx=4)
        tk.Label(col_header, text="* required",
                 bg=COLORS["surface"], fg=COLORS["accent2"],
                 font=FONTS["small"]).pack(side="right", padx=10)

        self.canvas = tk.Canvas(left, bg=COLORS["bg"], highlightthickness=0)
        scrollbar   = ttk.Scrollbar(left, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=4)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units")
        )

        self._build_right_panel(right)

    def _build_right_panel(self, parent):
        """Build the GWA display and summary stats in the right panel."""
        tk.Label(parent, text="YOUR GWA",
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 font=FONTS["small"]).pack(pady=(30, 2))

        self.gwa_label = tk.Label(parent, text="—",
                                  bg=COLORS["surface"], fg=COLORS["accent"],
                                  font=FONTS["gwa"])
        self.gwa_label.pack()

        self.remark_label = tk.Label(parent, text="Enter grades to\ncompute",
                                     bg=COLORS["surface"], fg=COLORS["text_dim"],
                                     font=FONTS["gwa_sub"], justify="center")
        self.remark_label.pack(pady=(4, 16))

        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=16)

        stats = tk.Frame(parent, bg=COLORS["surface"], pady=12)
        stats.pack(fill="x", padx=20)
        self.lbl_units   = self._stat(stats, "Total Units",   "—")
        self.lbl_count   = self._stat(stats, "Subjects",      "—")
        self.lbl_passed  = self._stat(stats, "Passed",        "—", COLORS["pass_color"])
        self.lbl_failed  = self._stat(stats, "Failed",        "—", COLORS["fail_color"])
        self.lbl_highest = self._stat(stats, "Highest Grade", "—")
        self.lbl_lowest  = self._stat(stats, "Lowest Grade",  "—")

        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=10)

        leg = tk.Frame(parent, bg=COLORS["surface"])
        leg.pack(padx=20, anchor="w")
        for line, color in [("1.0 = Excellent", COLORS["text_dim"]),
                             ("3.0 = Passing (max)", COLORS["text_dim"]),
                             ("5.0 = Failed", COLORS["fail_color"])]:
            tk.Label(leg, text=line, bg=COLORS["surface"],
                     fg=color, font=FONTS["small"]).pack(anchor="w")

    def _stat(self, parent, label: str, value: str, color=None) -> tk.Label:
        """Create one 'Label: Value' row in the stats panel. Returns the value label."""
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label + ":", bg=COLORS["surface"],
                 fg=COLORS["text_dim"], font=FONTS["small"]).pack(side="left")
        lbl = tk.Label(row, text=value, bg=COLORS["surface"],
                       fg=color or COLORS["text"], font=FONTS["small"])
        lbl.pack(side="right")
        return lbl

    def _btn(self, parent, text: str, command, color: str) -> tk.Button:
        """Create a styled flat button and return it (not yet packed)."""
        return tk.Button(parent, text=text, command=command,
                         bg=color, fg="#fff",
                         activebackground=COLORS["bg"], activeforeground=color,
                         relief="flat", font=FONTS["btn"],
                         padx=12, pady=5, cursor="hand2", highlightthickness=0)

    def _add_row(self):
        """Add one new empty subject row to the table."""
        uid = len(self.rows)
        row = SubjectRow(
            parent    = self.scroll_frame,
            index     = uid,
            on_change = self._refresh,
            on_remove = lambda u=uid: self._remove_row(u)
        )
        row._uid = uid
        self.rows.append(row)
        self._refresh()

    def _remove_row(self, uid: int):
        """Find the row with the given uid, remove it, then renumber the rest."""
        target = next((r for r in self.rows if r._uid == uid), None)
        if target is None:
            return
        if len(self.rows) <= 1:
            messagebox.showwarning("Cannot Remove", "Keep at least one subject row.")
            return
        target.destroy()
        self.rows.remove(target)
        for i, r in enumerate(self.rows):
            r.set_index(i)
        self._refresh()

    def _clear_all(self):
        """Ask for confirmation then reset the table to 3 empty rows."""
        if not messagebox.askyesno("Clear All", "Remove all subjects and start fresh?"):
            return
        for r in self.rows:
            r.destroy()
        self.rows.clear()
        self._add_row()
        self._add_row()
        self._add_row()

    def _refresh(self):
        """
        Called every time any entry changes.
        Collects valid rows, recomputes the GWA, and updates all panel labels.
        """
        valid = []
        for row in self.rows:
            row.update_status()     
            data = row.get_data()
            if data:                
                valid.append(data)

        if not valid:
            self.gwa_label.config(text="—", fg=COLORS["accent"])
            self.remark_label.config(text="Enter grades to\ncompute", fg=COLORS["text_dim"])
            for lbl in [self.lbl_units, self.lbl_count, self.lbl_passed,
                        self.lbl_failed, self.lbl_highest, self.lbl_lowest]:
                lbl.config(text="—")
            return

        gwa    = compute_gwa(valid)
        color  = COLORS["pass_color"] if gwa <= PASSING_GRADE else COLORS["fail_color"]
        grades = [s["grade"] for s in valid]
        passed = sum(1 for g in grades if is_passing(g))

        self.gwa_label.config(text=f"{gwa:.4f}", fg=color)
        self.remark_label.config(text=gwa_remark(gwa), fg=color)
        self.lbl_units.config(text=f"{sum(s['units'] for s in valid):.1f}")
        self.lbl_count.config(text=str(len(valid)))
        self.lbl_passed.config(text=str(passed))
        self.lbl_failed.config(text=str(len(valid) - passed))
        self.lbl_highest.config(text=f"{min(grades):.2f}")
        self.lbl_lowest.config(text=f"{max(grades):.2f}")

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background=COLORS["surface2"], troughcolor=COLORS["bg"],
                    arrowcolor=COLORS["accent"],   bordercolor=COLORS["border"])
    GWACalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
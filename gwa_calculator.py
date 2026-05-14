"""
GWA Calculator - Philippine 1.0–5.0 Grading System
Author: Group 6
Features: Add/remove subjects dynamically, live GWA computation, Pass/Fail status
UI: Dark mode Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

COLORS = {
    "bg":          "#0f1117",
    "surface":     "#1a1d27",
    "surface2":    "#242736",
    "accent":      "#6c63ff",
    "accent2":     "#ff6584",
    "pass_color":  "#00e5a0",
    "fail_color":  "#ff4d6d",
    "text":        "#e8eaf6",
    "text_dim":    "#8b8fa8",
    "border":      "#2e3148",
    "header_bg":   "#12141f",
    "entry_bg":    "#1e2133",
    "entry_fg":    "#e8eaf6",
}

FONTS = {
    "title":   ("Consolas", 22, "bold"),
    "subtitle":("Consolas", 10),
    "body":    ("Consolas", 10),
    "small":   ("Consolas", 9),
    "btn":     ("Consolas", 10, "bold"),
    "gwa":     ("Consolas", 36, "bold"),
    "gwa_sub": ("Consolas", 11),
}

PASSING_GRADE = 3.0   # Philippine standard: 3.0 or lower = passing


# ─── UTILITY FUNCTIONS ────────────────────────────────────────────────────────

def compute_gwa(subjects: list) -> float:
    """
    Compute the General Weighted Average (GWA).
    Formula: GWA = sum(grade * units) / sum(units)
    Returns the GWA rounded to 4 decimal places, or 0.0 if no valid data.
    """
    total_weighted = 0.0
    total_units    = 0.0

    for subj in subjects:
        grade = subj.get("grade")
        units = subj.get("units")
        if grade is not None and units is not None:
            try:
                total_weighted += float(grade) * float(units)
                total_units    += float(units)
            except (ValueError, TypeError):
                pass

    if total_units == 0:
        return 0.0
    return round(total_weighted / total_units, 4)


def is_passing(grade: float) -> bool:
    """Return True if grade is passing (1.0 to 3.0 in PH system)."""
    return 1.0 <= grade <= PASSING_GRADE


def gwa_remark(gwa: float) -> str:
    """Return Passing or Not Passing based on the GWA."""
    if gwa == 0.0:
        return "—"
    return "Passing" if gwa <= PASSING_GRADE else "Not Passing"


def validate_grade(value: str) -> tuple:
    """
    Validate a grade string. Must be a float between 1.0 and 5.0.
    Returns (is_valid: bool, grade: float or None, error_msg: str)
    """
    try:
        g = float(value)
        if not (1.0 <= g <= 5.0):
            return False, None, "Grade must be between 1.0 and 5.0"
        return True, g, ""
    except ValueError:
        return False, None, "Grade must be a number (e.g. 1.5, 2.0)"


def validate_units(value: str) -> tuple:
    """
    Validate a units string. Must be a positive number.
    Returns (is_valid: bool, units: float or None, error_msg: str)
    """
    try:
        u = float(value)
        if u <= 0:
            return False, None, "Units must be greater than 0"
        return True, u, ""
    except ValueError:
        return False, None, "Units must be a number (e.g. 3, 1.5)"


# ─── SUBJECT ROW WIDGET ───────────────────────────────────────────────────────

class SubjectRow:
    """
    A single subject row containing:
      - Row number, Subject Name entry, Units entry, Grade entry,
        Status label (PASSED / FAILED), Remove button.
    Uses grid layout so all columns stay aligned.
    """

    def __init__(self, parent_frame, index: int, on_change_callback, on_remove_callback):
        self.parent_frame = parent_frame
        self.index        = index
        self.on_change    = on_change_callback
        self.on_remove    = on_remove_callback
        self._build_row()

    def _build_row(self):
        self.frame = tk.Frame(
            self.parent_frame,
            bg=COLORS["surface2"],
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        self.frame.pack(fill="x", padx=10, pady=3)

        # ── Col 0: Row number ──
        self.num_label = tk.Label(
            self.frame,
            text=f"{self.index + 1:02d}",
            bg=COLORS["surface2"], fg=COLORS["accent"],
            font=FONTS["small"], width=3, anchor="center"
        )
        self.num_label.grid(row=0, column=0, padx=(8, 4), pady=8)

        # ── Col 1: Subject name (optional) ──
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            self.frame, textvariable=self.name_var,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["accent"],
            relief="flat", font=FONTS["body"], width=24,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        self.name_entry.grid(row=0, column=1, padx=4, pady=8, sticky="w")
        self.name_var.trace_add("write", lambda *_: self.on_change())
        self._add_placeholder(self.name_entry, "optional")

        # ── Col 2: Units (required, numbers only) ──
        # vcmd registers a validation command with Tkinter.
        # "%P" is a special Tkinter substitution that passes the
        # value the entry WOULD have after the keystroke, so we
        # can reject it before it appears if it isn't numeric.
        vcmd_units = (self.frame.register(self._only_numbers), "%P")
        self.units_var = tk.StringVar()
        self.units_entry = tk.Entry(
            self.frame, textvariable=self.units_var,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["accent"],
            relief="flat", font=FONTS["body"], width=6,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            validate="key", validatecommand=vcmd_units
        )
        self.units_entry.grid(row=0, column=2, padx=4, pady=8)
        self.units_var.set("3")   # default: most subjects are 3 units
        self.units_var.trace_add("write", lambda *_: self.on_change())

        # ── Col 3: Grade (required, numbers only) ──
        vcmd_grade = (self.frame.register(self._only_numbers), "%P")
        self.grade_var = tk.StringVar()
        self.grade_entry = tk.Entry(
            self.frame, textvariable=self.grade_var,
            bg=COLORS["entry_bg"], fg=COLORS["entry_fg"],
            insertbackground=COLORS["accent"],
            relief="flat", font=FONTS["body"], width=8,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            validate="key", validatecommand=vcmd_grade
        )
        self.grade_entry.grid(row=0, column=3, padx=4, pady=8)
        self.grade_var.trace_add("write", lambda *_: self.on_change())
        self._add_placeholder(self.grade_entry, "e.g. 1.5")

        # ── Col 4: Status (PASSED / FAILED / —) ──
        self.status_label = tk.Label(
            self.frame, text="  —  ",
            bg=COLORS["surface2"], fg=COLORS["text_dim"],
            font=FONTS["small"], width=10, anchor="center"
        )
        self.status_label.grid(row=0, column=4, padx=8, pady=8)

        # ── Col 5: Remove button ──
        remove_btn = tk.Button(
            self.frame, text="✕",
            bg=COLORS["surface2"], fg=COLORS["accent2"],
            activebackground=COLORS["accent2"],
            activeforeground="#ffffff",
            relief="flat", font=FONTS["small"],
            cursor="hand2", command=self.on_remove,
            padx=6, pady=2
        )
        remove_btn.grid(row=0, column=5, padx=(4, 8), pady=8)

    def get_data(self) -> dict:
        """Return this row's current values as a dict."""
        # Ignore placeholder text (dimmed hint shown when entry is empty)
        PLACEHOLDERS = {"optional", "e.g. 1.5"}
        raw_name  = self.name_var.get().strip()
        raw_units = self.units_var.get().strip()
        raw_grade = self.grade_var.get().strip()
        name      = "" if raw_name  in PLACEHOLDERS else raw_name
        units_str = "" if raw_units in PLACEHOLDERS else raw_units
        grade_str = "" if raw_grade in PLACEHOLDERS else raw_grade

        valid_u, units, _ = validate_units(units_str) if units_str else (False, None, "")
        valid_g, grade, _ = validate_grade(grade_str) if grade_str else (False, None, "")

        return {
            "name":        name,
            "units":       units if valid_u else None,
            "grade":       grade if valid_g else None,
            "units_str":   units_str,
            "grade_str":   grade_str,
            "valid_units": valid_u,
            "valid_grade": valid_g,
        }

    def set_data(self, name: str, units, grade):
        """Pre-fill this row's entries with data."""
        self.name_var.set(str(name) if name is not None else "")
        self.units_var.set(str(units) if units is not None else "")
        self.grade_var.set(str(grade) if grade is not None else "")

    def set_index(self, index: int):
        """Update the displayed row number."""
        self.index = index
        self.num_label.config(text=f"{index + 1:02d}")

    def update_status(self):
        """Refresh the PASSED / FAILED label based on the current grade entry."""
        data  = self.get_data()
        grade = data.get("grade")

        if grade is not None and data["valid_grade"]:
            if is_passing(grade):
                self.status_label.config(
                    text=" PASSED ", fg=COLORS["pass_color"], bg="#0a2e22"
                )
                self.frame.config(highlightbackground=COLORS["pass_color"])
            else:
                self.status_label.config(
                    text=" FAILED ", fg=COLORS["fail_color"], bg="#2e0a14"
                )
                self.frame.config(highlightbackground=COLORS["fail_color"])
        else:
            self.status_label.config(
                text="  —  ", fg=COLORS["text_dim"], bg=COLORS["surface2"]
            )
            self.frame.config(highlightbackground=COLORS["border"])

    @staticmethod
    def _only_numbers(value: str) -> bool:
        """
        Validation function for Units and Grade entries.
        Called by Tkinter on every keystroke via validatecommand.
        Returns True to allow the keystroke, False to block it.
        Allows: digits, a single decimal point, and an empty field.
        """
        if value == "":
            return True          # allow clearing the field
        try:
            float(value)         # valid number so far (e.g. "1", "1.", "1.5")
            return True
        except ValueError:
            return False         # reject anything that can't be part of a number

    def _add_placeholder(self, entry: tk.Entry, text: str):
        """
        Show dimmed placeholder text inside an entry when it is empty.
        Clears on focus-in, restores on focus-out if still empty.
        """
        def on_focus_in(e):
            if entry.get() == text:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS["entry_fg"])

        def on_focus_out(e):
            if entry.get().strip() == "":
                entry.insert(0, text)
                entry.config(fg=COLORS["text_dim"])

        entry.insert(0, text)
        entry.config(fg=COLORS["text_dim"])
        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def destroy(self):
        """Remove this row's frame from the UI."""
        self.frame.destroy()


# ─── MAIN APPLICATION ─────────────────────────────────────────────────────────

class GWACalculatorApp:
    """Main GWA Calculator Tkinter Application."""

    def __init__(self, root: tk.Tk):
        self.root         = root
        self.subject_rows = []
        self._setup_window()
        self._build_ui()
        # Start with 3 empty subject rows
        self._add_subject()
        self._add_subject()
        self._add_subject()

    # ── Window Setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        self.root.title("GWA Calculator — Philippine 1.0–5.0 Scale")
        self.root.geometry("820x620")
        self.root.minsize(700, 420)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        # Center on screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw // 2) - (820 // 2)
        y  = (sh // 2) - (620 // 2)
        self.root.geometry(f"820x620+{x}+{y}")

    # ── UI Builder ────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg=COLORS["header_bg"], pady=14)
        header.pack(fill="x")

        tk.Label(
            header, text="◈  GWA CALCULATOR",
            bg=COLORS["header_bg"], fg=COLORS["accent"],
            font=FONTS["title"]
        ).pack(side="left", padx=20)

        tk.Label(
            header, text="Philippine 1.0 – 5.0 Grading System",
            bg=COLORS["header_bg"], fg=COLORS["text_dim"],
            font=FONTS["subtitle"]
        ).pack(side="left", padx=6)

        # ── Body: Left (subject list) + Right (GWA panel) ──
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)

        left  = tk.Frame(body, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg=COLORS["surface"], width=220)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # ── Add Subject + Clear All buttons (above column headers) ──
        btn_row = tk.Frame(left, bg=COLORS["bg"], pady=8)
        btn_row.pack(fill="x", padx=10, pady=(10, 0))

        self._make_btn(
            btn_row, "+ Add Subject", self._add_subject, COLORS["accent"]
        ).pack(side="left", padx=(0, 8))

        self._make_btn(
            btn_row, "⊘ Clear All", self._clear_all, COLORS["accent2"]
        ).pack(side="left")

        # ── Column headers (match SubjectRow grid columns) ──
        col_header = tk.Frame(left, bg=COLORS["surface"], pady=7)
        col_header.pack(fill="x", padx=10, pady=(6, 0))

        # Columns marked with * are required
        col_defs = [
            ("#",              3),
            ("Subject Name",  24),
            ("Units *",        6),
            ("Grade (1–5) *",  8),
            ("Status",        10),
        ]
        for text, w in col_defs:
            tk.Label(
                col_header, text=text,
                bg=COLORS["surface"], fg=COLORS["accent"],
                font=FONTS["small"], width=w, anchor="w"
            ).pack(side="left", padx=4)

        # Legend: explain the * marker
        tk.Label(
            col_header, text="  * required",
            bg=COLORS["surface"], fg=COLORS["accent2"],
            font=FONTS["small"]
        ).pack(side="right", padx=10)

        # ── Scrollable subject list ──
        self.canvas = tk.Canvas(left, bg=COLORS["bg"], highlightthickness=0)
        scrollbar   = ttk.Scrollbar(left, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=4)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scroll
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units")
        )

        # ── Right panel: GWA display + stats ──
        self._build_right_panel(right)

    def _build_right_panel(self, parent):
        """Build the GWA display and summary statistics on the right side."""
        tk.Label(
            parent, text="YOUR GWA",
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            font=FONTS["small"]
        ).pack(pady=(30, 2))

        self.gwa_label = tk.Label(
            parent, text="—",
            bg=COLORS["surface"], fg=COLORS["accent"],
            font=FONTS["gwa"]
        )
        self.gwa_label.pack()

        self.remark_label = tk.Label(
            parent, text="Enter grades to\ncompute",
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            font=FONTS["gwa_sub"], wraplength=200, justify="center"
        )
        self.remark_label.pack(pady=(6, 20))

        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=16)

        # ── Stats ──
        stats = tk.Frame(parent, bg=COLORS["surface"], pady=14)
        stats.pack(fill="x", padx=20)

        self.total_units_label = self._stat_row(stats, "Total Units",   "—")
        self.total_subj_label  = self._stat_row(stats, "Subjects",      "—")
        self.passed_label      = self._stat_row(stats, "Passed",        "—", COLORS["pass_color"])
        self.failed_label      = self._stat_row(stats, "Failed",        "—", COLORS["fail_color"])
        self.highest_label     = self._stat_row(stats, "Highest Grade", "—")
        self.lowest_label      = self._stat_row(stats, "Lowest Grade",  "—")

        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=12)

        # ── Grade scale legend ──
        leg = tk.Frame(parent, bg=COLORS["surface"])
        leg.pack(padx=20, anchor="w")
        tk.Label(leg, text="1.0 = Excellent",
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 font=FONTS["small"]).pack(anchor="w")
        tk.Label(leg, text="3.0 = Passing (max)",
                 bg=COLORS["surface"], fg=COLORS["text_dim"],
                 font=FONTS["small"]).pack(anchor="w")
        tk.Label(leg, text="5.0 = Failed",
                 bg=COLORS["surface"], fg=COLORS["fail_color"],
                 font=FONTS["small"]).pack(anchor="w")

    def _stat_row(self, parent, label: str, value: str, value_color=None) -> tk.Label:
        """Helper: create one label : value row inside the stats panel."""
        frame = tk.Frame(parent, bg=COLORS["surface"])
        frame.pack(fill="x", pady=3)
        tk.Label(
            frame, text=label + ":",
            bg=COLORS["surface"], fg=COLORS["text_dim"],
            font=FONTS["small"], anchor="w"
        ).pack(side="left")
        lbl = tk.Label(
            frame, text=value,
            bg=COLORS["surface"],
            fg=value_color if value_color else COLORS["text"],
            font=FONTS["small"], anchor="e"
        )
        lbl.pack(side="right")
        return lbl

    def _make_btn(self, parent, text: str, command, color: str) -> tk.Button:
        """Helper: create a styled flat button."""
        return tk.Button(
            parent, text=text, command=command,
            bg=color, fg="#ffffff",
            activebackground=COLORS["bg"],
            activeforeground=color,
            relief="flat", font=FONTS["btn"],
            padx=12, pady=5, cursor="hand2",
            highlightthickness=0
        )

    # ── Subject Management ────────────────────────────────────────────────────

    def _add_subject(self, name="", units="", grade=""):
        """Add a new subject row, optionally pre-filled with data."""
        idx = len(self.subject_rows)
        row = SubjectRow(
            parent_frame       = self.scrollable_frame,
            index              = idx,
            on_change_callback = self._on_data_change,
            on_remove_callback = lambda r=idx: self._remove_subject(r)
        )
        row._uid = idx   # unique id for reliable removal lookup
        if name or units or grade:
            row.set_data(name, units, grade)
        self.subject_rows.append(row)
        self._on_data_change()

    def _remove_subject(self, uid: int):
        """Find the row by uid and remove it from the list and UI."""
        target = next((r for r in self.subject_rows if r._uid == uid), None)
        if target is None:
            return
        if len(self.subject_rows) <= 1:
            messagebox.showwarning("Cannot Remove",
                                   "You must keep at least one subject row.")
            return
        target.destroy()
        self.subject_rows.remove(target)
        # Re-number remaining rows
        for i, row in enumerate(self.subject_rows):
            row.set_index(i)
        self._on_data_change()

    def _clear_all(self):
        """Remove all rows and reset to 3 empty ones."""
        if not messagebox.askyesno("Clear All",
                                   "Remove all subjects and start fresh?"):
            return
        for row in self.subject_rows:
            row.destroy()
        self.subject_rows.clear()
        self._add_subject()
        self._add_subject()
        self._add_subject()

    # ── GWA Computation & UI Update ───────────────────────────────────────────

    def _on_data_change(self):
        """Called whenever any entry changes. Recomputes GWA and refreshes the panel."""
        subjects_data = []

        for row in self.subject_rows:
            row.update_status()
            data = row.get_data()
            if data["valid_units"] and data["valid_grade"]:
                subjects_data.append({
                    "name":  data["name"],
                    "units": data["units"],
                    "grade": data["grade"],
                })

        # Nothing valid yet — reset the panel
        if not subjects_data:
            self.gwa_label.config(text="—", fg=COLORS["accent"])
            self.remark_label.config(text="Enter grades to\ncompute",
                                     fg=COLORS["text_dim"])
            self.total_units_label.config(text="—")
            self.total_subj_label.config(text="—")
            self.passed_label.config(text="—")
            self.failed_label.config(text="—")
            self.highest_label.config(text="—")
            self.lowest_label.config(text="—")
            return

        gwa       = compute_gwa(subjects_data)
        passing   = gwa <= PASSING_GRADE
        gwa_color = COLORS["pass_color"] if passing else COLORS["fail_color"]

        self.gwa_label.config(text=f"{gwa:.4f}", fg=gwa_color)
        self.remark_label.config(text=gwa_remark(gwa), fg=gwa_color)

        total_units = sum(float(s["units"]) for s in subjects_data)
        passed      = sum(1 for s in subjects_data if is_passing(float(s["grade"])))
        failed      = len(subjects_data) - passed
        grades      = [float(s["grade"]) for s in subjects_data]

        self.total_units_label.config(text=f"{total_units:.1f}")
        self.total_subj_label.config(text=str(len(subjects_data)))
        self.passed_label.config(text=str(passed))
        self.failed_label.config(text=str(failed))
        # In PH system: lower number = better grade
        self.highest_label.config(text=f"{min(grades):.2f}")
        self.lowest_label.config(text=f"{max(grades):.2f}")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()

    # Apply dark theme to the ttk scrollbar
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Vertical.TScrollbar",
        background  = COLORS["surface2"],
        troughcolor = COLORS["bg"],
        arrowcolor  = COLORS["accent"],
        bordercolor = COLORS["border"]
    )

    app = GWACalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
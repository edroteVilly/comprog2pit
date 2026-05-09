from tkinter import *
from tkinter import messagebox

# ---------------- WINDOW ----------------
root = Tk()
root.title("GWA Calculator System")
root.geometry("500x500")
root.config(bg="#f0f4f7")

# ---------------- VARIABLES ----------------
subjects = []

# ---------------- FUNCTIONS ----------------
def add_subject():
    try:
        subject = subject_entry.get()
        grade = float(grade_entry.get())
        units = float(units_entry.get())

        if subject == "":
            messagebox.showerror("Error", "Please enter subject name")
            return

        # Save subject data
        subjects.append((subject, grade, units))

        # Display in listbox
        subject_listbox.insert(
            END,
            f"{subject} | Grade: {grade} | Units: {units}"
        )

        # Clear entries
        subject_entry.delete(0, END)
        grade_entry.delete(0, END)
        units_entry.delete(0, END)

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Grade and Units must be numbers"
        )

def compute_gwa():
    if len(subjects) == 0:
        messagebox.showwarning(
            "No Data",
            "Please add subjects first"
        )
        return

    total_weighted = 0
    total_units = 0

    for subject, grade, units in subjects:
        total_weighted += grade * units
        total_units += units

    gwa = total_weighted / total_units

    # Remarks
    if gwa <= 1.75:
        remarks = "Excellent"
    elif gwa <= 2.50:
        remarks = "Good"
    elif gwa <= 3.00:
        remarks = "Passed"
    else:
        remarks = "Failed"

    result_label.config(
        text=f"GWA: {gwa:.2f}  |  Remarks: {remarks}"
    )

def clear_all():
    subjects.clear()
    subject_listbox.delete(0, END)
    result_label.config(text="GWA: ")
    
    subject_entry.delete(0, END)
    grade_entry.delete(0, END)
    units_entry.delete(0, END)

# ---------------- TITLE ----------------
title_label = Label(
    root,
    text="GWA Calculator System",
    font=("Arial", 18, "bold"),
    bg="#f0f4f7",
    fg="#333"
)
title_label.pack(pady=10)

# ---------------- INPUT FRAME ----------------
input_frame = Frame(root, bg="#f0f4f7")
input_frame.pack(pady=10)

# Subject
Label(
    input_frame,
    text="Subject:",
    font=("Arial", 11),
    bg="#f0f4f7"
).grid(row=0, column=0, padx=5, pady=5)

subject_entry = Entry(input_frame, width=20)
subject_entry.grid(row=0, column=1)

# Grade
Label(
    input_frame,
    text="Grade:",
    font=("Arial", 11),
    bg="#f0f4f7"
).grid(row=1, column=0, padx=5, pady=5)

grade_entry = Entry(input_frame, width=20)
grade_entry.grid(row=1, column=1)

# Units
Label(
    input_frame,
    text="Units:",
    font=("Arial", 11),
    bg="#f0f4f7"
).grid(row=2, column=0, padx=5, pady=5)

units_entry = Entry(input_frame, width=20)
units_entry.grid(row=2, column=1)

# ---------------- BUTTONS ----------------
button_frame = Frame(root, bg="#f0f4f7")
button_frame.pack(pady=10)

add_button = Button(
    button_frame,
    text="Add Subject",
    width=15,
    bg="#4CAF50",
    fg="white",
    command=add_subject
)
add_button.grid(row=0, column=0, padx=10)

compute_button = Button(
    button_frame,
    text="Compute GWA",
    width=15,
    bg="#2196F3",
    fg="white",
    command=compute_gwa
)
compute_button.grid(row=0, column=1, padx=10)

clear_button = Button(
    button_frame,
    text="Clear",
    width=15,
    bg="#f44336",
    fg="white",
    command=clear_all
)
clear_button.grid(row=0, column=2, padx=10)

# ---------------- LISTBOX ----------------
subject_listbox = Listbox(
    root,
    width=60,
    height=10,
    font=("Arial", 10)
)
subject_listbox.pack(pady=10)

# ---------------- RESULT LABEL ----------------
result_label = Label(
    root,
    text="GWA:",
    font=("Arial", 14, "bold"),
    bg="#f0f4f7",
    fg="#222"
)
result_label.pack(pady=15)

# ---------------- RUN ----------------
root.mainloop()
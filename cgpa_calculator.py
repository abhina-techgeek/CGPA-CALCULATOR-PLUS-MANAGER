"""
CGPA TRACKER (pre final file)
================================
A multi-user CGPA calculator .
IT Supports adding, viewing, editing, deleting,
searching, and exporting semester records, plus basic statistics.

Author :: abhinav kumar ('.;.')
"""

import json
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# FIXED
# ---------------------------------------------------------------------------

DATA_FILE = "cgpa_records.json"
EXPORT_FOLDER = "transcripts"

GRADE_POINTS = {
    "A+": 10, "A": 9, "B+": 8, "B": 7,
    "C+": 6, "C": 5, "D": 4, "F": 0
}

# Course type codes:
#   LTP -> Learning, Theory, Practical (has a lab/practical component)
#   LT  -> Learning, Theory only
#   PJ  -> Project
COURSE_TYPES = ["LTP", "LT", "PJ"]

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


# ---------------------------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------------------------

def colored_grade(grade):
    """Return the grade string wrapped in an  color code."""
    if grade in ("A+", "A"):
        return f"{GREEN}{grade}{RESET}"
    elif grade in ("B+", "B"):
        return f"{CYAN}{grade}{RESET}"
    elif grade == "F":
        return f"{RED}{grade}{RESET}"
    return f"{YELLOW}{grade}{RESET}"


def print_header(title, width=44):
    """Print a boxed header for section titles."""
    print(f"\n+{'-' * width}+")
    print(f"| {title:<{width - 1}}|")
    print(f"+{'-' * width}+")


def pause():
    """Simple pause so the user can read output before the menu reprints."""
    input("\nPress Enter to continue...")


# ---------------------------------------------------------------------------
# GRADE LOGIC
# ---------------------------------------------------------------------------

def point_to_grade(point):
    """Convert a numeric GPA/CGPA value into a letter grade."""
    if point >= 9:
        return "A+"
    elif point >= 8:
        return "A"
    elif point >= 7:
        return "B+"
    elif point >= 6:
        return "B"
    elif point >= 5:
        return "C+"
    elif point >= 4:
        return "C"
    elif point >= 3.5:
        return "D"
    else:
        return "F"


def calculate_gpa(subjects):
    """Calculate GPA for a single semester's subject list."""
    total_credits = sum(s["credit"] for s in subjects)
    total_points = sum(s["credit"] * s["point"] for s in subjects)
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


def calculate_cgpa(records):
    """Calculate cumulative GPA across a list of semester records."""
    total_credits = 0
    total_points = 0
    for record in records:
        for s in record["subjects"]:
            total_credits += s["credit"]
            total_points += s["credit"] * s["point"]
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)


# ---------------------------------------------------------------------------
# VALIDATED INPUT HELPERS
# ---------------------------------------------------------------------------

def get_positive_float(prompt):
    """Keep asking until the user enters a positive number."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value <= 0:
                print("Please enter a number greater than 0.")
                continue
            return value
        except ValueError:
            print("That's not a valid number. Try again.")


def get_valid_grade(prompt):
    """Keep asking until the user enters a recognized grade."""
    while True:
        grade = input(prompt).strip().upper()
        if grade in GRADE_POINTS:
            return grade
        print("Invalid grade. Choose from:", ", ".join(GRADE_POINTS.keys()))


def get_valid_course_type(prompt):
    """Keep asking until the user enters a recognized course type (LTP/LT/PJ)."""
    while True:
        ctype = input(prompt).strip().upper()
        if ctype in COURSE_TYPES:
            return ctype
        print("Invalid course type. Choose from:", ", ".join(COURSE_TYPES))


def get_non_empty_string(prompt):
    """Keep asking until the user enters non-blank text."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("This field can't be empty.")


def get_menu_choice(prompt, valid_choices):
    """Keep asking until the user picks one of the valid menu options."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"Invalid choice. Options are: {', '.join(valid_choices)}")


# ---------------------------------------------------------------------------
# FILE STORAGE (JSON — no database used)
# ---------------------------------------------------------------------------

def load_data():
    """Load all student records from the JSON file. Returns {} if missing/corrupt."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: data file was corrupted. Starting fresh.")
                return {}
    return {}


def save_data(data):
    """Write the full data dictionary back to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def ensure_export_folder():
    """Create the transcripts folder if it doesn't exist yet."""
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)


# ---------------------------------------------------------------------------
# SUBJECT / SEMESTER INPUT
# ---------------------------------------------------------------------------

def input_subjects():
    """Prompt the user for a full semester's worth of subjects."""
    subjects = []
    while True:
        raw_n = input("How many subjects this semester? ").strip()
        if raw_n.isdigit() and int(raw_n) > 0:
            n = int(raw_n)
            break
        print("Please enter a whole number greater than 0.")

    print(f"\nValid grades: {', '.join(GRADE_POINTS.keys())}")
    print(f"Valid course types: {', '.join(COURSE_TYPES)} "
          f"(LTP=Learning/Theory/Practical, LT=Learning/Theory, PJ=Project)\n")

    for i in range(1, n + 1):
        print(f"-- Subject {i} of {n} --")
        code = get_non_empty_string("  Course code: ").upper()
        name = get_non_empty_string("  Name: ")
        credit = get_positive_float("  Credit hours: ")
        ctype = get_valid_course_type("  Course type (LTP/LT/PJ): ")
        grade = get_valid_grade("  Grade: ")
        subjects.append({
            "code": code,
            "name": name,
            "credit": credit,
            "type": ctype,
            "grade": grade,
            "point": GRADE_POINTS[grade]
        })
    return subjects


def build_record(subjects):
    """Wrap a subject list into a full semester record with date and GPA."""
    gpa = calculate_gpa(subjects)
    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "subjects": subjects,
        "gpa": gpa
    }


# ---------------------------------------------------------------------------
# DISPLAY FUNCTIONS
# ---------------------------------------------------------------------------

def display_record(record, index, width=74):
    """Print one semester's subjects and GPA as a bordered table."""
    print(f"\n+{'-' * width}+")
    print(f"| Semester {index:<3} {record['date']:>{width - 14}} |")
    print(f"+{'-' * width}+")
    print(f"| {'Code':<8}{'Subject':<15}{'Credit':<8}{'Type':<6}{'Grade':<15}{'Point':<6}{' ' * (width - 58)}|")
    print(f"+{'-' * width}+")
    for s in record["subjects"]:
        grade_display = colored_grade(s["grade"])
        code = s.get("code", "-")
        ctype = s.get("type", "-")
        print(f"| {code:<8}{s['name']:<15}{s['credit']:<8}{ctype:<6}{grade_display:<15}{s['point']:<6}"
              f"{' ' * (width - 58)}|")
    print(f"+{'-' * width}+")
    print(f"| GPA: {record['gpa']:<{width - 6}}|")
    print(f"+{'-' * width}+")


def view_all_records(data, student_id):
    """Show every saved semester for one student."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records found for {student_id}.")
        return
    print_header(f"Records for: {student_id}")
    for i, record in enumerate(records, start=1):
        display_record(record, i)


def show_cgpa(data, student_id):
    """Print the overall CGPA and letter grade for one student."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records found for {student_id}.")
        return
    cgpa = calculate_cgpa(records)
    grade = point_to_grade(cgpa)
    print(f"\n{student_id}'s Overall CGPA: {cgpa}  (Grade: {colored_grade(grade)})")


def list_all_students(data):
    """Print a roster table of every student stored in the file."""
    if not data:
        print("\nNo students stored yet.")
        return
    print_header("Student Roster")
    print(f"{'Name':<20}{'Semesters':<12}{'CGPA':<8}")
    print("-" * 40)
    for name, records in data.items():
        cgpa = calculate_cgpa(records) if records else 0.0
        print(f"{name:<20}{len(records):<12}{cgpa:<8}")


# ---------------------------------------------------------------------------
# EDIT / DELETE
# ---------------------------------------------------------------------------

def edit_semester(data, student_id):
    """Let the user overwrite an existing semester's subjects."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records to edit for {student_id}.")
        return

    view_all_records(data, student_id)
    raw = input("\nWhich semester number do you want to edit? ").strip()
    if not raw.isdigit() or not (1 <= int(raw) <= len(records)):
        print("Invalid semester number.")
        return

    idx = int(raw) - 1
    print("\nRe-entering subjects for this semester:")
    new_subjects = input_subjects()
    records[idx]["subjects"] = new_subjects
    records[idx]["gpa"] = calculate_gpa(new_subjects)
    records[idx]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M") + " (edited)"

    save_data(data)
    print("Semester updated successfully.")


def delete_semester(data, student_id):
    """Let the user remove a semester record entirely."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records to delete for {student_id}.")
        return

    view_all_records(data, student_id)
    raw = input("\nWhich semester number do you want to delete? ").strip()
    if not raw.isdigit() or not (1 <= int(raw) <= len(records)):
        print("Invalid semester number.")
        return

    idx = int(raw) - 1
    confirm = input(f"Delete semester {idx + 1}? This can't be undone (y/n): ").strip().lower()
    if confirm == "y":
        records.pop(idx)
        save_data(data)
        print("Semester deleted.")
    else:
        print("Cancelled.")


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------

def search_subject(data, student_id):
    """Search a student's history for a subject by (partial) name or course code."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records found for {student_id}.")
        return

    query = get_non_empty_string("Enter subject name or course code (or part of it) to search: ").lower()
    found = False

    print_header(f"Search results for '{query}'")
    for i, record in enumerate(records, start=1):
        for s in record["subjects"]:
            code = s.get("code", "")
            ctype = s.get("type", "-")
            if query in s["name"].lower() or query in code.lower():
                found = True
                print(f"Semester {i} ({record['date']}): "
                      f"[{code}] {s['name']} ({ctype}) — {colored_grade(s['grade'])} "
                      f"({s['credit']} credits, {s['point']} points)")

    if not found:
        print("No matching subjects found.")


# ---------------------------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------------------------

def show_statistics(data, student_id):
    """Display best/worst semester GPA and overall trend."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records found for {student_id}.")
        return

    gpas = [r["gpa"] for r in records]
    best = max(records, key=lambda r: r["gpa"])
    worst = min(records, key=lambda r: r["gpa"])
    average = round(sum(gpas) / len(gpas), 2)

    print_header(f"Statistics for {student_id}")
    print(f"Semesters recorded : {len(records)}")
    print(f"Average semester GPA: {average}")
    print(f"Best semester       : {best['date']}  (GPA {best['gpa']})")
    print(f"Weakest semester    : {worst['date']}  (GPA {worst['gpa']})")
    print(f"Current CGPA        : {calculate_cgpa(records)}")


# ---------------------------------------------------------------------------
# EXPORT
# ---------------------------------------------------------------------------

def export_transcript(data, student_id):
    """Write a plain-text transcript file for one student."""
    records = data.get(student_id, [])
    if not records:
        print(f"\nNo records found for {student_id}.")
        return

    ensure_export_folder()
    safe_name = student_id.replace(" ", "_")
    filepath = os.path.join(EXPORT_FOLDER, f"{safe_name}_transcript.txt")

    with open(filepath, "w") as f:
        f.write(f"TRANSCRIPT FOR: {student_id}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 60 + "\n")

        for i, record in enumerate(records, start=1):
            f.write(f"\nSemester {i} ({record['date']})\n")
            f.write(f"{'Code':<8}{'Subject':<20}{'Credit':<8}{'Type':<6}{'Grade':<6}{'Point':<6}\n")
            f.write("-" * 54 + "\n")
            for s in record["subjects"]:
                code = s.get("code", "-")
                ctype = s.get("type", "-")
                f.write(f"{code:<8}{s['name']:<20}{s['credit']:<8}{ctype:<6}{s['grade']:<6}{s['point']:<6}\n")
            f.write(f"Semester GPA: {record['gpa']}\n")

        cgpa = calculate_cgpa(records)
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"OVERALL CGPA: {cgpa}  (Grade: {point_to_grade(cgpa)})\n")

    print(f"\nTranscript exported to: {filepath}")


# ---------------------------------------------------------------------------
# HELP / ABOUT
# ---------------------------------------------------------------------------

def show_help():
    """Print a short explanation of how the grading scale works."""
    print_header("Help / Grading Scale")
    print("This tool uses a 10-point grading scale:\n")
    for grade, point in GRADE_POINTS.items():
        print(f"  {grade:<4} = {point} points")
    print("\nCourse types:")
    print("  LTP = Learning, Theory & Practical (has a lab/practical component)")
    print("  LT  = Learning & Theory only")
    print("  PJ  = Project")
    print("\nGPA (one semester)  = sum(credit x point) / sum(credit)")
    print("CGPA (all semesters) = same formula across every saved semester")
    print("\nAll data is stored locally in 'cgpa_records.json'.")
    print("No internet connection or database server is required.")


# ---------------------------------------------------------------------------
# MENUS
# ---------------------------------------------------------------------------

def show_menu(student_id):
    """Print the main per-student menu."""
    print_header(f"CGPA TRACKER — {student_id}")
    print("1. Add new semester result")
    print("2. View my records")
    print("3. Show my overall CGPA")
    print("4. Edit a semester")
    print("5. Delete a semester")
    print("6. Search for a subject")
    print("7. Show statistics")
    print("8. Export transcript (.txt)")
    print("9. View all students (roster)")
    print("10. Help")
    print("11. Switch student / Exit")


def student_session(data, student_id):
    """Run the menu loop for one logged-in student until they exit."""
    valid = [str(n) for n in range(1, 12)]

    while True:
        show_menu(student_id)
        choice = get_menu_choice("Choose an option (1-11): ", valid)

        if choice == "1":
            subjects = input_subjects()
            record = build_record(subjects)
            data.setdefault(student_id, []).append(record)
            save_data(data)
            print(f"\nSemester GPA: {record['gpa']}  "
                  f"(Grade: {colored_grade(point_to_grade(record['gpa']))})")
            print("Record saved successfully.")
            pause()

        elif choice == "2":
            view_all_records(data, student_id)
            pause()

        elif choice == "3":
            show_cgpa(data, student_id)
            pause()

        elif choice == "4":
            edit_semester(data, student_id)
            pause()

        elif choice == "5":
            delete_semester(data, student_id)
            pause()

        elif choice == "6":
            search_subject(data, student_id)
            pause()

        elif choice == "7":
            show_statistics(data, student_id)
            pause()

        elif choice == "8":
            export_transcript(data, student_id)
            pause()

        elif choice == "9":
            list_all_students(data)
            pause()

        elif choice == "10":
            show_help()
            pause()

        elif choice == "11":
            print(f"\nSee you, {student_id}!")
            break


# ---------------------------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------------------------

def main():
    """Entry point: load data, log in a student, run their session, repeat."""
    data = load_data()

    print_header("Welcome to the CGPA Tracker")
    print("Track semester GPA, cumulative CGPA, and full transcripts")
    print("for multiple students — all stored locally, no database.")

    while True:
        student_id = get_non_empty_string("\nEnter your name or student ID: ")
        if student_id not in data:
            data[student_id] = []
            print(f"New student profile created for {student_id}.")

        student_session(data, student_id)

        again = input("\nLog in as another student? (y/n): ").strip().lower()
        if again != "y":
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
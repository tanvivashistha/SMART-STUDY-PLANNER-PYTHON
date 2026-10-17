"""
data_manager.py
Smart Study Planner and Exam Readiness Analyzer
Module: Data Manager and Input Validation

Functions in this module:
    get_int()    - safely read a whole number inside a range
    get_date()   - safely read a date typed as DD-MM-YYYY
    get_text()   - safely read non-empty text (helper for add_topic)
    load_data()  - read topics.csv and exams.csv into Python data structures
    save_data()  - write the data structures back to the CSV files
    add_topic()  - ask the user for a new topic, validate it, store and save it

Data structures shared with the other modules:
    topics : list of dictionaries, one per topic
             {"subject": str, "topic": str, "difficulty": int (1-5),
              "confidence": int (1-5), "hours_needed": int}
    exams  : dictionary  {subject (str): exam date (datetime.date)}
"""

import csv
from datetime import date, datetime

TOPICS_FILE = "topics.csv"
EXAMS_FILE = "exams.csv"

TOPIC_FIELDS = ["subject", "topic", "difficulty", "confidence", "hours_needed"]
DATE_FORMAT = "%d-%m-%Y"          # what the user types, e.g. 25-11-2026
FILE_DATE_FORMAT = "%Y-%m-%d"     # how dates are stored in the CSV file


# ---------------------------------------------------------------------------
# INPUT VALIDATION
# ---------------------------------------------------------------------------
def get_int(prompt, min_value, max_value):
    """Keep asking until the user types a whole number between min and max."""
    while True:
        text = input(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            print(f"  Invalid input. Please enter a whole number "
                  f"({min_value} to {max_value}).")
            continue
        if number < min_value or number > max_value:
            print(f"  Out of range. Please enter a number from "
                  f"{min_value} to {max_value}.")
            continue
        return number


def get_date(prompt, allow_past=False):
    """Keep asking until the user types a real date as DD-MM-YYYY.
    Past dates are rejected unless allow_past is True."""
    while True:
        text = input(prompt).strip()
        try:
            chosen = datetime.strptime(text, DATE_FORMAT).date()
        except ValueError:
            print("  Invalid date. Use DD-MM-YYYY with a real date "
                  "(example: 25-11-2026).")
            continue
        if chosen < date.today() and not allow_past:
            print("  That date has already passed. Enter today or a future date.")
            continue
        return chosen


def get_text(prompt):
    """Keep asking until the user types something that is not empty."""
    while True:
        text = input(prompt).strip()
        if text == "":
            print("  This cannot be empty.")
            continue
        return text


# ---------------------------------------------------------------------------
# FILE HANDLING
# ---------------------------------------------------------------------------
def load_data(topics_file=TOPICS_FILE, exams_file=EXAMS_FILE):
    """Read both CSV files. Returns (topics, exams).
    If a file does not exist yet, that part starts empty."""
    topics = []
    exams = {}

    try:
        with open(topics_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    topics.append({
                        "subject": row["subject"],
                        "topic": row["topic"],
                        "difficulty": int(row["difficulty"]),
                        "confidence": int(row["confidence"]),
                        "hours_needed": int(row["hours_needed"]),
                    })
                except (ValueError, KeyError, TypeError):
                    print(f"  Skipped a damaged row in {topics_file}: {row}")
    except FileNotFoundError:
        pass    # first run: no file yet, start with an empty list

    try:
        with open(exams_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    exams[row["subject"]] = datetime.strptime(
                        row["exam_date"], FILE_DATE_FORMAT).date()
                except (ValueError, KeyError, TypeError):
                    print(f"  Skipped a damaged row in {exams_file}: {row}")
    except FileNotFoundError:
        pass    # first run: no file yet, start with an empty dictionary

    return topics, exams


def save_data(topics, exams, topics_file=TOPICS_FILE, exams_file=EXAMS_FILE):
    """Write the topics list and exams dictionary to their CSV files."""
    with open(topics_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TOPIC_FIELDS)
        writer.writeheader()
        writer.writerows(topics)

    with open(exams_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["subject", "exam_date"])
        for subject, exam_date in exams.items():
            writer.writerow([subject, exam_date.strftime(FILE_DATE_FORMAT)])


# ---------------------------------------------------------------------------
# ADDING A TOPIC
# ---------------------------------------------------------------------------
def add_topic(topics, exams, topics_file=TOPICS_FILE, exams_file=EXAMS_FILE):
    """Ask for a new topic, validate every answer, add it to the data and
    save to the CSV files. Returns the new topic dictionary, or None if the
    topic already exists."""
    print("\n--- Add a new topic ---")
    subject = get_text("Subject name: ").title()
    topic = get_text("Topic name: ")

    # Do not allow the same topic twice for the same subject
    for t in topics:
        if t["subject"] == subject and t["topic"].lower() == topic.lower():
            print(f"  '{topic}' already exists under {subject}. Nothing added.")
            return None

    difficulty = get_int("Difficulty (1 = easy, 5 = very hard): ", 1, 5)
    confidence = get_int("Your confidence (1 = weak, 5 = strong): ", 1, 5)
    hours_needed = get_int("Hours needed to prepare this topic (1-50): ", 1, 50)

    # Each subject has one exam date. Ask only if this subject is new.
    if subject in exams:
        print(f"  Exam date for {subject} is already saved: "
              f"{exams[subject].strftime(DATE_FORMAT)}")
    else:
        exams[subject] = get_date(f"Exam date for {subject} (DD-MM-YYYY): ")

    new_topic = {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "confidence": confidence,
        "hours_needed": hours_needed,
    }
    topics.append(new_topic)
    save_data(topics, exams, topics_file, exams_file)
    print(f"  Saved: {subject} - {topic}")
    return new_topic


# ---------------------------------------------------------------------------
# Small menu so this module can be run and tested on its own
# ---------------------------------------------------------------------------
def show_topics(topics, exams):
    """Print all stored topics (used only for testing this module)."""
    if not topics:
        print("\nNo topics stored yet.")
        return
    print(f"\n{'Subject':<12}{'Topic':<18}{'Diff':<6}{'Conf':<6}{'Hours':<7}Exam date")
    for t in topics:
        exam = exams[t["subject"]].strftime(DATE_FORMAT)
        print(f"{t['subject']:<12}{t['topic']:<18}{t['difficulty']:<6}"
              f"{t['confidence']:<6}{t['hours_needed']:<7}{exam}")


def main():
    topics, exams = load_data()
    print(f"Loaded {len(topics)} topic(s) and {len(exams)} exam date(s).")
    while True:
        print("\n1. Add topic\n2. Show topics\n3. Exit")
        choice = get_int("Choose an option (1-3): ", 1, 3)
        if choice == 1:
            add_topic(topics, exams)
        elif choice == 2:
            show_topics(topics, exams)
        else:
            save_data(topics, exams)
            print("Data saved. Goodbye!")
            break


if __name__ == "__main__":
    main()

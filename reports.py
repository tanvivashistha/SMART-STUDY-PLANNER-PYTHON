
"""
reports.py
Smart Study Planner and Exam Readiness Analyzer

Module: Report, Visualization and Main Menu

Functions:
    generate_report() - creates and saves readiness report
    plot_readiness()  - creates subject readiness bar graph
    main()            - connects all project modules
"""

# Import functions from other team members' modules
from data_manager import load_data, save_data, add_topic, get_int
from priority_engine import rank_topics, print_ranking
from schedule_and_conflict_detector import (
    build_schedule,
    detect_conflicts
)


# -------------------------------------------------
# TASK 1: GENERATE READINESS REPORT
# -------------------------------------------------

def generate_report(topics, output_file="report.txt"):

    print("\n========== EXAM READINESS REPORT ==========")

    if not topics:
        print("No topics available. Add topics first.")
        return {}

    subject_data = {}

    # Calculate average confidence for each subject
    for t in topics:

        subject = t["subject"]
        confidence = t["confidence"]

        if subject not in subject_data:
            subject_data[subject] = []

        subject_data[subject].append(confidence)

    readiness = {}

    for subject, scores in subject_data.items():

        average = sum(scores) / len(scores)

        # Convert confidence out of 5 into percentage
        percentage = (average / 5) * 100

        readiness[subject] = round(percentage, 2)

    # Find weakest and strongest subjects
    weakest = min(readiness, key=readiness.get)
    strongest = max(readiness, key=readiness.get)

    # Display report
    print("\nSubject-wise Readiness:\n")

    for subject, score in readiness.items():
        print(f"{subject:<15} {score:.2f}%")

    print("\nWeakest Subject :", weakest)
    print("Strongest Subject:", strongest)

    # Save report in a text file
    with open(output_file, "w", encoding="utf-8") as f:

        f.write("SMART STUDY PLANNER\n")
        f.write("EXAM READINESS REPORT\n")
        f.write("=" * 35 + "\n\n")

        for subject, score in readiness.items():
            f.write(f"{subject}: {score:.2f}%\n")

        f.write("\nWeakest Subject: " + weakest)
        f.write("\nStrongest Subject: " + strongest)

    print(f"\nReport successfully saved to {output_file}")

    return readiness


# -------------------------------------------------
# TASK 2: PLOT READINESS GRAPH
# -------------------------------------------------

def plot_readiness(readiness):

    if not readiness:
        print("No readiness data available.")
        return

    try:
        import matplotlib.pyplot as plt

    except ImportError:
        print("Matplotlib is not installed.")
        print("Install it using: pip install matplotlib")
        return

    subjects = list(readiness.keys())
    scores = list(readiness.values())

    plt.figure(figsize=(8, 5))

    plt.bar(subjects, scores)

    plt.title("Exam Readiness by Subject")
    plt.xlabel("Subjects")
    plt.ylabel("Readiness (%)")

    plt.ylim(0, 100)

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()


# -------------------------------------------------
# TASK 3: MAIN MENU
# -------------------------------------------------

def main():

    topics, exams = load_data()

    print("\n===================================")
    print("       SMART STUDY PLANNER")
    print("===================================")

    while True:

        print("\n1. Add a topic")
        print("2. Rank topics")
        print("3. Generate study schedule")
        print("4. Detect conflicts")
        print("5. Generate readiness report")
        print("6. Plot readiness graph")
        print("7. Exit")

        choice = get_int("\nEnter your choice (1-7): ", 1, 7)

        # Option 1: Add topic
        if choice == 1:

            add_topic(topics, exams)

        # Option 2: Rank topics
        elif choice == 2:

            ranked = rank_topics(topics, exams)
            print_ranking(ranked)

        # Option 3: Generate schedule
        elif choice == 3:

            ranked = rank_topics(topics, exams)

            schedule = build_schedule(ranked, exams)

            if not schedule:
                print("No schedule available.")

            else:
                print("\n========== STUDY SCHEDULE ==========")

                for day, subject, topic, hours in schedule:

                    print(
                        f"{day.strftime('%d-%m-%Y')} | "
                        f"{subject} | {topic} | {hours} hour(s)"
                    )

        # Option 4: Detect conflicts
        elif choice == 4:

            warnings = detect_conflicts(topics, exams)

            print("\n========== CONFLICT REPORT ==========")

            if warnings:
                for warning in warnings:
                    print("-", warning)
            else:
                print("No conflicts detected!")

        # Option 5: Generate report
        elif choice == 5:

            generate_report(topics)

        # Option 6: Plot graph
        elif choice == 6:

            readiness = generate_report(topics)
            plot_readiness(readiness)

        # Option 7: Exit
        elif choice == 7:

            save_data(topics, exams)

            print("\nData saved successfully.")
            print("Thank you for using Smart Study Planner!")

            break


# -------------------------------------------------
# RUN THE PROGRAM
# -------------------------------------------------

if __name__ == "__main__":
    main()

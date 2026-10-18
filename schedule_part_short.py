from datetime import date, timedelta

DAILY_HOURS = 6        # study hours per day
BLOCK_SIZE = 2         # longest single study block (hours)
LOW_CONFIDENCE = 2     # average confidence below this = weak subject
URGENT_DAYS = 7        # fewer days left than this = urgent


def build_schedule(ranked_topics, exam_dates, daily_hours=DAILY_HOURS):
    # ranked_topics: list of dictionaries, highest priority first
    # exam_dates: dictionary {subject: date}
    # returns a list of tuples (date, subject, topic, hours)
    schedule = []
    if not ranked_topics or not exam_dates:
        return schedule

    # hours each topic still needs
    remaining = {}
    for t in ranked_topics:
        remaining[(t["subject"], t["topic"])] = t["hours_needed"]

    day = date.today()
    last_exam = max(exam_dates.values())

    while day <= last_exam:
        hours_left = daily_hours
        while hours_left > 0:
            gave_hours = False
            # go through topics from highest priority to lowest
            for t in ranked_topics:
                key = (t["subject"], t["topic"])
                if hours_left == 0:
                    break
                # skip if finished, no exam date, or exam already over
                if remaining[key] <= 0 or t["subject"] not in exam_dates:
                    continue
                if exam_dates[t["subject"]] < day:
                    continue
                block = min(BLOCK_SIZE, remaining[key], hours_left)
                schedule.append((day, t["subject"], t["topic"], block))
                remaining[key] -= block
                hours_left -= block
                gave_hours = True
            if not gave_hours:      # nothing left to study today
                break
        day = day + timedelta(days=1)

    return schedule


def detect_conflicts(topics, exam_dates, daily_hours=DAILY_HOURS):
    # returns a list of warning messages
    warnings = []
    today = date.today()

    # Rule 1: two exams on the same date
    seen = {}
    for subject in exam_dates:
        exam_day = exam_dates[subject]
        if exam_day in seen:
            warnings.append("CLASH: " + seen[exam_day] + " and " + subject + " exams are on the same day")
        else:
            seen[exam_day] = subject

    for subject in exam_dates:
        days_left = (exam_dates[subject] - today).days
        if days_left < 0:           # exam already over
            continue

        # total hours needed and average confidence of this subject
        total_hours = 0
        total_conf = 0
        count = 0
        for t in topics:
            if t["subject"] == subject:
                total_hours += t["hours_needed"]
                total_conf += t["confidence"]
                count += 1
        if count == 0:
            continue

        # Rule 2: more hours needed than available (today counts as a day)
        available = (days_left + 1) * daily_hours
        if total_hours > available:
            warnings.append("OVERLOAD: " + subject + " needs " + str(total_hours) +
                            " hours but only " + str(available) + " are available")

        # Rule 3: weak subject and little time left
        average = total_conf / count
        if average < LOW_CONFIDENCE and days_left < URGENT_DAYS:
            warnings.append("WEAK SUBJECT: " + subject + " (average confidence " +
                            str(round(average, 1)) + ", " + str(days_left) + " days left)")

    return warnings


# ---- quick test ----
'''
if __name__ == "__main__":
    topics = [
        {"subject": "Physics", "topic": "Electrostatics", "difficulty": 5, "confidence": 1, "hours_needed": 6},
        {"subject": "Maths", "topic": "Matrices", "difficulty": 3, "confidence": 4, "hours_needed": 4},
    ]
    exam_dates = {"Physics": date.today() + timedelta(days=3),
                  "Maths": date.today() + timedelta(days=3)}

    for row in build_schedule(topics, exam_dates):
        print(row)
    for w in detect_conflicts(topics, exam_dates):
        print(w)
'''

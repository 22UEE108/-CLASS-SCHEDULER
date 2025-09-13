# demo.py
from datetime import datetime, date, time, timedelta
from db import SessionLocal, init_db, Student, ClassTemplate, ScheduledClass
from scheduler import Scheduler
from notifier import Notifier
from gmail_handler import GmailHandler, EmailEvent

def seed_example_data(session):
    # create student
    student = Student(name="Raman", email="raman@mail.com")
    session.add(student)
    session.commit()

    # Weekly templates (Mon-Fri) + a weekend slot
    session.add_all([
        ClassTemplate(student_id=student.id, subject="Digital Electronics", weekday=0, start_time=time(10,0), end_time=time(11,0)),
        ClassTemplate(student_id=student.id, subject="Signals & Systems", weekday=0, start_time=time(11,30), end_time=time(12,30)),
        ClassTemplate(student_id=student.id, subject="Maths", weekday=1, start_time=time(10,0), end_time=time(11,0)),
        ClassTemplate(student_id=student.id, subject="DSA", weekday=2, start_time=time(10,0), end_time=time(11,0)),
        # weekend slot (Saturday)
        ClassTemplate(student_id=student.id, subject="Weekend Slot", weekday=5, start_time=time(10,0), end_time=time(11,0)),
    ])
    session.commit()

    # Populate scheduled_classes for an example week (using the templates)
    week_monday = date(2025, 9, 8)
    templates = session.query(ClassTemplate).filter(ClassTemplate.student_id == student.id).all()
    for tmpl in templates:
        days_ahead = tmpl.weekday - week_monday.weekday()
        slot_date = week_monday + timedelta(days=days_ahead)
        start_dt = datetime.combine(slot_date, tmpl.start_time)
        end_dt = datetime.combine(slot_date, tmpl.end_time)
        sc = ScheduledClass(student_id=student.id, subject=tmpl.subject, start_dt=start_dt, end_dt=end_dt)
        session.add(sc)
    session.commit()
    return student, week_monday

def run_demo():
    print("Initializing DB (create tables if not exist)...")
    init_db()
    session = SessionLocal()
    student, week_monday = seed_example_data(session)
    scheduler = Scheduler(session)
    notifier = Notifier()
    gmail = GmailHandler(demo_mode=True)

    # Simulate incoming interview mail: overlaps Monday 10:30 (Digital Electronics)
    interview = EmailEvent(subject="Placement Interview - Google",
                           start_dt=datetime(2025, 9, 8, 10, 30),
                           end_dt=datetime(2025, 9, 8, 11, 30))

    print("Simulating incoming interview email -> running rescheduler...")
    actions = scheduler.reschedule_for_event(student, interview.start_dt, interview.end_dt, week_monday)
    for a in actions:
        print("ACTION:", a)

    # Daily notification (console)
    notifier.send_sms(student.email, f"Daily: actions:\n" + "\n".join(actions))

if __name__ == "__main__":
    run_demo()

# tests/test_scheduler.py
import pytest
from datetime import datetime, date, time, timedelta
from db import init_db, SessionLocal, Student, ClassTemplate, ScheduledClass
from scheduler import Scheduler

@pytest.fixture
def session():
    # Warning: tests as provided rely on DB in .env. For real unit tests,
    # adapt db.py to allow an in-memory SQLite DB for test isolation.
    init_db()
    s = SessionLocal()
    yield s
    s.close()

def test_reschedule_simple(session):
    # seed student + template + scheduled class (mon 10:00-11:00)
    student = Student(name="Test", email="test@mail.com")
    session.add(student); session.commit()
    tmpl = ClassTemplate(student_id=student.id, subject="Core", weekday=0, start_time=time(10,0), end_time=time(11,0))
    session.add(tmpl); session.commit()

    # scheduled class for Monday 2025-09-08 10:00 (conflicts with interview)
    sc = ScheduledClass(student_id=student.id, subject="Core", start_dt=datetime(2025,9,8,10,0), end_dt=datetime(2025,9,8,11,0))
    session.add(sc); session.commit()

    scheduler = Scheduler(session)
    actions = scheduler.reschedule_for_event(student, datetime(2025,9,8,10,30), datetime(2025,9,8,11,30), date(2025,9,8))
    assert any("Rescheduled" in a or "Marked pending" in a for a in actions)

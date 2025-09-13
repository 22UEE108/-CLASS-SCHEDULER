# scheduler.py
from datetime import datetime, timedelta, time
from typing import Optional
from sqlalchemy.orm import Session
from db import ScheduledClass, Attendance, Pending, ClassTemplate, Student
import calendar

WEEKDAY_RANGE = range(0, 5)  # Mon(0) .. Fri(4)
WEEKEND = [5, 6]             # Sat(5), Sun(6)

class Scheduler:
    """
    Scheduler handles:
    - detecting conflicts between incoming interview events and scheduled classes
    - rescheduling displaced classes to next free slot in the week, then weekend
    - marking attendance as Present (compensated) for classes displaced by interview/oa/prep
    - marking pending if no free slots remain
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def find_conflicting_classes(self, student: Student, event_start: datetime, event_end: datetime):
        """Return ScheduledClass objects that overlap event."""
        q = self.db.query(ScheduledClass).filter(
            ScheduledClass.student_id == student.id,
            ScheduledClass.is_interview == False,
            ScheduledClass.pending == False,
            ScheduledClass.start_dt < event_end,
            ScheduledClass.end_dt > event_start
        ).all()
        return q

    def _week_slots_datetimes(self, student: Student, week_monday_date: datetime.date):
        """
        Return allowed slot datetimes for the week based on class templates.
        Result: list of tuples (slot_start_dt, slot_end_dt, template_id)
        """
        slots = []
        for tmpl in student.templates:
            # calc the date for this tmpl.weekday in that week
            days_ahead = tmpl.weekday - week_monday_date.weekday()
            slot_date = week_monday_date + timedelta(days=days_ahead)
            start_dt = datetime.combine(slot_date, tmpl.start_time)
            end_dt = datetime.combine(slot_date, tmpl.end_time)
            slots.append((start_dt, end_dt, tmpl.id))
        # return sorted
        slots.sort(key=lambda x: (x[0], x[1]))
        return slots

    def _slot_is_free(self, student: Student, slot_start: datetime, slot_end: datetime):
        """Check if student has any scheduled class overlapping this slot."""
        q = self.db.query(ScheduledClass).filter(
            ScheduledClass.student_id == student.id,
            ScheduledClass.pending == False,
            ScheduledClass.start_dt < slot_end,
            ScheduledClass.end_dt > slot_start
        ).count()
        return q == 0

    def reschedule_for_event(self, student: Student, event_start: datetime, event_end: datetime, week_monday_date: datetime.date):
        """
        Main entry: when an interview/OA event arrives for a student,
        reschedule conflicting classes.
        Returns list of actions performed (for notification).
        """
        actions = []
        conflicts = self.find_conflicting_classes(student, event_start, event_end)
        for cls in conflicts:
            actions.append(f"Conflict found: {cls.subject} at {cls.start_dt}")
            # mark attendance for original date as Present (compensated)
            att = Attendance(
                student_id=student.id,
                scheduled_class_id=cls.id,
                date=cls.start_dt.date(),
                status='Present',
                reason='Interview'  # compensated
            )
            self.db.add(att)

            # find next free slot in same week (Mon..Fri)
            slots = self._week_slots_datetimes(student, week_monday_date)
            # sort slots chronologically and pick the first slot that is free and not the same slot
            candidate = None
            for start_dt, end_dt, tmpl_id in slots:
                if self._slot_is_free(student, start_dt, end_dt):
                    candidate = (start_dt, end_dt)
                    break

            # If no candidate in weekdays, try weekend slots (templates with weekday 5/6)
            if candidate is None:
                weekend_slots = [ (s,e,t) for s,e,t in slots if s.weekday() in WEEKEND ]
                for start_dt, end_dt, tmpl_id in weekend_slots:
                    if self._slot_is_free(student, start_dt, end_dt):
                        candidate = (start_dt, end_dt)
                        break

            if candidate is None:
                # No slot found -> mark pending (will be reported on weekend)
                cls.pending = True
                self.db.add(Pending(student_id=student.id, subject=cls.subject, original_start_dt=cls.start_dt))
                actions.append(f"Marked pending: {cls.subject} (no free slot)")
            else:
                new_start, new_end = candidate
                # update the scheduled class to the new slot and record rescheduled_from
                cls.rescheduled_from = cls.id
                cls.start_dt = new_start
                cls.end_dt = new_end
                self.db.add(cls)
                actions.append(f"Rescheduled {cls.subject} -> {new_start.strftime('%Y-%m-%d %H:%M')}")

        self.db.commit()
        return actions

    def student_block_for_prep(self, student: Student, scheduled_class: ScheduledClass):
        """
        Student voluntarily blocks a class for placement prep.
        Mark attendance for that class date as Present with reason 'Prep'.
        """
        att = Attendance(
            student_id=student.id,
            scheduled_class_id=scheduled_class.id,
            date=scheduled_class.start_dt.date(),
            status='Present',
            reason='Prep'
        )
        self.db.add(att)
        self.db.commit()
        return f"Class {scheduled_class.subject} on {scheduled_class.start_dt} marked Present for Prep."

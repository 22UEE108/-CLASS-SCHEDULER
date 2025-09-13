# gmail_handler.py
from typing import List
from datetime import datetime

class EmailEvent:
    def __init__(self, subject: str, start_dt: datetime, end_dt: datetime, is_interview=True):
        self.subject = subject
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.is_interview = is_interview

class GmailHandler:
    """
    Demo-friendly handler. In DEMO_MODE, we simulate incoming emails/events.
    To plug real Gmail:
      - Use google-api-python-client and gmail.users().messages().list()
      - Filter messages by subject keywords ("Placement Interview", "OA", "Online Assessment")
      - Parse message body for date/time (or use structured invites)
    """

    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode

    def fetch_events_for_student(self, student_email: str) -> List[EmailEvent]:
        if self.demo_mode:
            # Demo: return empty list by default; demo.py will provide simulated events
            return []
        # Real implementation: use Gmail API to fetch and parse messages into EmailEvent
        raise NotImplementedError("Plug Gmail API here (see README)")

    # helper: parse messages to produce EmailEvent objects (implementation left for actual integration)

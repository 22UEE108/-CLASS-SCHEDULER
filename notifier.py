# notifier.py
import os
from dotenv import load_dotenv

load_dotenv()
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

class Notifier:
    def __init__(self):
        self.client = None
        if not DEMO_MODE and TWILIO_SID and TWILIO_TOKEN:
            try:
                from twilio.rest import Client
                self.client = Client(TWILIO_SID, TWILIO_TOKEN)
            except Exception as e:
                print("Twilio not available:", e)
                self.client = None

    def send_sms(self, to: str, body: str):
        if self.client:
            message = self.client.messages.create(body=body, from_=TWILIO_FROM, to=to)
            return message.sid
        else:
            # fallback: print to console (demo)
            print(f"[NOTIFICATION to {to}]\n{body}\n")
            return None

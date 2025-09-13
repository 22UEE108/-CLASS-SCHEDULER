# Automated Class Scheduler with Placement Integration

## Overview
Managing college classes alongside placement interviews and online assessments can be hectic. This project **automates scheduling** so students never miss important classes or placement preparation.

It reschedules classes if they conflict with interviews, tracks attendance, and sends **notifications** to help students stay on top of their schedule.

## Features
- **Automatic rescheduling** of classes when placement interviews or assessments overlap  
- **Attendance tracking** for all classes, including compensated classes for placement prep  
- **Daily notifications** about what classes to attend or reschedule  
- **Demo mode** to simulate scheduling without connecting to real Gmail or Twilio  
- **Easy to extend** with new students, classes, or notifications  

## Tech Stack
- **Python** – Core logic and scheduling  
- **MySQL** – Stores students, classes, and attendance  
- **SQLAlchemy** – Connects Python to MySQL  
- **Optional:** Gmail API & Twilio for real email detection and SMS notifications
### How to Run
1. Clone the repository
2. Install dependencies
3. Create a `.env` file from `.env.example` (fill in credentials if needed)
4. Run the demo



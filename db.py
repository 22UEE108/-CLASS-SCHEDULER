import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Time, ForeignKey, Enum, SmallInteger
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "class_scheduler")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False, unique=True)
    templates = relationship("ClassTemplate", back_populates="student", cascade="all, delete-orphan")
    scheduled_classes = relationship("ScheduledClass", back_populates="student", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

class ClassTemplate(Base):
    __tablename__ = "class_templates"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    weekday = Column(SmallInteger, nullable=False)  # 0..6 (Mon..Sun)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    student = relationship("Student", back_populates="templates")

class ScheduledClass(Base):
    __tablename__ = "scheduled_classes"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    start_dt = Column(DateTime, nullable=False)
    end_dt = Column(DateTime, nullable=False)
    rescheduled_from = Column(Integer, nullable=True)
    is_interview = Column(Boolean, default=False)
    pending = Column(Boolean, default=False)
    student = relationship("Student", back_populates="scheduled_classes")
    attendance = relationship("Attendance", back_populates="scheduled_class", cascade="all, delete-orphan")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    scheduled_class_id = Column(Integer, ForeignKey("scheduled_classes.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(Enum('Present','Absent'), nullable=False)
    reason = Column(String(64), nullable=True)  # e.g., 'Interview' or 'Prep'
    student = relationship("Student", back_populates="attendance")
    scheduled_class = relationship("ScheduledClass", back_populates="attendance")

class Pending(Base):
    __tablename__ = "pending"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(200))
    original_start_dt = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

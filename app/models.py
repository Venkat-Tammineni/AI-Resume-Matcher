from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    ai_feedback = Column(Text, nullable=True)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text)
    location = Column(String(100))
    skills_required = Column(Text)  # Comma-separated or full paragraph

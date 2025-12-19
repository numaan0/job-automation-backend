# app/models/hiring_manager.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.sqlite import BLOB
from app.database import Base 

class HiringManager(Base):
    __tablename__ = "hiring_managers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)

    source_url = Column(Text, nullable=True)

    email = Column(String(255), nullable=True)
    email_pattern = Column(String(255), nullable=True)
    email_confidence = Column(Integer, nullable=True)

    email_attempts = Column(Integer, default=0)
    last_emailed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

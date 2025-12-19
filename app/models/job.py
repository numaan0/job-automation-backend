# app/models/job.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(String)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    contract_type = Column(String, nullable=True)
    category = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    apply_link = Column(String, nullable=True)
    source = Column(String, nullable=True)
    link_status = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
    collected_at = Column(DateTime)

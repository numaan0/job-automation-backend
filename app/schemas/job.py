# app/schemas/job.py

from pydantic import BaseModel, Field
from typing import List, Optional


class SkillMatchResult(BaseModel):
    """Skill matching for a single job"""
    matched_skills: List[str] = Field(description="Skills that match from your profile")
    missing_skills: List[str] = Field(description="Your skills not required")
    match_score: int = Field(description="Match percentage 0-100", ge=0, le=100)


class MatchedJob(BaseModel):
    """Single job with matching results"""
    id: str
    title: str
    company: str
    location: str
    apply_link: str
    posted_date: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    category: str
    match_score: int = Field(ge=0, le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    jd_preview: Optional[str] = Field(None, description="First 500 chars of JD")


class JobSearchResponse(BaseModel):
    """Final structured response"""
    status: str = Field(description="success or error")
    source: str = Field(default="Adzuna")
    query: str
    location: str
    total_found: int = Field(description="Total jobs from Adzuna")
    total_scraped: int = Field(description="Jobs successfully scraped")
    total_matched: int = Field(description="Jobs passing filter")
    matched_jobs: List[MatchedJob]

from pydantic import BaseModel, Field
from typing import List, Optional

class Person(BaseModel):
    name: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None

class PeopleExtractionResponse(BaseModel):
    people: List[Person]
    
    
class HiringManagerRequest(BaseModel):
    """
    Request body for the hiring manager discovery pipeline.
    Keep it in the same file as Person/PeopleExtractionResponse so schemas are co-located.
    """
    company: str = Field(..., example="Accenture")
    location: Optional[str] = Field("India", example="Bengaluru")
    job_title: Optional[str] = Field(
        None,
        example="Full Stack Engineer",
        description="Optional context to improve search relevance"
    )
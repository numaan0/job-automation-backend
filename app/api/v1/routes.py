# app/api/v1/routes.py

import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.agent_service import search_jobs_structured
from app.services.job_pipeline import search_and_match_jobs
from app.tools.adzuna_search import search_jobs_adzuna
from app.schemas.job import JobSearchResponse

router = APIRouter()


class JobSearchRequest(BaseModel):
    role: str
    location: str = "in"
    max_results: int = 20
    min_match_score: int = 40

class JobApplicationRequest(BaseModel):
    job_posting: str
    job_title: str
    company: str


class JobSearchRequest(BaseModel):
    role: str = Field(..., min_length=2)
    location: str = Field(default="in")
    max_results: int = Field(default=20, ge=1, le=50)
    min_match_score: int = Field(default=40, ge=0, le=100)


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs_endpoint(request: JobSearchRequest):
    """
    Complete job search and matching pipeline
    
    Returns structured Pydantic response
    """
    
    try:
        result = await search_and_match_jobs(
            query=request.role,
            location=request.location,
            max_results=request.max_results,
            min_match_score=request.min_match_score
        )
        
        return result
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/apply")
# async def apply_for_job_endpoint(request: JobApplicationRequest):
#     """
#     Multi-step job application workflow
#     Returns structured output with cover letter
#     """
    
#     try:
#         result = apply_for_job_structured(
#             job_posting=request.job_posting,
#             job_title=request.job_title,
#             company=request.company
#         )
        
#         return result
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

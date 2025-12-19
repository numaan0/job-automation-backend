# app/api/v1/routes.py

import traceback
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.schemas.hiring_manager import HiringManagerRequest
from app.services.agent_service import search_jobs_structured
# from app.services.job_pipeline import search_and_match_jobs
from app.services.automation_pipeline import run_full_automation
from app.services.hiring_manager_pipeline import run_hiring_manager_pipeline
from app.tools.adzuna_search import search_jobs_adzuna
from app.schemas.job import JobSearchResponse
from app.database import get_db
from app.services.job_collector import collect_jobs
from app.services.job_pipeline import match_unprocessed_jobs
from app.schemas.job import JobSearchResponse
from sqlalchemy.ext.asyncio import AsyncSession

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


# @router.post("/search", response_model=JobSearchResponse)
# async def search_jobs_endpoint(request: JobSearchRequest):
#     """
#     Complete job search and matching pipeline
    
#     Returns structured Pydantic response
#     """
    
#     try:
#         result = await search_and_match_jobs(
#             query=request.role,
#             location=request.location,
#             max_results=request.max_results,
#             min_match_score=request.min_match_score
#         )
        
#         return result
    
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))






class JobCollectionRequest(BaseModel):
    query: str = Field(..., min_length=2)
    location: str = Field(default="in")
    max_results: int = Field(default=20, ge=1, le=50)


class JobMatchingRequest(BaseModel):
    min_match_score: int = Field(default=40, ge=0, le=100)
    limit: int = Field(default=20, ge=1, le=100, description="Max jobs to process")

@router.post("/collect")
async def collect_jobs_endpoint(
    request: JobCollectionRequest,
    db: AsyncSession = Depends(get_db)   # <-- Inject async DB session
):
    try:
        result = await collect_jobs(
            db=db,  # Pass DB session
            query=request.query,
            location=request.location,
            max_results=request.max_results
        )
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match", response_model=JobSearchResponse)
async def match_jobs_endpoint(
    request: JobMatchingRequest,
    db: AsyncSession = Depends(get_db)   # <-- Inject async DB session
):
    try:
        result = await match_unprocessed_jobs(
            db=db,  # Pass DB session
            min_match_score=request.min_match_score,
            limit=request.limit
        )
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/hiring-managers")
async def hiring_managers_endpoint(
    request: HiringManagerRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await run_hiring_manager_pipeline(
        db=db,
        company=request.company,
        location=request.location,
        job_title=request.job_title
    )
    return result




class AutomationRequest(BaseModel):
    query: str
    location: str = "in"
    max_results: int = 20
    min_match_score: int = 40


@router.post("/run-automation")
async def run_automation_endpoint(
    request: AutomationRequest,
    db: AsyncSession = Depends(get_db)
):
    return await run_full_automation(
        db=db,
        query=request.query,
        location=request.location,
        max_results=request.max_results,
        min_match_score=request.min_match_score
    )


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
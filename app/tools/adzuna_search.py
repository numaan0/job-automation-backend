# app/tools/adzuna_search.py

from langchain_core.tools import tool
from app.services.adzuna_service import AdzunaService
import json
import asyncio

@tool
def search_jobs_adzuna(
    query: str, 
    location: str = "in",
    max_results: int = 20
) -> dict:
    """
    Search for jobs using Adzuna API (free tier: 166 searches/day)
    
    Args:
        query: Job title or keywords (e.g., "Python Developer", "Data Analyst")
        location: Country code (in=India, us=USA, uk=UK)
        max_results: Number of jobs to return (default 20, max 50)
        
    Returns:
        JSON string with job listings including real apply links
    """
    
    print(f"🔍 Searching Adzuna for: {query} in {location}")
    
    service = AdzunaService()
    
    # Search Adzuna
    result = asyncio.run(
        service.search_jobs(
            query=query,
            location=location,
            results_per_page=min(max_results, 50),
            max_days_old=7,
            sort_by="date"
        )
        ) 

    print(result,"I am here")
    print(type(result))
    if result["status"] == "success":
        jobs_count = len(result["jobs"])
        print(f"✅ Found {jobs_count} jobs from Adzuna")
        
        # Filter jobs with valid apply links
        jobs_with_links = [
            job for job in result["jobs"] 
            if job.get("apply_link")
        ]
        
        print(f"✅ {len(jobs_with_links)}/{jobs_count} jobs have apply links")
        print(jobs_with_links)
        print(result)
        return {
            "jobs": jobs_with_links,
            "total_results": result["total_results"],
            "source": "Adzuna",
            "status": "success"
        }
    
    else:
        print(f"❌ Adzuna search failed: {result.get('error')}")
        return {
            "jobs": [],
            "error": result.get("error"),
            "status": "failed"
        }

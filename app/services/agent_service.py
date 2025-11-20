# app/services/agent_service.py

from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.llm_service import get_llm
from app.tools.adzuna_search import search_jobs_adzuna
from app.tools.fetch_job_description import fetch_job_description
from app.tools.skill_matcher import match_skills

import json


# ============================================
# Pydantic Schemas
# ============================================

class SkillMatchResult(BaseModel):
    """Skill matching result"""
    match_score: int = Field(description="Match percentage 0-100")
    matched: List[str] = Field(description="Matched skills")
    missing: List[str] = Field(description="Missing skills")
    
    
class SearchJobAdzuna(BaseModel):
    """Get jobs via Adzuna API"""
    jobs: List[dict] = Field(description="List of jobs")
    total_results: int = Field(description="Total results")
    page: int = Field(description="Page number")
    results_per_page: int = Field(description="Results per page")


class ContactInfo(BaseModel):
    """Contact information for a person."""
    name: str = Field(description="The name of the person")
    email: str = Field(description="The email address of the person")
    phone: str = Field(description="The phone number of the person")
# ============================================
# Simple Agent with Structured Output
# ============================================

def get_job_agent():
    """Agent with tools and structured output for skill matching"""
    llm = get_llm(enable_grounding=False)
    
    tools = [search_jobs_adzuna]
    
    agent = create_agent(
    model=llm,
    response_format=SearchJobAdzuna ,tools=tools)

    
    
    # Agent with structured output baked in
    return agent


# ============================================
# Main Search Function (SIMPLE!)
# ============================================

def search_jobs_structured(
    query: str, 
    location: str = "in", 
    max_results: int = 20,
    min_match_score: int = 40
) -> dict:
    """Simple 4-step pipeline"""
    
    agent = get_job_agent()
    print(agent,"I am here")
    # ============================================
    # STEP 1: Search via agent
    # ============================================
    print(f"🔍 Searching for '{query}' in {location}")
    
    # result = agent.invoke({
    #     "messages": [{
    #         "role": "user",
    #         "content": f"Search for {query} jobs in {location}"
    #     }]
    # })
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Get the jobs from the search_jobs_adzuna and provide the response formatted"}]
    })

    print(result["structured_response"])
    
    print(result,"I am here")
    
    # Extract from intermediate steps
    raw_jobs = []
    for action, output in result.get("intermediate_steps", []):
        if action.tool == "search_jobs_adzuna":
            raw_jobs = json.loads(output).get("jobs", [])
            break
    
    if not raw_jobs:
        return {"status": "error", "message": "No jobs found", "matched_jobs": []}
    
    print(f"✅ Found {len(raw_jobs)} jobs")
    
    # ============================================
    # STEP 2: Fetch descriptions (Python loop)
    # ============================================
    print(f"📄 Fetching descriptions...")
    
    jobs_with_jd = []
    for job in raw_jobs[:max_results]:
        try:
            jd = fetch_job_description.invoke({"url": job["apply_link"]})
            if jd and not jd.startswith("ERROR"):
                job["full_description"] = jd
                jobs_with_jd.append(job)
        except:
            continue
    
    print(f"✅ Fetched {len(jobs_with_jd)} descriptions")
    
    # ============================================
    # STEP 3: Match skills with structured output
    # ============================================
    print(f"🧠 Matching skills...")
    
    enriched_jobs = []
    for job in jobs_with_jd:
        try:
            # Agent returns SkillMatchResult automatically!
            match_result = agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"Match skills for:\n{job['full_description'][:800]}"
                }]
            })
            
            # ✅ Access structured response directly
            skill_data = match_result["structured_response"]
            
            enriched_jobs.append({
                "id": job["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "apply_link": job["apply_link"],
                "posted_date": job["posted_date"],
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "match_score": skill_data.match_score,
                "matched_skills": skill_data.matched,
                "missing_skills": skill_data.missing
            })
        except Exception as e:
            print(f"⚠️ Match failed: {e}")
            continue
    
    print(f"✅ Matched {len(enriched_jobs)} jobs")
    
    # ============================================
    # STEP 4: Filter & sort (Python)
    # ============================================
    filtered = [j for j in enriched_jobs if j["match_score"] >= min_match_score]
    filtered.sort(key=lambda x: x["match_score"], reverse=True)
    
    print(f"✅ {len(filtered)} jobs passed filter")
    
    return {
        "status": "success",
        "source": "Adzuna",
        "total_fetched": len(raw_jobs),
        "total_matched": len(filtered),
        "matched_jobs": filtered
    }
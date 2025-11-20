# app/services/job_pipeline.py

from app.services.adzuna_service import AdzunaService
from app.services.scraper_service import JobScraperService
from app.services.skill_matcher_service import SkillMatcherService
from app.schemas.job import JobSearchResponse, MatchedJob
import pandas as pd
from datetime import datetime
import os


async def search_and_match_jobs(
    query: str,
    location: str = "in",
    max_results: int = 20,
    min_match_score: int = 40
) -> JobSearchResponse:
    """
    Complete job search pipeline
    
    Returns Pydantic model with structured data
    """
    
    # ==========================================
    # STEP 1: Search Adzuna (NO agent)
    # ==========================================
    print(f"🔍 Step 1: Searching Adzuna...")
    
    adzuna = AdzunaService()
    search_result = await adzuna.search_jobs(
        query=query,
        location=location,
        results_per_page=max_results
    )
    
    if search_result["status"] != "success":
        return JobSearchResponse(
            status="error",
            query=query,
            location=location,
            total_found=0,
            total_scraped=0,
            total_matched=0,
            matched_jobs=[]
        )
    
    raw_jobs = search_result["jobs"]
    print(f"✅ Found {len(raw_jobs)} jobs\n")
    
    # ==========================================
    # STEP 2: Save to CSV (NO agent)
    # ==========================================
    print(f"💾 Step 2: Saving raw jobs to CSV...")
    
    csv_path = save_jobs_to_csv(raw_jobs, query, location)
    print(f"✅ Saved to {csv_path}\n")
    
    # ==========================================
    # STEP 3: Scrape full JDs (NO agent)
    # ==========================================
    print(f"📄 Step 3: Scraping job descriptions...")
    
    scraper = JobScraperService()
    jobs_with_jd = []
    
    for idx, job in enumerate(raw_jobs, 1):
        print(f"  [{idx}/{len(raw_jobs)}] {job['title']}")
        
        if not job.get("apply_link"):
            print(f"    ↳ ❌ No link")
            continue
        
        full_jd = await scraper.fetch_job_description(job["apply_link"])
        
        if full_jd and len(full_jd) > 100:
            job["full_jd"] = full_jd
            jobs_with_jd.append(job)
            print(f"    ↳ ✅ {len(full_jd)} chars")
        else:
            print(f"    ↳ ❌ Failed")
    
    print(f"\n✅ Scraped {len(jobs_with_jd)} job descriptions\n")
    
    # ==========================================
    # STEP 4: Match skills (YES LLM with structured output)
    # ==========================================
    print(f"🧠 Step 4: Matching skills with LLM...")
    
    skill_matcher = SkillMatcherService()
    matched_jobs = []
    
    for idx, job in enumerate(jobs_with_jd, 1):
        print(f"  [{idx}/{len(jobs_with_jd)}] {job['title']}")
        
        try:
            # LLM returns SkillMatchResult (Pydantic)
            match_result = await skill_matcher.match_job(job["full_jd"])
            
            score = match_result.match_score
            print(f"    ↳ Score: {score}%")
            
            # Filter by score
            if score >= min_match_score:
                matched_jobs.append(MatchedJob(
                    id=str(job["id"]),
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    apply_link=job["apply_link"],
                    posted_date=job["posted_date"],
                    salary_min=job.get("salary_min"),
                    salary_max=job.get("salary_max"),
                    category=job.get("category", "N/A"),
                    match_score=score,
                    matched_skills=match_result.matched_skills,
                    missing_skills=match_result.missing_skills,
                    jd_preview=job["full_jd"][:500]
                ))
                print(f"    ↳ ✅ Matched!")
            else:
                print(f"    ↳ ❌ Below threshold")
        
        except Exception as e:
            print(f"    ↳ ❌ Error: {str(e)[:50]}")
    
    print(f"\n✅ {len(matched_jobs)} jobs passed filter\n")
    
    # ==========================================
    # STEP 5: Return Pydantic model
    # ==========================================
    return JobSearchResponse(
        status="success",
        query=query,
        location=location,
        total_found=len(raw_jobs),
        total_scraped=len(jobs_with_jd),
        total_matched=len(matched_jobs),
        matched_jobs=sorted(matched_jobs, key=lambda x: x.match_score, reverse=True)
    )


def save_jobs_to_csv(jobs: list, query: str, location: str) -> str:
    """Save raw Adzuna jobs to CSV"""
    
    df = pd.DataFrame(jobs)
    
    # Create exports folder
    os.makedirs("./data/exports", exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jobs_{query.replace(' ', '_')}_{location}_{timestamp}.csv"
    filepath = f"./data/exports/{filename}"
    
    df.to_csv(filepath, index=False)
    
    return filepath

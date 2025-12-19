import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from app.services.scraper_service import JobScraperService
from app.services.skill_matcher_service import SkillMatcherService
from app.schemas.job import JobSearchResponse, MatchedJob
from app.models.job import Job  # your ORM model

# Remove CSV_PATH, pandas import since no CSV

async def match_unprocessed_jobs(
    db: AsyncSession,
    min_match_score: int = 40,
    limit: int = 20
) -> JobSearchResponse:
    """
    Query unprocessed jobs from DB,
    scrape job descriptions,
    match skills using LLM,
    update processed flag in DB,
    return matched jobs in Pydantic model.
    """

    # Step 1: Fetch unprocessed jobs from DB
    result = await db.execute(
        select(Job).where(Job.processed == False).limit(limit)
    )
    unprocessed_jobs = result.scalars().all()

    if not unprocessed_jobs:
        return JobSearchResponse(
            status="success",
            query="N/A",
            location="N/A",
            total_found=0,
            total_scraped=0,
            total_matched=0,
            matched_jobs=[]
        )
    print(f"✅ Found {len(unprocessed_jobs)} unprocessed jobs (limit: {limit})\n")

    # Step 2: Scraping job descriptions
    print(f"📄 Step 2: Scraping job descriptions...")
    scraper = JobScraperService()
    jobs_with_jd = []

    for idx, job in enumerate(unprocessed_jobs, 1):
        print(f"  [{idx}/{len(unprocessed_jobs)}] {job.title}")

        if not job.apply_link:
            # Mark as processed even if no link
            job.processed = True
            await db.commit()
            print(f"    ↳ ❌ No link")
            continue

        full_jd = await scraper.fetch_job_description(job.apply_link)

        if full_jd and len(full_jd) > 100:
            job.full_jd = full_jd  # Add attribute dynamically or adjust model
            jobs_with_jd.append(job)
            print(f"    ↳ ✅ {len(full_jd)} chars")
        else:
            job.processed = True
            await db.commit()
            print(f"    ↳ ❌ Failed to scrape")

    print(f"\n✅ Scraped {len(jobs_with_jd)} job descriptions\n")

    # Step 3: Match skills using LLM
    print(f"🧠 Step 3: Matching skills...")
    skill_matcher = SkillMatcherService()
    matched_jobs = []

    for idx, job in enumerate(jobs_with_jd, 1):
        print(f"  [{idx}/{len(jobs_with_jd)}] {job.title}")

        try:
            match_result = await skill_matcher.match_job(job.full_jd)
            score = match_result.match_score
            print(f"    ↳ Score: {score}%")

            # Mark as processed
            job.processed = True
            await db.commit()

            if score >= min_match_score:
                matched_jobs.append(MatchedJob(
                    id=str(job.id),
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    apply_link=job.apply_link,
                    posted_date=job.posted_date,
                    salary_min=job.salary_min,
                    salary_max=job.salary_max,
                    category=getattr(job, "category", "N/A"),
                    match_score=score,
                    matched_skills=match_result.matched_skills,
                    missing_skills=match_result.missing_skills,
                    jd_preview=job.full_jd[:500]
                ))
                print(f"    ↳ ✅ Matched!")
            else:
                print(f"    ↳ ❌ Below threshold")

            print("I am going for sleep")
            await asyncio.sleep(5)  # Keep your delay or adjust as needed

        except Exception as e:
            job.processed = True
            await db.commit()
            print(f"    ↳ ❌ Error: {str(e)[:50]}")

    print(f"\n✅ Processed {len(unprocessed_jobs)} jobs")
    print(f"✅ {len(matched_jobs)} jobs passed filter\n")

    return JobSearchResponse(
        status="success",
        query="From DB",
        location="N/A",
        total_found=len(unprocessed_jobs),
        total_scraped=len(jobs_with_jd),
        total_matched=len(matched_jobs),
        matched_jobs=sorted(matched_jobs, key=lambda x: x.match_score, reverse=True)
    )

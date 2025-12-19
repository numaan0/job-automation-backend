# app/services/job_collector.py
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.job import Job
from app.services.adzuna_service import AdzunaService

async def collect_jobs(
    db: AsyncSession, 
    query: str, 
    location: str = "in", 
    max_results: int = 20
) -> dict:
    print(f"🔍 Collecting jobs for '{query}' in {location}...")

    adzuna = AdzunaService()
    search_result = await adzuna.search_jobs(query=query, location=location, results_per_page=max_results)

    if search_result["status"] != "success":
        return {"status": "error", "message": "Adzuna search failed", "jobs_added": 0}

    raw_jobs = search_result["jobs"]
    print(f"✅ Found {len(raw_jobs)} jobs from Adzuna")

    # Get existing IDs to avoid duplicates
    result = await db.execute(select(Job.id))
    existing_ids = set(row[0] for row in result.scalars().all())
    print(f"📄 Found {len(existing_ids)} existing jobs in database")

    new_jobs = []
    for job in raw_jobs:
        job_id = str(job["id"])
        if job_id in existing_ids:
            continue

        new_jobs.append(Job(
            id=job_id,
            title=job.get("title"),
            company=job.get("company"),
            location=job.get("location"),
            description=job.get("description"),
            salary_min=job.get("salary_min"),
            salary_max=job.get("salary_max"),
            contract_type=job.get("contract_type"),
            category=job.get("category"),
            posted_date=job.get("posted_date"),
            apply_link=job.get("apply_link"),
            source=job.get("source"),
            link_status=job.get("link_status"),
            processed=False,
            collected_at=datetime.now()
        ))

    jobs_added = 0
    for job_obj in new_jobs:
        db.add(job_obj)
        try:
            await db.commit()
            jobs_added += 1
        except IntegrityError:
            await db.rollback()

    print(f"✅ Added {jobs_added} new jobs (skipped {len(raw_jobs) - jobs_added} duplicates)")
    return {
        "status": "success",
        "total_found": len(raw_jobs),
        "jobs_added": jobs_added,
        "duplicates_skipped": len(raw_jobs) - jobs_added,
        "db_path": "SQLite: ./data/jobs.db"
    }

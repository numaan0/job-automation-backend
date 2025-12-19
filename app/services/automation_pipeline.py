from sqlalchemy.ext.asyncio import AsyncSession
from app.services.job_collector import collect_jobs
from app.services.job_pipeline import match_unprocessed_jobs
from app.services.hiring_manager_pipeline import run_hiring_manager_pipeline


async def run_full_automation(
    db: AsyncSession,
    query: str,
    location: str,
    max_results: int,
    min_match_score: int
):
    # Step 1 — Collect jobs
    collected = await collect_jobs(
        db=db,
        query=query,
        location=location,
        max_results=max_results
    )

    # Step 2 — Match jobs
    matched = await match_unprocessed_jobs(
        db=db,
        min_match_score=min_match_score,
        limit=max_results
    )

    # Step 3 — Hiring managers (company-level)
    # NOTE: this can be looped per matched job later
    hiring_managers = await run_hiring_manager_pipeline(
        db=db,
        company=query,   # or derive from matched jobs later
        location=location,
        job_title=None
    )

    return {
        "status": "success",
        "jobs_collected": collected.get("total_found"),
        "jobs_matched": matched.total_matched,
        "hiring_managers_found": hiring_managers.get("total_managers_found"),
        "message": "automation complete"
    }

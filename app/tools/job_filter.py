# app/tools/job_filter.py

from langchain_core.tools import tool
import json

@tool
def filter_jobs_by_skillmatch(jobs_json: str, min_score: int = 40) -> str:
    """
    Filters a list of job objects based on match_score.

    Expected input (stringified JSON):
    {
        "jobs": [
            {
                "id": "...",
                "title": "...",
                "company": "...",
                "location": "...",
                "apply_link": "...",
                "match_score": 85,
                "matched": [...],
                "missing": [...]
            },
            ...
        ]
    }

    Returns structured JSON:
    {
        "matched_jobs": [...],
        "total_matched": 4
    }
    """

    try:
        data = json.loads(jobs_json)

        jobs = data.get("jobs", [])

        filtered = [
            job for job in jobs
            if isinstance(job.get("match_score"), (int, float)) 
            and job["match_score"] >= min_score
        ]

        return json.dumps({
            "matched_jobs": filtered,
            "total_matched": len(filtered)
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "error": str(e)
        })

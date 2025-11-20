# import traceback
# from langchain_core.tools import tool
# from app.services.llm_service import get_llm
# import json
# import re


from langchain_core.tools import tool
from app.services.llm_service import get_llm
from app.schemas.job import JobSearchResponse
import json
import traceback

@tool
def search_jobs(role_name: str, sort_latest: bool = True) -> str:
    """
    Search for job listings using Google Search grounding
    
    Args:
        role_name: Job title to search for (e.g., "Python Developer", "Data Analyst")
        sort_latest: If True, focus on most recent postings. Default is True.
    
    Returns:
        JSON string with list of jobs containing title, description, company, and link
    """
    
    llm = get_llm(enable_grounding=True)
    
    # Force structured output - guarantees valid JSON
    structured_llm = llm.with_structured_output(JobSearchResponse)
    
    time_filter = "from the last 3 days" if sort_latest else ""
    print("Searching jobs for role:", role_name, "Latest only:", sort_latest, "Time filter:", time_filter)
    
    prompt = f"""Search Google for "{role_name}" job openings {time_filter}.

Find exactly 20 job postings.

For EACH job, extract:
- title: exact job title
- company: company name  
- description: brief description (1-2 sentences)
- source: "LinkedIn", "Indeed", or "Naukri"
- location: job location
- posted_date: when posted (e.g., "2 days ago")

Return ALL 20 jobs. Do not skip any."""

    
    try:
        # structured_llm guarantees JobSearchResponse object
        response = structured_llm.invoke(prompt)
        print("Search Jobs Response:", response)
        # response is already a JobSearchResponse object
        return json.dumps({
            "jobs": [
                {
                    "title": job.title,
                    "company": job.company,
                    "description": job.description,
                    "source": job.source,
                    "location": job.location,}
                for job in response.jobs
            ]
        }, indent=2)
    
    except Exception as e:
        traceback.print_exc()
        return json.dumps({
            "error": f"Search failed: {str(e)}"
        })

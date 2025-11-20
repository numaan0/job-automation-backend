# app/services/adzuna_service.py

import httpx
from typing import List, Dict, Optional
from app.core.config import get_settings

settings = get_settings()

class AdzunaService:
    """
    Adzuna API client for job search
    Free tier: 5,000 requests/month = 166/day
    """
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self):
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY
    
    async def search_jobs(
        self,
        query: str,
        location: str = "in",  # India country code
        results_per_page: int = 20,
        page: int = 1,
        max_days_old: int = 7,
        sort_by: str = "date"  # "date" or "relevance"
    ) -> Dict:
        """
        Search for jobs on Adzuna
        
        Args:
            query: Job title/keywords (e.g., "Python Developer")
            location: Country code (in=India, us=USA, uk=UK)
            results_per_page: Jobs per page (max 50)
            page: Page number (for pagination)
            max_days_old: Only jobs posted in last N days
            sort_by: "date" (latest first) or "relevance"
            
        Returns:
            Dict with jobs list and metadata
        """
        
        url = f"{self.BASE_URL}/{location}/search/{page}"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": results_per_page,
            "what": query, 
            "max_days_old": max_days_old,
            "sort_by": sort_by
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse Adzuna response
                jobs = self._parse_jobs(data.get("results", []))
                
                return {
                    "jobs": jobs,
                    "total_results": data.get("count", 0),
                    "page": page,
                    "results_per_page": results_per_page,
                    "status": "success"
                }
            
            except httpx.HTTPStatusError as e:
                print(f"❌ Adzuna API error: {e.response.status_code}")
                return {
                    "jobs": [],
                    "error": f"API error: {e.response.status_code}",
                    "status": "failed"
                }
            
            except Exception as e:
                print(f"❌ Adzuna request failed: {str(e)}")
                return {
                    "jobs": [],
                    "error": str(e),
                    "status": "failed"
                }
    
    def _parse_jobs(self, results: List[Dict]) -> List[Dict]:
        """Parse Adzuna API response into clean job objects"""
        
        jobs = []
        
        for result in results:
            job = {
                "id": result.get("id"),
                "title": result.get("title", "N/A"),
                "company": result.get("company", {}).get("display_name", "N/A"),
                "location": result.get("location", {}).get("display_name", "N/A"),
                "description": result.get("description", "")[:300],  # First 300 chars
                "salary_min": result.get("salary_min"),
                "salary_max": result.get("salary_max"),
                "contract_type": result.get("contract_type", "N/A"),  # Full-time, Contract, etc.
                "category": result.get("category", {}).get("label", "N/A"),
                "posted_date": result.get("created", "N/A"),
                "apply_link": result.get("redirect_url"),  # ✅ REAL apply link
                "source": "Adzuna",
                "link_status": "found" if result.get("redirect_url") else "not_found"
            }
            
            jobs.append(job)
            
        print(f"✅ Parsed {len(jobs)} jobs from Adzuna")
        print(jobs)        
        return jobs

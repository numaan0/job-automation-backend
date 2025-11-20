# app/services/scraper_service.py

import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import Optional


class JobScraperService:
    """
    Scrapes full job descriptions from job posting URLs
    """
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    
    async def fetch_job_description(self, url: str) -> Optional[str]:
        """
        Fetch full job description from job posting URL
        
        Args:
            url: Job posting URL (from Adzuna redirect_url)
            
        Returns:
            Full job description text or None if failed
        """
        
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=15.0,
                follow_redirects=True  # Follow Adzuna redirects
            ) as client:
                
                # Fetch page
                response = await client.get(url)
                
                if response.status_code != 200:
                    print(f"  ↳ ❌ HTTP {response.status_code}")
                    return None
                
                # Parse HTML
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove unwanted elements
                for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
                    tag.decompose()
                
                # Extract text
                text = soup.get_text(separator="\n", strip=True)
                
                # Clean up
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                cleaned_text = "\n".join(lines)
                
                # Rate limit (be respectful)
                await asyncio.sleep(1)
                
                # Return first 5000 chars (enough for LLM)
                return cleaned_text[:5000] if cleaned_text else None
        
        except httpx.TimeoutException:
            print(f"  ↳ ❌ Timeout")
            return None
        
        except httpx.HTTPError as e:
            print(f"  ↳ ❌ HTTP Error: {str(e)[:50]}")
            return None
        
        except Exception as e:
            print(f"  ↳ ❌ Error: {str(e)[:50]}")
            return None

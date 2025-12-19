# app/services/scraper_service.py

import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import Optional


class JobScraperService:
    """
    Handles:
      - scraping job descriptions from job posting pages
      - scraping clean text from general web pages (for hiring manager search)
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

        # Persistent client for multiple requests
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=15.0,
            follow_redirects=True
        )

    # ------------------------------------------------------
    #  SCRAPE JOB DESCRIPTION (from job apply links)
    # ------------------------------------------------------
    async def fetch_job_description(self, url: str) -> Optional[str]:
        """
        Fetch a job description from a job posting URL.
        Used for Adzuna job links.
        """

        try:
            response = await self.client.get(url)

            if response.status_code != 200:
                print(f"  ↳ ❌ HTTP {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove irrelevant elements
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned = "\n".join(lines)

            await asyncio.sleep(1)  # avoid rate limit

            return cleaned[:5000] if cleaned else None

        except Exception as e:
            print(f"  ↳ ❌ Scrape Error: {str(e)[:80]}")
            return None

    # ------------------------------------------------------
    #  SCRAPE GENERAL WEB TEXT (for hiring manager pages)
    # ------------------------------------------------------
    async def fetch_text(self, url: str) -> str:
        """
        Extract clean text from ANY webpage.
        Used for Tavily hiring manager links.
        """

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]

            return "\n".join(lines)

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return ""

    async def close(self):
        await self.client.aclose()

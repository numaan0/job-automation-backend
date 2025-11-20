# app/tools/fetch_job_description.py

from langchain_core.tools import tool
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

@tool
def fetch_job_description(url: str) -> str:
    """
    Safely fetches the full job description from a job posting URL.

    Steps:
    1. Check robots.txt (avoid disallowed sites)
    2. Send browser-like GET request
    3. Extract readable text from HTML
    4. Return plain text (no HTML)
    """

    try:
        # ---------------------------------------
        # 1. Extract base site for robots.txt
        # ---------------------------------------
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base}/robots.txt"

        client = httpx.Client(headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9"
        }, timeout=10.0)

        # ---------------------------------------
        # 2. Respect robots.txt
        # ---------------------------------------
        try:
            robots = client.get(robots_url)
            if "Disallow" in robots.text:
                disallow_rules = [
                    line.split(":")[1].strip()
                    for line in robots.text.splitlines()
                    if line.startswith("Disallow")
                ]

                for rule in disallow_rules:
                    if parsed.path.startswith(rule):
                        return "ROBOTS_BLOCKED"
        except:
            # If robots.txt fails, we still proceed safely
            pass

        # ---------------------------------------
        # 3. Fetch the page with browser headers
        # ---------------------------------------
        page = client.get(url)
        if page.status_code != 200:
            return f"FAILED_TO_FETCH_PAGE: {page.status_code}"

        # ---------------------------------------
        # 4. Parse HTML → readable text
        # ---------------------------------------
        soup = BeautifulSoup(page.text, "html.parser")

        # Remove scripts, styles, navbars, footer
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        cleaned = "\n".join([line.strip() for line in text.splitlines() if line.strip()])

        # Rate limit → avoid bans
        time.sleep(1)

        return cleaned[:5000]   # limit size for LLM safety

    except Exception as e:
        return f"ERROR: {str(e)}"

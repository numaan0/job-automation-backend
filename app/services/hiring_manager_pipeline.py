# app/services/hiring_manager_pipeline.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tavily_service import find_hiring_manager_urls
from app.services.scraper_service import JobScraperService
from app.services.people_extractor_service import LLMPeopleExtractor
from app.services.email_pattern_service import EmailPatternService
from app.services.hiring_manager_service import upsert_hiring_manager

from app.schemas.hiring_manager import Person
from app.models.hiring_manager import HiringManager


async def run_hiring_manager_pipeline(
    db: AsyncSession,
    company: str,
    location: str,
    job_title: str,
    max_urls: int = 8
):
    """
    Full pipeline until Step 6.
    No email sending — final step prints 'sent'.

    Steps:
    1. Tavily → Find URLs where hiring managers appear
    2. Scrape each URL
    3. LLM → Extract names, titles, company
    4. Upsert into DB
    5. Generate email patterns
    6. Return structured output
    """

    print("\n🔍 STEP 1 — Searching for hiring manager URLs...\n")

    urls = await find_hiring_manager_urls(company, location, limit=max_urls)

    print(f"   → Found {len(urls)} candidate pages\n")

    if not urls:
        return {
            "status": "no_urls",
            "message": f"No hiring manager pages found for {company}"
        }

    scraper = JobScraperService()
    extractor = LLMPeopleExtractor()

    extracted_people = []

    print("📄 STEP 2 — Scraping URLs...\n")

    for idx, url in enumerate(urls, 1):
        print(f"  [{idx}/{len(urls)}] Scraping: {url}")

        text = await scraper.fetch_text(url)
        if not text or len(text) < 100:
            print("    ↳ ❌ Not enough text, skipping\n")
            continue

        print("    ↳ Extracting people...")

        people_response = await extractor.extract_people(text)
        people = people_response.people

        if not people:
            print("    ↳ ❌ No managers found\n")
            continue

        print(f"    ↳ ✅ Found {len(people)} people\n")

        for person in people:
            # STEP 4 — Store in DB
            manager_obj = await upsert_hiring_manager(
                db=db,
                person=person,
                source_url=url
            )

            extracted_people.append({
                "name": person.name,
                "title": person.title,
                "company": person.company,
                "location": person.location,
                "profile_source": url,
            })

        # Rate limit respectfully
        await asyncio.sleep(2)

    print("\n🎯 STEP 6 — Pipeline complete (no email sent)")
    print("sent\n")  # <-- Testing only

    return {
        "status": "success",
        "company": company,
        "location": location,
        "total_managers_found": len(extracted_people),
        "managers": extracted_people
    }

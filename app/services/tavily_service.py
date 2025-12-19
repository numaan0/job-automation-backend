# app/services/tavily_service.py

from tavily import TavilyClient
from app.core.config import get_settings

# Initialize client

settings = get_settings()
tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

class TavilySearchService:

    @staticmethod
    async def search_web(query: str, max_results: int = 10):
        """
        Perform a Tavily web search.
        Returns list of URLs + metadata.
        """

        try:
            response = tavily.search(
                query=query,
                max_results=max_results,
                include_domains=None,  # Allow global search
                include_raw_content=False
            )

            results = response.get("results", [])
            return [item["url"] for item in results]

        except Exception as e:
            print(f"❌ Tavily search failed: {e}")
            return []
        
        
HIRING_MANAGER_KEYWORDS = [
"engineering manager",
"software engineering manager",
"tech lead",
"technical lead",
"hiring manager",
"delivery manager",
"software manager",
"development manager",
"engineering leadership"
]

def build_queries(company: str, location: str):
    """
    Build multiple powerful OSINT queries.
    """

    queries = []

    for kw in HIRING_MANAGER_KEYWORDS:
        queries.append(f"{company} {kw} {location}")
        queries.append(f"{company} {kw} {location} contact")
        queries.append(f"{company} {kw} {location} email")
        queries.append(f"{company} {kw} {location} team")

    return list(set(queries))



async def find_hiring_manager_urls(company: str, location: str, limit: int = 20):
    """
    Build search queries → send to Tavily → return unique URLs.
    """

    queries = build_queries(company, location)

    all_urls = set()

    for q in queries:
        urls = await TavilySearchService.search_web(q, max_results=5)
        for url in urls:
            all_urls.add(url)

        if len(all_urls) >= limit:
            break  # stop early if enough URLs

    return list(all_urls)[:limit]

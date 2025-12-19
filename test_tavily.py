# test_tavily.py

import asyncio
from app.services.tavily_service import find_hiring_manager_urls

async def test():
    urls = await find_hiring_manager_urls("Accenture", "Bangalore")
    print(urls)

asyncio.run(test())

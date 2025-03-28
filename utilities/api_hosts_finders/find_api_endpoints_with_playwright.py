import re
import config
from custom_logger import get_logger
from playwright.async_api import async_playwright
from utilities import async_wait_for_page_load, api_endpoints_parser


logger = get_logger("find_api_endpoints_with_playwright")


async def find_api_endpoints_with_playwright(target_url: str) -> (set, set):
    async with async_playwright() as playwright:
        try:
            chromium = playwright.chromium  # "firefox" || "webkit".
            browser = await chromium.launch()
            page = await browser.new_page()
            await page.goto(target_url)
            await async_wait_for_page_load()
            logs = await page.evaluate("() => window.performance?.getEntries?.() || []")

            api_requests: set = set()
            other_requests: set = set()
            for log in logs:
                if "name" in log:
                    api_match: bool = False
                    for pattern in config.API_PATTERNS:
                        if matches := re.findall(pattern, log["name"]):
                            api_match = True
                            api_requests.update(matches)
                    if not api_match and log["name"].startswith('http'):
                        other_requests.add(log["name"])

            return api_requests, other_requests
        except Exception as e:
            logger.exception(f"[!] playwright api kontrolü başarısız: {e}")

if __name__ == '__main__':
    import asyncio
    r = asyncio.run(find_api_endpoints_with_playwright("https://farukseker.com.tr"))
    from pprint import pprint
    pprint(r)

from models import ContentResultModel
import asyncio
import config
import aiofiles
from custom_logger import get_logger
from playwright.async_api import async_playwright
from utilities import async_wait_for_page_load, api_endpoints_parser

logger = get_logger("content_analysis_with_playwright")


async def content_analysis_with_playwright(target_url: str) -> ContentResultModel:
    content_result_model: ContentResultModel = ContentResultModel(processors='Playwright')
    async with async_playwright() as playwright:
        try:
            chromium = playwright.chromium  # "firefox" || "webkit".
            browser = await chromium.launch()
            await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await browser.new_page()
            await page.goto(target_url)
            await async_wait_for_page_load()

            for _ in range(10, 0, -1):
                await asyncio.sleep(1)
                await page.evaluate("window.scrollBy(0, 1);")

            content_result_model.title = await page.title()
            content_result_model.content = await page.content()
            content_result_model.raw_html = await page.content()

            content_result_model.page_preview_path = str(config.TEMP_FOLDER / 'content-preview-playwright.png')
            async with aiofiles.open(content_result_model.page_preview_path, 'wb') as _content:
                content = await page.screenshot(full_page=True)
                await _content.write(content)
            logs = await page.evaluate("() => window.performance?.getEntries?.() || []")
            logs = [log["name"] for log in logs if "name" in log]
            content_result_model.api_requests, content_result_model.other_requests = api_endpoints_parser(logs)

        except Exception as exception:
            logger.exception(exception, exc_info=True)
            content_result_model.has_err = True
            raise exception

        finally:
            await page.close()
        return content_result_model

if __name__ == '__main__':
    r = asyncio.run(content_analysis_with_playwright("https://farukseker.com.tr"))
    from pprint import pprint
    pprint(r)

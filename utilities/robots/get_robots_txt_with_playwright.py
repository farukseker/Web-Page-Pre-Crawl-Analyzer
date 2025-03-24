from bs4 import BeautifulSoup
from models import RobotTxtResult
from custom_logger import get_logger
from playwright.async_api import async_playwright


logger = get_logger("get_robots_txt_with_playwright")

# playwright: Playwright,


async def get_robots_txt_with_playwright(url: str) -> RobotTxtResult:
    robot_txt_result: RobotTxtResult = RobotTxtResult(processor='Playwright')
    async with async_playwright() as playwright:
        chromium = playwright.chromium  # "firefox" || "webkit".
        browser = await chromium.launch()
        try:
            page = await browser.new_page()
            await page.goto(url)
            content = await page.content()
            if len(content) > 1:
                soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
                robot_txt_result.content = soup.text
                robot_txt_result.http_status = 200
        except Exception as exception:
            logger.critical(exception)
            robot_txt_result.http_status = True
        finally:
            await browser.close()
            return robot_txt_result

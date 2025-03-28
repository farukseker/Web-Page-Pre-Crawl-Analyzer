import re
import config
from custom_logger import get_logger
from selenium import webdriver
from utilities import undetected_chromedriver_killer
import time

logger = get_logger("check_page_api_urls_with_selenium")


def check_page_api_urls_with_selenium(target_url) -> (set, set):
    api_requests: set = set()
    other_requests: set = set()
    try:
        chrome_driver: webdriver.Chrome = webdriver.Chrome(options=config.make_chrome_options())
        chrome_driver.get(target_url)

        for _ in range(10, 0, -1):
            time.sleep(1)
            chrome_driver.execute_script("window.scrollBy(0, 1);")
            print(f'{_}.second left')

        logs = chrome_driver.execute_script("return window.performance.getEntries();")

        for log in logs:
            if "name" in log:
                print(log['name'])
                api_match: bool = False
                for pattern in config.API_PATTERNS:
                    if matches := re.findall(pattern, log["name"]):
                        api_match = True
                        api_requests.update(matches)
                if not api_match and log["name"].startswith('http'):
                    other_requests.add(log["name"])
        if not api_requests:
            logger.info("[✖] Sayfada XHR veya Fetch API istekleri bulunamadı.")
    except Exception as exception:
        logger.critical(exception)
    finally:
        if callable(chrome_driver):
            undetected_chromedriver_killer(driver=chrome_driver)
        return api_requests, other_requests


if __name__ == '__main__':
    r = check_page_api_urls_with_selenium("https://farukseker.com.tr")
    print(r)

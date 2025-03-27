from utilities import undetected_chromedriver_killer
from custom_logger import get_logger
import undetected_chromedriver
import config
import time
import re

logger = get_logger("find_api_endpoints_with_undetected_chromedriver")


def find_api_endpoints_with_undetected_chromedriver(target_url: str):
    api_requests: set = set()
    other_requests: set = set()
    try:
        driver = undetected_chromedriver.Chrome(options=config.make_chrome_options(), keep_alive=True)
        with open(config.BASE_DIR / "script.js", 'r', encoding='utf-8') as script_file:
            script = script_file.read()
            driver.execute_script(script)
        time.sleep(.2)
        driver.get(target_url)
        for _ in range(10, 0, -1):
            time.sleep(1)
            driver.execute_script("window.scrollBy(0, 1);")
            print(f'{_}.second left')

        logs = driver.execute_script("return window.performance.getEntries();")

        for log in logs:
            if "name" in log:
                api_match: bool = False
                for pattern in config.API_PATTERNS:
                    if matches := re.findall(pattern, log["name"]):
                        api_match = True
                        api_requests.update(matches)
                if not api_match and log["name"].startswith('http'):
                    other_requests.add(log["name"])
        if not api_requests:
            logger.info("[✖] Sayfada XHR veya Fetch API istekleri bulunamadı.")
        return api_requests, other_requests
    except Exception as exception:
        logger.critical(exception)
    finally:
        undetected_chromedriver_killer(driver=driver)


if __name__ == '__main__':
    from pprint import pprint
    r = find_api_endpoints_with_undetected_chromedriver('https://farukseker.com.tr')
    pprint(r[0])
    pprint(r[1])

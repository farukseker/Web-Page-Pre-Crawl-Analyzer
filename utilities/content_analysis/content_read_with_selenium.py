from custom_logger import get_logger
from models import ContentResultModel
import config
from selenium import webdriver
from utilities import undetected_chromedriver_killer, api_endpoints_parser
import time


logger = get_logger("content_analysis_with_selenium")


def content_analysis_with_selenium(target_url: str) -> ContentResultModel:
    content_result_model: ContentResultModel = ContentResultModel(processors='selenium')
    try:
        chrome_driver: webdriver.Chrome = webdriver.Chrome(options=config.make_chrome_options())
        chrome_driver.get(target_url)

        for _ in range(10, 0, -1):
            time.sleep(1)
            chrome_driver.execute_script("window.scrollBy(0, 1);")
        try:
            logs = chrome_driver.execute_script("return window.performance.getEntries();")
            logs = [log["name"] for log in logs if "name" in log]
        except Exception as exception:
            logger.exception(exception)
            content_result_model.has_err = True
            logs = []

        content_result_model.api_requests, content_result_model.other_requests = api_endpoints_parser(logs)

        content_result_model.title = chrome_driver.title
        content_result_model.content = chrome_driver.page_source
        content_result_model.raw_html = chrome_driver.page_source

        content_result_model.page_preview_path = str(config.TEMP_FOLDER / 'content-preview-selenium.png')
        width = chrome_driver.execute_script("return document.documentElement.scrollWidth")
        height = chrome_driver.execute_script("return document.documentElement.scrollHeight")
        chrome_driver.set_window_size(width, height)
        chrome_driver.get_screenshot_as_file(content_result_model.page_preview_path)

    except Exception as exception:
        logger.exception(exception)
        content_result_model.has_err = True
    finally:
        undetected_chromedriver_killer(chrome_driver)

    return content_result_model


if __name__ == '__main__':
    r = content_analysis_with_selenium('https://farukseker.com.tr')
    print(r)

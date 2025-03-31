from utilities import undetected_chromedriver_killer, api_endpoints_parser
from models import ContentResultModel
from custom_logger import get_logger
import undetected_chromedriver
import config
import time

logger = get_logger("content_analysis_with_undetected_chromedriver")


def content_analysis_with_undetected_chromedriver(url) -> ContentResultModel:
    content_result_model: ContentResultModel = ContentResultModel(processors='undetected_chromedriver')
    driver = undetected_chromedriver.Chrome(options=config.make_chrome_options(), keep_alive=True)
    try:
        with open(config.BASE_DIR / "script.js", 'r', encoding='utf-8') as script_file:
            script = script_file.read()
            driver.execute_script(script)

        time.sleep(.2)
        driver.get(url)
        for _ in range(10, 0, -1):
            time.sleep(1)
            driver.execute_script("window.scrollBy(0, 1);")
            print(f'{_}.second left')
        content_result_model.title = driver.title
        content_result_model.content = driver.page_source
        content_result_model.raw_html = driver.page_source
        content_result_model.http_status = 200
        content_result_model.page_preview_path = str(config.TEMP_FOLDER / 'content-preview-selenium.png')
        width = driver.execute_script("return document.documentElement.scrollWidth")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        driver.set_window_size(width, height)
        driver.get_screenshot_as_file(content_result_model.page_preview_path)

        logs = driver.execute_script("return window.performance.getEntries();")
        logs = [log["name"] for log in logs if "name" in log]
        content_result_model.api_requests, content_result_model.other_requests = api_endpoints_parser(logs)

    except Exception as exception:
        logger.exception(exception)
        content_result_model.has_err = True
    finally:
        undetected_chromedriver_killer(driver)

    return content_result_model


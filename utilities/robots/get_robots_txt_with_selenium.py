import config
from models import RobotTxtResult
from custom_logger import get_logger
from bs4 import BeautifulSoup
from selenium import webdriver
from utilities import undetected_chromedriver_killer

logger = get_logger("get_robots_txt_with_selenium")


def get_robots_txt_with_selenium(url: str) -> RobotTxtResult:
    chrome_driver: webdriver.Chrome = webdriver.Chrome(options=config.make_chrome_options())
    robot_txt_result: RobotTxtResult = RobotTxtResult(processor='Selenium')
    try:
        chrome_driver.maximize_window()
        chrome_driver.get(url)
        content = chrome_driver.page_source
        if len(content) > 1:
            soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
            robot_txt_result.content = soup.text
            robot_txt_result.http_status = 200
    except Exception as exception:
        logger.critical(exception, exc_info=True)
        robot_txt_result.http_status = 0
        robot_txt_result.has_err = True
    finally:
        undetected_chromedriver_killer(driver=chrome_driver)
        if callable(chrome_driver):
            chrome_driver.close()

    return robot_txt_result

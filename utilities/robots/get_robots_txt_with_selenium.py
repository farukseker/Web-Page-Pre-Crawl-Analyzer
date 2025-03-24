import config
import requests
from models import RobotTxtResult
from custom_logger import get_logger
from bs4 import BeautifulSoup
from selenium import webdriver
from utilities import undetected_chromedriver_killer

logger = get_logger("get_robots_txt_with_selenium")


def get_robots_txt_with_selenium(url: str, driver: webdriver) -> RobotTxtResult:
    robot_txt_result: RobotTxtResult = RobotTxtResult(processor='Selenium')
    try:
        driver.maximize_window()
        driver.get(url)
        content = driver.page_source
        if len(content) > 1:
            soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
            robot_txt_result.content = soup.text
            robot_txt_result.http_status = 200
    except Exception as exception:
        logger.critical(exception, exc_info=True)
        robot_txt_result.http_status = 0
        robot_txt_result.has_err = True
    # finally:
        # undetected_chromedriver_killer(driver=driver)
        # if callable(driver):
        #     driver.close()

    return robot_txt_result

from bs4 import BeautifulSoup
from models import RobotTxtResult
from custom_logger import get_logger


logger = get_logger("get_robots_txt_with_undetected_chromedriver")


def get_robots_txt_with_undetected_chromedriver(url: str, undetected_chromedriver) -> RobotTxtResult:
    robot_txt_result: RobotTxtResult = RobotTxtResult(processor='Undetected Chromedriver')
    try:
        undetected_chromedriver.get(url)
        content = undetected_chromedriver.page_source
        if len(content) > 1:
            soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
            robot_txt_result.http_status = 200
            robot_txt_result.content = soup.text
        else:
            robot_txt_result.content = content
            robot_txt_result.has_err = True
    except Exception as exception:
        logger.critical(exception)
        robot_txt_result.has_err = False
    finally:
        return robot_txt_result

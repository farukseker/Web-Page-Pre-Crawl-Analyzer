from bs4 import BeautifulSoup
from utilities import undetected_chromedriver_killer
import config
from models import RobotTxtResult
from custom_logger import get_logger
import undetected_chromedriver

logger = get_logger("get_robots_txt_with_undetected_chromedriver")


def get_robots_txt_with_undetected_chromedriver(url: str) -> RobotTxtResult:
    uc_driver: undetected_chromedriver = undetected_chromedriver.Chrome(options=config.make_chrome_options(),
                                                                        keep_alive=True)
    uc_driver.execute_script(config.ANTI_BOT_CLOAKER_SCRIPT)

    robot_txt_result: RobotTxtResult = RobotTxtResult(processor='Undetected Chromedriver')
    try:
        uc_driver.get(url)
        content = uc_driver.page_source
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
        undetected_chromedriver_killer(driver=uc_driver)
        return robot_txt_result

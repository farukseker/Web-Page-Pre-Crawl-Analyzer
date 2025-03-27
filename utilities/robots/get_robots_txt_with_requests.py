import gzip
import requests
from models import RobotTxtResult
from custom_logger import get_logger
import config

logger = get_logger("get_robots_txt_with_requests")


def get_robots_txt_with_requests(url: str) -> RobotTxtResult:
    session: requests.Session = requests.Session()
    robot_txt_result: RobotTxtResult = RobotTxtResult(processor='Requests')
    response = session.get(url, headers=config.HEADERS)
    try:
        if response.status_code == 200:
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    content = gzip.decompress(response.content)
                    robot_txt_result.content = content.decode(errors="ignore")
                except:
                    robot_txt_result.content = response.text if response.text.strip() else response.content.decode(
                        errors="ignore"
                    )
            else:
                robot_txt_result.content = response.text if response.text.strip() else response.content.decode(
                    errors="ignore"
                )
        else:
            robot_txt_result.content = response.text
        robot_txt_result.http_status = response.status_code
    except requests.RequestException as exception:
        logger.exception("Request failed: %s", exception, exc_info=True)
        robot_txt_result.http_status = getattr(exception.response, 'status_code', 0)
    except Exception as exception:
        logger.critical(exception, exc_info=True)
        robot_txt_result.has_err = True
    finally:
        session.close()
    return robot_txt_result


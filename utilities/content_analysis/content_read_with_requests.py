from models import ContentResultModel
from utilities import api_endpoints_parser
import requests
from bs4 import BeautifulSoup
from custom_logger import get_logger
import config

logger = get_logger('content_analysis_with_requests')


def content_analysis_with_requests(target_url: str) -> ContentResultModel:
    content_result_model: ContentResultModel = ContentResultModel(processors="requests")
    try:
        session: requests.Session = requests.Session()
        logger.info("[*] Sayfa taranıyor")
        response = session.get(target_url, headers=config.HEADERS)
        content_result_model.http_status = response.status_code
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            page_title = "this page does not have title"
            if soup.find('title'):
                page_title = soup.find('title').text
            content_result_model.title = page_title
            content_result_model.content = soup.text
            content_result_model.raw_html = response.text
            scripts = soup.find_all("script")
            scripts = [script.string for script in scripts if script.string]
            content_result_model.api_requests, content_result_model.other_requests = api_endpoints_parser(scripts)

    except Exception as exception:
        logger.exception(exception, exc_info=True)
        content_result_model.has_err = True
    return content_result_model


if __name__ == '__main__':
    r = content_analysis_with_requests('https://farukseker.com.tr')
    print(r.api_requests)
    print(r.other_requests)

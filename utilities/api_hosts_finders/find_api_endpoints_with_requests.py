import re
import requests
from bs4 import BeautifulSoup
from custom_logger import get_logger
import config

logger = get_logger('find_api_endpoints_with_requests')


def find_api_endpoints_with_requests(target_url: str) -> set:
    session: requests.Session = requests.Session()
    logger.info("[*] Sayfa taranıyor, API endpointleri aranıyor...")
    response = session.get(target_url, headers=config.HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script")

    found_endpoints = set()
    for script in scripts:
        script_text = script.string
        if script_text:
            for pattern in config.API_PATTERNS:
                matches = re.findall(pattern, script_text)
                found_endpoints.update(matches)

    if found_endpoints:
        logger.info("[✔] Bulunan API Endpointleri:")
        for endpoint in found_endpoints:
            logger.info(f"   -> {endpoint}")
    else:
        logger.info("[✖] Sayfada açıkça görünen API endpointi bulunamadı.")

    return found_endpoints

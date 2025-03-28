import requests
from custom_logger import get_logger
import config

logger = get_logger("find_api_gateways")


def find_api_gateways(target_url) -> list[str]:
    session: requests.Session = requests.Session()
    gateway_list = []
    try:
        response = session.get(target_url, headers=config.HEADERS)
        headers = response.headers
        for gateway, keys in config.API_GATEWAYS.items():
            if any(key.lower() in headers for key in keys):
                gateway_list.append(gateway)
                logger.info(f"[✔] {gateway} API Gateway tespit edildi!")
    except Exception as e:
        logger.exception(f"[!] HTTP başlıklarını kontrol ederken hata oluştu: {e}")
    finally:
        return gateway_list

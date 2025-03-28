import config
import re


def api_endpoints_parser(pyload: list) -> (set, set):
    api_requests: set = set()
    other_requests: set = set()
    for lotion in pyload:
        for pattern in config.API_PATTERNS:
            if matches := re.findall(pattern, lotion):
                api_requests.update(matches)
            elif lotion.startswith('http'):
                other_requests.add(lotion)

    return api_requests, other_requests

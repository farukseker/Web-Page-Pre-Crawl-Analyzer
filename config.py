from pathlib import Path

from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options


BASE_DIR: Path = Path(__file__).resolve().parent
HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  "AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/120.0.0.0 Safari/537.36"
}

API_GATEWAYS: dict[str, list[str]] = {
    "Cloudflare": ["cf-ray", "server: cloudflare"],
    "AWS API Gateway": ["x-amzn-requestid", "x-amz-apigw-id"],
    "Google API Gateway": ["x-google-backend-request-id"],
    "Fastly": ["via", "x-served-by"],
    "Akamai": ["akamai-x-cache", "x-akamai-staging"]
}


def make_chrome_options() -> Options:
    ua = UserAgent()
    __chrome_options = Options()
    __chrome_options.add_argument(f"user-agent={ua.random}")
    __chrome_options.add_argument("--headless")
    __chrome_options.add_argument("--enable-logging")
    __chrome_options.add_argument("--log-level=0")
    __chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    __chrome_options.add_argument("--user-data-dir=C:\\Users\\seker\\AppData\\Local\\Temp\\selenium-profile")
    return __chrome_options


with open("script.js", 'r', encoding='utf-8') as script_file:
    ANTI_BOT_CLOAKER_SCRIPT = script_file.read()


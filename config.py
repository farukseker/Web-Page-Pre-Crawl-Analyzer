from pathlib import Path
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import os
import tempfile
from random import randrange


BASE_DIR: Path = Path(__file__).resolve().parent
TEMP_FOLDER: Path = Path(tempfile.gettempdir()).resolve() / 'WebSecurityAnalyzer'

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)


def remove_temp_dir() -> None:
    if os.path.exists(TEMP_FOLDER):
        os.remove(TEMP_FOLDER)


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

API_PATTERNS: list[str] = [
    r"https?://[a-zA-Z0-9.-]+/api/[a-zA-Z0-9/_-]*",
    r"https?://[a-zA-Z0-9.-]+/v[0-9]+/[a-zA-Z0-9/_-]*",
    r"https?://[a-zA-Z0-9.-]+/graphql",
    r"https?://[a-zA-Z0-9.-]+/wp-json/[a-zA-Z0-9/_-]*",
    r"https?://[a-zA-Z0-9.-]+/rest/[a-zA-Z0-9/_-]*"
]


def get_random_session_id():
    return ''.join([str(randrange(0, 9)) for _ in range(10)])


def make_chrome_options() -> Options:
    ua = UserAgent(platforms='desktop')
    __chrome_options = Options()
    __chrome_options.add_argument(f"user-agent={ua.chrome}")
    __chrome_options.add_argument("--disable-gpu")
    __chrome_options.add_argument("--headless")
    __chrome_options.add_argument("--no-sandbox")
    __chrome_options.add_argument("--enable-logging")
    __chrome_options.add_argument("--log-level=0")
    __chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    temp_dir = tempfile.mkdtemp()
    __chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    __chrome_options.add_argument("--window-size=1920,1080")
    # __chrome_options.add_argument("--user-data-dir=" + str(TEMP_FOLDER / f'selenium-profile_{get_random_session_id()}'))
    # __chrome_options.add_argument("--user-data-dir=C:\\Users\\seker\\AppData\\Local\\Temp\\selenium-profile")

    return __chrome_options


with open(BASE_DIR / "script.js", 'r', encoding='utf-8') as script_file:
    ANTI_BOT_CLOAKER_SCRIPT = script_file.read()


with open(BASE_DIR / '.previews/default.img', 'r') as dif:
    DEFAULT_PREVIEW_IMAGE = dif.read()

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')

with open(BASE_DIR / 'ai_prompt_templates/task.rulers', 'r') as dif:
    OLLAMA_RULES = dif.read()

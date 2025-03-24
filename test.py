import gzip

import requests
import time
from bs4 import BeautifulSoup
from models import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright, Playwright
import undetected_chromedriver
from fake_useragent import UserAgent
from custom_logger import get_logger
import re


logger = get_logger("web_page_analyzer")


class WebPageAnalyzer:
    def __init__(self, target_url: str):
        self.target_url = target_url

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        chrome_options.add_argument("--user-data-dir=C:\\Users\\seker\\AppData\\Local\\Temp\\selenium-profile")

        self.driver: webdriver.Chrome = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

        self.session: requests.Session = requests.Session()
        self.headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/120.0.0.0 Safari/537.36"
        }

        self.api_gateways: dict[str, list[str]] = {
            "Cloudflare": ["cf-ray", "server: cloudflare"],
            "AWS API Gateway": ["x-amzn-requestid", "x-amz-apigw-id"],
            "Google API Gateway": ["x-google-backend-request-id"],
            "Fastly": ["via", "x-served-by"],
            "Akamai": ["akamai-x-cache", "x-akamai-staging"]
        }

        self.undetected_chromedriver: undetected_chromedriver.Chrome = self.__load_undetected_chromedriver()

        self.result: dict = {
            "robots": {
                    "finder": None,
                    "content": None,
                    "status": True
            }
        }

    @staticmethod
    def get_random_user_agent():
        ua = UserAgent()
        return ua.random

    def __load_undetected_chromedriver(self) -> undetected_chromedriver.Chrome:
        options = Options()
        options.add_argument(f"user-agent={self.get_random_user_agent()}")
        options.add_argument("--disable-gpu")
        options.add_argument('headless')
        driver = undetected_chromedriver.Chrome(options=options, keep_alive=True)
        with open("script.js", 'r', encoding='utf-8') as script_file:
            script = script_file.read()
            driver.execute_script(script)
        time.sleep(.2)
        return driver

    def get_robots_txt_with_requests(self, url: str) -> RobotTxtResult:
        robot_txt_result: RobotTxtResult = RobotTxtResult(content='', http_status=0, has_err=False)
        response = self.session.get(url, headers=self.headers)
        try:
            if not response.status_code == 200:
                if response.headers.get('Content-Encoding') == 'gzip':
                    content = gzip.decompress(response.content)
                    robot_txt_result.content = content.decode(errors="ignore")
                else:
                    robot_txt_result.content = response.text if response.text.strip() else response.content.decode(
                        errors="ignore"
                    )
            else:
                robot_txt_result.content = response.text
            robot_txt_result.http_status = response.status_code
        except requests.RequestException as exception:
            logger.exception("Request failed: %s", exception)
            robot_txt_result.http_status = getattr(exception.response, 'status_code', 0)
            robot_txt_result.http_status = True
        except Exception as exception:
            logger.critical(exception)
            robot_txt_result.http_status = True
            # raise exception
        finally:
            return robot_txt_result

    def get_robots_txt_with_selenium(self, url: str) -> RobotTxtResult:
        robot_txt_result: RobotTxtResult = RobotTxtResult(content='', http_status=0, has_err=False)
        try:
            self.driver.get(url)
            content = self.driver.page_source
            if len(content) > 1:
                soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
                robot_txt_result.content = soup.text
                robot_txt_result.http_status = 200
        except Exception as exception:
            logger.critical(exception)
            robot_txt_result.http_status = True
            # raise exception
        return robot_txt_result

    @staticmethod
    def get_robots_txt_with_playwright(playwright: Playwright, url: str) -> RobotTxtResult:
        robot_txt_result: RobotTxtResult = RobotTxtResult(content='', http_status=0, has_err=False)

        chromium = playwright.chromium  # "firefox" || "webkit".
        browser = chromium.launch()
        try:
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            if len(content) > 1:
                soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
                robot_txt_result.content = soup.text
                robot_txt_result.http_status = 200
        except Exception as exception:
            logger.critical(exception)
            robot_txt_result.http_status = True
        finally:
            browser.close()
            return robot_txt_result

    def get_robots_txt_with_undetected_chromedriver(self, url: str) -> RobotTxtResult:
        robot_txt_result: RobotTxtResult = RobotTxtResult(content='', http_status=0, has_err=False)
        try:
            self.undetected_chromedriver.get(url)
            content = self.undetected_chromedriver.page_source
            if len(content) > 1:
                soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
                robot_txt_result.http_status = 200
                robot_txt_result.content = soup.text
            else:
                robot_txt_result.content = content
                robot_txt_result.has_err = True
        except Exception as exception:
            logger.critical(exception)
            robot_txt_result.http_status = True
        finally:
            return robot_txt_result

    def check_robots_txt(self) -> None:
        robots_url = self.target_url + "/robots.txt"
        self.result["robots"]["status"]: bool = False
        try:
            logger.info("[✔] robots.txt bulundu:")

            requests_robots_txt = self.get_robots_txt_with_requests(robots_url)
            print(f'dönen : {requests_robots_txt}')
            selenium_robots_txt = self.get_robots_txt_with_selenium(robots_url)
            with sync_playwright() as playwright:
                playwright_robots_txt = self.get_robots_txt_with_playwright(playwright, robots_url)
            undetected_chromedriver_robots_txt = self.get_robots_txt_with_undetected_chromedriver(robots_url)

            a = [
                {
                    "module": "requests",
                    "is_load": "",
                }
            ]

        except Exception as e:
            logger.exception(f"[!] robots.txt kontrolü başarısız: {e}")
            print(f"[!] robots.txt kontrolü başarısız: {e}")

    def check_http_headers(self):
        """API gateway ve güvenlik servislerini HTTP başlıklarından tespit eder"""
        print("[*] HTTP başlıkları kontrol ediliyor...")
        try:
            response = self.session.get(self.target_url, headers=self.headers)
            headers = response.headers

            for gateway, keys in self.api_gateways.items():
                if any(key.lower() in headers for key in keys):
                    print(f"[✔] {gateway} API Gateway tespit edildi!")

        except Exception as e:
            print(f"[!] HTTP başlıklarını kontrol ederken hata oluştu: {e}")


web_page_analyzer: WebPageAnalyzer = WebPageAnalyzer("https://farukseker.com.tr/")
# print(web_page_analyzer.get_robots_txt_with_requests("https://farukseker.com.tr/robots.txt"))
web_page_analyzer.check_robots_txt()
# web_page_analyzer.check_http_headers()

print(web_page_analyzer.result)

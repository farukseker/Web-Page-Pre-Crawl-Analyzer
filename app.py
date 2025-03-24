import streamlit as st
import undetected_chromedriver
from selenium import webdriver

import config
from utilities.robots import (
    get_robots_txt_with_requests,
    get_robots_txt_with_selenium,
    get_robots_txt_with_playwright,
    get_robots_txt_with_undetected_chromedriver
)
from urllib.parse import urlparse
import asyncio


def main():
    st.set_page_config(page_title="Web Page Analyzer", layout="wide")
    st.title("Web Page Analyzer")

    with st.spinner("Drivers loading"):
        try:
            uc_driver: undetected_chromedriver = undetected_chromedriver.Chrome(options=config.make_chrome_options(),
                                                                                keep_alive=True)
            uc_driver.execute_script(config.ANTI_BOT_CLOAKER_SCRIPT)
            chrome_driver: webdriver.Chrome = webdriver.Chrome(options=config.make_chrome_options())
        except Exception as e:
            st.error(f"Driverlerin yüklenmesi sırasında hata: {e}")

    url = st.text_input("Analiz etmek istediğiniz URL'yi girin:", value='https://farukseker.com.tr/')
    url_obj = urlparse(url)

    if st.button("Analiz Et") and url:

        with st.spinner("Analiz ediliyor..."):
            try:
                st.subheader("Robots.txt Sonucu")

                robots_url = f'{url_obj.scheme}://{url_obj.netloc}/robots.txt'
                st.text(f'> Target: {robots_url}')

                requests_col, selenium_col, playwright_col, undetected_chromedriver_col = st.columns(4)

                requests_result = get_robots_txt_with_requests(robots_url)
                requests_col.subheader('Requests Result')
                requests_col.code(f"HTTP STATUS: {requests_result.http_status}")
                requests_col.code(f"ERROR: {requests_result.has_err}")
                requests_col.code(requests_result.content)

                selenium_result = get_robots_txt_with_selenium(robots_url, chrome_driver)
                selenium_col.subheader('Selenium Result')
                selenium_col.code(f"HTTP STATUS: {selenium_result.http_status}")
                selenium_col.code(f"ERROR: {selenium_result.has_err}")
                selenium_col.code(selenium_result.content)

                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                playwright_result = loop.run_until_complete(get_robots_txt_with_playwright(robots_url))

                playwright_col.subheader('Playwright Result')
                playwright_col.code(f"HTTP STATUS: {playwright_result.http_status}")
                playwright_col.code(f"ERROR: {playwright_result.has_err}")
                playwright_col.code(playwright_result.content)

                undetected_chromedriver_result = get_robots_txt_with_undetected_chromedriver(robots_url, uc_driver)
                undetected_chromedriver_col.subheader('Undetected Chromedriver Result')
                undetected_chromedriver_col.code(f"HTTP STATUS: {undetected_chromedriver_result.http_status}")
                undetected_chromedriver_col.code(f"ERROR: {undetected_chromedriver_result.has_err}")
                undetected_chromedriver_col.code(undetected_chromedriver_result.content)

            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")


if __name__ == "__main__":
    main()

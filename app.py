import streamlit as st
import undetected_chromedriver
from selenium import webdriver
import time
import config
from utilities.robots import (
    get_robots_txt_with_requests,
    get_robots_txt_with_selenium,
    get_robots_txt_with_playwright,
    get_robots_txt_with_undetected_chromedriver
)

from utilities.content_analysis import (
    content_analysis_with_requests,
    content_analysis_with_selenium,
    content_analysis_with_playwright,
    content_analysis_with_undetected_chromedriver
)

from utilities import find_api_gateways
from urllib.parse import urlparse
import asyncio
from ai_agent import LocalLLM


llm = LocalLLM()
llm_list = llm.list_llm()

do_task = False

def main():
    global do_task
    st.set_page_config(page_title="Web Page Analyzer", layout="wide")
    st.title("Web Page Analyzer")

    col1, col2, = st.columns([1, 2])

    selected_model = col1.selectbox("Select llm model for analiz and chat", llm_list)
    llm.selected_model = selected_model

    url = col2.text_input("Analiz etmek istediğiniz URL'yi girin:", value='https://farukseker.com.tr/')
    url_obj = urlparse(url)
    st.session_state.content_is_load = False

    if st.button("Analiz Et"):
        do_task = True

    if do_task and url:
        print("task")
        st.session_state.content_is_load = False
        st.session_state.analyzed = False
        st.session_state.messages.clear()

        with st.spinner("Analiz ediliyor..."):
            try:
                st.subheader("Robots.txt Sonucu")

                robots_url = f'{url_obj.scheme}://{url_obj.netloc}/robots.txt'
                st.markdown(f'> Robots.txt url >> [{robots_url}]({robots_url})')

                requests_col, selenium_col, playwright_col, undetected_chromedriver_col = st.columns(4)

                requests_result = get_robots_txt_with_requests(robots_url)
                requests_col.subheader('Requests Result')
                requests_col.code(f"HTTP STATUS: {requests_result.http_status}")
                requests_col.code(f"ERROR: {requests_result.has_err}")
                requests_col.code(requests_result.content)
                time.sleep(1)

                selenium_result = get_robots_txt_with_selenium(robots_url)
                selenium_col.subheader('Selenium Result')
                selenium_col.code(f"HTTP STATUS: {selenium_result.http_status}")
                selenium_col.code(f"ERROR: {selenium_result.has_err}")
                selenium_col.code(selenium_result.content)
                time.sleep(1)

                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
                playwright_result = loop.run_until_complete(get_robots_txt_with_playwright(robots_url))

                playwright_col.subheader('Playwright Result')
                playwright_col.code(f"HTTP STATUS: {playwright_result.http_status}")
                playwright_col.code(f"ERROR: {playwright_result.has_err}")
                playwright_col.code(playwright_result.content)
                time.sleep(1)

                undetected_chromedriver_result = get_robots_txt_with_undetected_chromedriver(robots_url)
                undetected_chromedriver_col.subheader('Undetected Chromedriver Result')
                undetected_chromedriver_col.code(f"HTTP STATUS: {undetected_chromedriver_result.http_status}")
                undetected_chromedriver_col.code(f"ERROR: {undetected_chromedriver_result.has_err}")
                undetected_chromedriver_col.code(undetected_chromedriver_result.content)
                time.sleep(1)

                # ROBOTS END

            except Exception as e:
                st.error(f"Analiz sırasında bir hata oluştu: {e}")
        st.subheader(f'API Gateways:')
        with st.spinner('Searching API Gateways'):
            if api_gateways_results := find_api_gateways(url):
                tags_html = ''.join(
                    [
                        '<span style="background-color: rgb(9 12 18); padding: 5px 10px; border-radius: 10px;">'
                        f'{api_gateway}'
                        '</span>'
                        for api_gateway in api_gateways_results
                    ]
                )
                st.markdown(
                    f"""
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        {tags_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error('API Gateways Not Found')

        st.subheader('Content Load Tests')

        requests_col, selenium_col, playwright_col, undetected_chromedriver_col = st.columns(4)

        with st.spinner('Waiting for Requests :'):
            content_analysis_with_requests_result = content_analysis_with_requests(target_url=url)
            requests_col.subheader('Requests')
            requests_col.text(f'Page Title: {content_analysis_with_requests_result.title}')
            r1, r2 = requests_col.columns(2)
            r1.code(f'Status: {content_analysis_with_requests_result.http_status}')
            r2.code(f'leng: {len(content_analysis_with_requests_result.content)}')
            requests_col.text('preview img')
            requests_col.image(content_analysis_with_requests_result.page_preview_path)
            time.sleep(1)

        with st.spinner('Waiting for Selenium :'):
            content_analysis_with_selenium_result = content_analysis_with_selenium(target_url=url)
            selenium_col.subheader('Selenium')
            selenium_col.text(f'Page Title: {content_analysis_with_selenium_result.title}')
            r1, r2 = selenium_col.columns(2)
            r1.code(f'Status: {content_analysis_with_selenium_result.http_status}')
            r2.code(f'leng: {len(content_analysis_with_selenium_result.content)}')
            selenium_col.text('preview img')
            selenium_col.image(content_analysis_with_selenium_result.page_preview_path)
            time.sleep(1)

        with st.spinner('Waiting for Playwright :'):
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            content_analysis_with_playwright_result = loop.run_until_complete(content_analysis_with_playwright(url))

            playwright_col.subheader('Playwright')
            playwright_col.text(f'Page Title: {content_analysis_with_playwright_result.title}')
            r1, r2 = playwright_col.columns(2)
            r1.code(f'Status: {content_analysis_with_playwright_result.http_status}')
            r2.code(f'leng: {len(content_analysis_with_playwright_result.content)}')
            playwright_col.text('preview img')
            playwright_col.image(content_analysis_with_playwright_result.page_preview_path)

        with st.spinner('Waiting for Undetected Chromedriver :'):
            content_analysis_with_undetected_chromedriver_result = content_analysis_with_undetected_chromedriver(url)
            undetected_chromedriver_col.subheader('Undetected Chromedriver')
            undetected_chromedriver_col.text(f'Page Title: {content_analysis_with_undetected_chromedriver_result.title}')
            r1, r2 = undetected_chromedriver_col.columns(2)
            r1.code(f'Status: {content_analysis_with_undetected_chromedriver_result.http_status}')
            r2.code(f'leng: {len(content_analysis_with_undetected_chromedriver_result.content)}')
            undetected_chromedriver_col.text('preview img')
            undetected_chromedriver_col.image(content_analysis_with_undetected_chromedriver_result.page_preview_path)

        st.session_state.content_is_load = True

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not st.session_state.analyzed and st.session_state.content_is_load:
        with st.spinner(f"{selected_model}'is thinking"):
            try:
                for context in [
                    {
                        "message": "Can u analize Requests module content: ",
                        "content": content_analysis_with_requests_result.content
                    },
                    {
                        "message": "Can u analize Requests module Selenium: ",
                        "content": content_analysis_with_selenium_result.content
                    },
                    {
                        "message": "Can u analize Requests module Playwright: ",
                        "content": content_analysis_with_playwright_result.content
                    },
                    {
                        "message": "Can u analize Requests module Undetected Chromedriver: ",
                        "content": content_analysis_with_undetected_chromedriver_result.content
                    }
                ]:
                    with st.chat_message('user'):
                        st.markdown(context.get('message'))
                        llm.save_user_message(f'{context.get('message')} content : {context.get('content')}:')

                    st.session_state.messages.append({
                        "role": "user",
                        "content": context.get('message')
                    })

                    response = llm.analyze_web_page_content(context.get('content'))
                    response = response.model_dump()

                    markdown_answer: str = f"""
                    {response.pop('ai_comment')}
                    ```json
                    {response}
                    ```
                    """
                    with st.chat_message('assistant'):
                        st.markdown(markdown_answer)
                        llm.save_llm_message(markdown_answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": markdown_answer
                    })

                with st.chat_message('System'):
                    message = f'''
                    In my previous 4 proms, I send you the html content of a web page and you will help the user
                    based on this content, while showing analysis and examples,
                    the domain name web style you will take as a basis '{url}' '''
                    st.markdown(message)
                    # llm.save_user_message(message)
                    response_placeholder = st.empty()
                    r = llm.chat_with_llm(message, response_placeholder)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": r
                    })

                st.session_state.analyzed = True
            except Exception as e:
                print('LLM ERROR: ')
                print(e)

    user_input = st.chat_input("Mesajınızı yazın...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        response_placeholder = st.empty()

        bot_reply = llm.chat_with_llm(user_input, response_placeholder)

        # response = llm.chain.invoke({'content': user_input})
        # bot_reply = response.model_dump_json()

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        # with st.chat_message("assistant"):
        #     st.markdown(bot_reply)
        # response_placeholder.empty()
    # for _ in llm.chat_history:
    #     print(_)


if __name__ == "__main__":
    main()

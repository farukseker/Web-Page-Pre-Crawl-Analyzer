import streamlit as st
import time
import config
import atexit
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
import sys

if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()  # Windows için
    asyncio.set_event_loop(loop)
else:
    loop = asyncio.new_event_loop()  # Linux/macOS için
    asyncio.set_event_loop(loop)


selected_tools: list = []
selected_tasks: list = []
all_colons: list[st.columns] = []


def clear_results() -> None:
    global all_colons
    for col in all_colons:
        col.empty()
    all_colons.clear()


def cleanup():
    config.remove_temp_dir()


atexit.register(cleanup)

default_values = {
    "robots": {},
    "api_gateways": [],
    "content_load_test": {},
    "messages": [],
    "selected_url": '',
    "analyzed": False,
    "content_is_load": False,
    "start_analyze": False,
    "wt_chat": False,
    "overload_test_url_list": set(),
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


llm = LocalLLM()
llm_list = llm.list_llm()

if "chat_room_id" not in st.session_state:
    st.session_state.chat_room_id = llm.create_chat_room()
    llm.chat_room_id = st.session_state.chat_room_id
    llm.load_chat_history()

llm.chat_room_id = st.session_state.chat_room_id
llm.load_chat_history()


def show_robots_result():
    global loop, selected_tools, all_colons
    if not st.session_state.robots:
        return

    requests_result, selenium_result, playwright_result, undetected_chromedriver_result = (
        st.session_state.robots.get('requests_result'),
        st.session_state.robots.get('selenium_result'),
        st.session_state.robots.get('undetected_chromedriver_result'),
        st.session_state.robots.get('playwright_result')
    )

    if any([requests_result, selenium_result, playwright_result, undetected_chromedriver_result]):
        st.subheader("Robots.txt Sonucu")
        for tool, col in zip(selected_tools, st.columns(len(selected_tools))):
            all_colons.append(col)
            match tool:
                case 'requests':
                    col.subheader('Requests Result')
                    col.code(f"HTTP STATUS: {requests_result.http_status}")
                    col.code(f"ERROR: {requests_result.has_err}")
                    col.code(requests_result.content)
                case 'selenium':
                    col.subheader('Selenium Result')
                    col.code(f"HTTP STATUS: {selenium_result.http_status}")
                    col.code(f"ERROR: {selenium_result.has_err}")
                    col.code(selenium_result.content)
                case 'playwright':
                    col.subheader('Playwright Result')
                    col.code(f"HTTP STATUS: {playwright_result.http_status}")
                    col.code(f"ERROR: {playwright_result.has_err}")
                    col.code(playwright_result.content)
                case 'undetected_chromedriver':
                    col.subheader('Undetected Chromedriver Result')
                    col.code(f"HTTP STATUS: {undetected_chromedriver_result.http_status}")
                    col.code(f"ERROR: {undetected_chromedriver_result.has_err}")
                    col.code(undetected_chromedriver_result.content)
                case _:
                    ...


def show_api_gateways_result():
    global all_colons
    if "api_gateways" in st.session_state and len(st.session_state.api_gateways) > 0:
        st.subheader(f'API Gateways:')
        tags_html = ''.join(
            [
                '<span style="background-color: rgb(9 12 18); padding: 5px 10px; border-radius: 10px;">'
                f'{api_gateway}'
                '</span>'
                for api_gateway in st.session_state.api_gateways
            ]
        )
        api_gateway_result_col = st.markdown(
            f"""
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                {tags_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        all_colons.append(api_gateway_result_col)
    else:
        if st.session_state.content_is_load:
            st.error('API Gateways Not Found')
    st.text(' ')


def show_content_load_test_results():
    global loop, selected_tools, all_colons
    if not st.session_state.content_load_test:
        return
    requests_result, selenium_result, playwright_result, undetected_chromedriver_result = (
        st.session_state.content_load_test.get('requests_result'),
        st.session_state.content_load_test.get('selenium_result'),
        st.session_state.content_load_test.get('playwright_result'),
        st.session_state.content_load_test.get('undetected_chromedriver_result'),
    )
    if any([requests_result, selenium_result, playwright_result, undetected_chromedriver_result]):
        st.subheader('Content Load Tests')
        for tool, col in zip(selected_tools, st.columns(len(selected_tools))):
            all_colons.append(col)
            match tool:
                case 'requests':
                    col.subheader('Requests')
                    col.text(f'Page Title: {requests_result.title}')
                    r1, r2 = col.columns(2)
                    r1.code(f'Status: {requests_result.http_status}')
                    r2.code(f'content length: {len(requests_result.content)}')
                    col.text('preview img')
                    col.image(requests_result.page_preview_path)
                case 'selenium':
                    col.subheader('Selenium')
                    col.text(f'Page Title: {selenium_result.title}')
                    r1, r2 = col.columns(2)
                    r1.code(f'Status: {selenium_result.http_status}')
                    r2.code(f'content length: {len(selenium_result.content)}')
                    col.text('preview img')
                    col.image(selenium_result.page_preview_path)
                case 'playwright':
                    col.subheader('Playwright')
                    col.text(f'Page Title: {playwright_result.title}')
                    r1, r2 = col.columns(2)
                    r1.code(f'Status: {playwright_result.http_status}')
                    r2.code(f'content length: {len(playwright_result.content)}')
                    col.text('preview img')
                    col.image(playwright_result.page_preview_path)
                case 'undetected_chromedriver':
                    col.subheader('Undetected Chromedriver')
                    col.text(f'Page Title: {undetected_chromedriver_result.title}')
                    r1, r2 = col.columns(2)
                    r1.code(f'Status: {undetected_chromedriver_result.http_status}')
                    r2.code(f'content length: {len(undetected_chromedriver_result.content)}')
                    col.text('preview img')
                    col.image(undetected_chromedriver_result.page_preview_path)


def show_api_gateway_list():
    global loop, selected_tools
    if not st.session_state.content_load_test and not len(selected_tools) > 0:
        return

    api_set_list: set = set()
    other_set_list: set = set()

    for selected_tool in selected_tools:
        if (state := st.session_state.content_load_test.get(f'{selected_tool}_result')) and any([state.api_requests, state.other_requests]):

            api_set_list.update(state.api_requests)
            other_set_list.update(state.other_requests)

    st.session_state.overload_test_url_list.update(api_set_list)
    st.session_state.overload_test_url_list.update(other_set_list)

    st.subheader('API')
    st.table([{'host': urlparse(api).hostname, 'path': urlparse(api).path} for api in api_set_list if urlparse(api)])

    st.subheader('Other Url')
    st.table([{'host': urlparse(other).hostname, 'path': urlparse(other).path[:30]} for other in other_set_list if urlparse(other)])


def main():
    global loop, selected_tools, selected_tasks
    TASK_ROBOT_TXT: str = 'Get Robots.txt'
    TASK_API_GATEWAYS_TXT: str = 'Find API Gateways'
    TASK_CONTENT_LOAD_TXT: str = 'Full By Content Load Test With LLM'
    # st.set_page_config(page_title="Web Page Analyzer", layout="wide")
    st.set_page_config(
        page_title="Web Page Analyzer",
        layout='wide',
    )
    st.title("Web Page Analyzer")

    st.text('Test sites')
    if st.button('CreepJS'):
        st.session_state.selected_url = 'https://abrahamjuliot.github.io/creepjs/'

    if st.button('Bot.sannysoft.com'):
        st.session_state.selected_url = 'https://bot.sannysoft.com/'

    url = st.text_input("Analiz etmek istediğiniz URL'yi girin:", value=st.session_state.selected_url)
    url_obj = urlparse(url)

    tool_col, task_col = st.columns(2)

    selected_tools = tool_col.multiselect(
        label='Tools',
        options=(
            'requests',
            'selenium',
            'playwright',
            'undetected_chromedriver',
        ),
        default='requests'
    )

    if len(selected_tools) > 0:
        selected_tasks = task_col.multiselect(
            label='Tasks',
            options=(
                TASK_ROBOT_TXT,
                TASK_API_GATEWAYS_TXT,
                TASK_CONTENT_LOAD_TXT,
            )
        )

    if not st.session_state.start_analyze and not st.session_state.content_is_load:
        btn_place_holder = st.empty()

        if btn_place_holder.button("Analiz Et"):
            st.session_state.start_analyze = True
            st.session_state.robots = {}
            st.session_state.api_gateways = []
            st.session_state.content_load_test = {}
            st.session_state.messages.clear()
            st.session_state.content_is_load = False
            st.session_state.analyzed = False
            btn_place_holder.empty()

    if st.session_state.start_analyze and not st.session_state.content_is_load and url:
        st.session_state.content_is_load = True
        clear_results()
        if TASK_ROBOT_TXT in selected_tasks:
            with st.spinner("Robots.txt Sonucu Bekleniyor..."):
                try:
                    robots_url = f'{url_obj.scheme}://{url_obj.netloc}/robots.txt'
                    for selected_tool in selected_tools:
                        match selected_tool:
                            case 'requests':
                                requests_result = get_robots_txt_with_requests(robots_url)
                                st.session_state.robots.__setitem__(
                                    "requests_result",
                                    requests_result
                                )
                                time.sleep(1)
                            case 'selenium':
                                selenium_result = get_robots_txt_with_selenium(robots_url)
                                st.session_state.robots.__setitem__(
                                    "selenium_result",
                                    selenium_result
                                )
                                time.sleep(1)
                            case 'playwright':
                                undetected_chromedriver_result = get_robots_txt_with_undetected_chromedriver(robots_url)
                                st.session_state.robots.__setitem__(
                                    "undetected_chromedriver_result",
                                    undetected_chromedriver_result
                                )
                                time.sleep(1)
                            case 'undetected_chromedriver':
                                playwright_result = loop.run_until_complete(get_robots_txt_with_playwright(robots_url))
                                st.session_state.robots.__setitem__(
                                    "playwright_result",
                                    playwright_result
                                )
                            case _:
                                ...
                    # show_robots_result()
                    # ROBOTS END

                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")

        if TASK_API_GATEWAYS_TXT in selected_tasks:
            with st.spinner('Searching API Gateways'):
                st.session_state.api_gateways = find_api_gateways(url)
        if TASK_CONTENT_LOAD_TXT in selected_tasks:
            for selected_tool in selected_tools:
                match selected_tool:
                    case 'requests':
                        with st.spinner('Waiting for Requests :'):
                            st.session_state.content_load_test.__setitem__(
                                "requests_result",
                                content_analysis_with_requests(target_url=url)
                            )
                    case 'selenium':
                        with st.spinner('Waiting for Selenium :'):
                            st.session_state.content_load_test.__setitem__(
                                "selenium_result",
                                content_analysis_with_selenium(target_url=url)
                            )
                    case 'playwright':
                        with st.spinner('Waiting for Playwright :'):
                            st.session_state.content_load_test.__setitem__(
                                "playwright_result",
                                loop.run_until_complete(content_analysis_with_playwright(url))
                            )
                            time.sleep(1)
                    case 'undetected_chromedriver':
                        with st.spinner('Waiting for Undetected Chromedriver :'):
                            st.session_state.content_load_test.__setitem__(
                                "undetected_chromedriver_result",
                                content_analysis_with_undetected_chromedriver(url)
                            )
                    case _:
                        ...
                time.sleep(1)

    if st.session_state.content_load_test:
        if TASK_ROBOT_TXT in selected_tasks:
            show_robots_result()
        if TASK_API_GATEWAYS_TXT in selected_tasks:
            show_api_gateway_list()
        if TASK_CONTENT_LOAD_TXT in selected_tasks:
            show_content_load_test_results()
            show_api_gateways_result()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.content_is_load and TASK_CONTENT_LOAD_TXT in selected_tasks:
        col1, col2 = st.columns([1, 3])
        selected_model = col1.selectbox("Select llm model for analiz and chat", llm_list)
        llm.selected_model = selected_model

    if not st.session_state.wt_chat and st.session_state.content_is_load and TASK_CONTENT_LOAD_TXT in selected_tasks:
        if st.button('What Think Chat'):
            st.session_state.wt_chat = True

    if st.session_state.wt_chat and not st.session_state.analyzed and st.session_state.content_is_load:
        st.session_state.analyzed = True
        with st.spinner(f"{llm.selected_model}'is thinking"):
            try:
                pre_message = 'analyze content taken by {module}'
                pre_prompt: str = """
                MAKE SURE TO KEEP YOUR ANSWERS SHORT:
                Look at this message, I will add the HTML document of your website in curly brackets at the end of this message, analyze this content
                and tell me if the content is blocked by a waf or a bot protection, also try to understand the technologies it uses, we need this
                then here is the content for you and MAKE SURE TO KEEP YOUR ANSWERS SHORT, MAKE SURE TO KEEP YOUR ANSWERS SHORT
                {test_module}
                {content}
                """.replace('\n', '')

                for selected_tool in selected_tools:
                    state = st.session_state.content_load_test.get(f'{selected_tool}_result')

                    with st.chat_message('user'):
                        st.markdown(pre_message.format(module=state.processors))
                        llm.save_user_message(
                            pre_prompt.format(
                                test_module=f'{state.processors} module content: ',
                                content=state.content
                            )
                        )

                    st.session_state.messages.append({
                        "role": "user",
                        "content": pre_message.format(module=state.processors)
                    })

                    with st.chat_message('assistant'):
                        response_placeholder = st.empty()
                        response = llm.chat_with_llm(
                            pre_prompt.format(
                                test_module=f'{state.processors} module content: ',
                                content=state.content
                            ),
                            response_placeholder
                        )
                        time.sleep(.25)
                        llm.save_llm_message(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                with st.chat_message('system'):
                    message = f'''
                    In my previous 4 proms, I send you the html content of a web page and you will help the user
                    based on this content, while showing analysis and examples,
                    the domain name web style you will take as a basis '{url}' '''
                    st.markdown(message)
                    # llm.save_user_message(message)
                    response_placeholder = st.empty()
                    r = llm.chat_with_llm(message.replace('\n', ''), response_placeholder)
                    st.session_state.messages.append({
                        "role": "ai",
                        "content": r
                    })

            except Exception as e:
                print('LLM ERROR: ')
                print(e)

    if st.session_state.wt_chat and st.session_state.analyzed:
        user_input = st.chat_input("Mesajınızı yazın...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message('assistant'):
                response_placeholder = st.empty()
                response = llm.chat_with_llm(user_input, response_placeholder)
                time.sleep(.25)
                llm.save_llm_message(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()

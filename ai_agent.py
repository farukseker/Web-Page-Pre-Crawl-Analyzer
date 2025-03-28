import json
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama.llms import OllamaLLM
from langchain_ollama.chat_models import Client
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from pydantic import BaseModel
import config


class ContentAnalysis(BaseModel):
    is_stuck_waf: bool
    content_is_readable: bool
    extractable_format: str  # Should be one of "json", "csv", or "none"
    ai_comment: str


class LocalLLM:

    def __init__(self):
        self.parser: PydanticOutputParser = PydanticOutputParser(pydantic_object=ContentAnalysis)
        self.__selected_template: Path | str | None = config.BASE_DIR / 'ai_prompt_templates/content_analysis.prompt'
        self.__selected_model: str | None = None
        # self.ollm = self.do_ollama_llm()
        self.__chat_session_deque = self.load_chat_history()
        self.chat_bot: ChatOllama | None = None
        self.conversation = None

    def start_conversation(self):
        self.conversation = RunnableWithMessageHistory(self.chat_bot, lambda session_id: self.__chat_session_deque)

    def load_llm_chat(self):
        self.chat_bot = ChatOllama(model=self.__selected_model, base_url=config.OLLAMA_BASE_URL)

    @property
    def _prompt_template_text(self) -> str:
        with open(self.__selected_template, 'r', encoding='utf-8') as df:
            return df.read()

    @property
    def load_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(template=self._prompt_template_text, input_variables=['content'])

    @property
    def client(self) -> Client:
        try:
            return Client(host=config.OLLAMA_BASE_URL)
        except Exception as exception:
            print(exception)

    def list_llm(self) -> list | None:
        try:
            model_list = self.client.list()
            return [n.model for n in [model[1] for model in model_list][0]]
        except Exception as e:
            # logger.error('llm listing', str(e))
            return []

    @property
    def selected_model(self) -> str:
        return self.__selected_model

    @selected_model.setter
    def selected_model(self, _llm: str):
        if _llm in self.list_llm():
            self.__selected_model = _llm
            self.load_llm_chat()
            self.start_conversation()
        else:
            # logger.error("The selected llm model is does not in LocalLLM's list")
            raise ValueError("The selected llm model is does not in LocalLLM's list")

    @property
    def chain(self):
        if self.__selected_model is None:
            # logger.error('The selected_model is does not None')
            raise ValueError('The selected_model is does not None')

        return self.load_prompt_template | OllamaLLM(client=self.client, model=self.selected_model, base_url=config.OLLAMA_BASE_URL) | self.parser

    def analyze_web_page_content(self, content_text) -> ContentAnalysis | None:
        try:
            return self.chain.invoke({'content': content_text})
        except Exception as e:
            print("ERROR LINE: ")
            print(e)
            # logger.error(e)
            return None
            # raise e

    @staticmethod
    def load_chat_history():
        """Önceki konuşmaları JSON'dan yükler"""
        if config.HISTORY_FILE.exists():
            with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                history = ChatMessageHistory()
                for msg in data:
                    if msg["role"] == "human":
                        history.add_user_message(msg["content"])
                    else:
                        history.add_ai_message(msg["content"])
                return history
        return ChatMessageHistory()

    def save_chat_history(self):
        """Mevcut konuşmaları JSON dosyasına kaydeder"""
        messages = []
        for msg in self.__chat_session_deque.messages:
            messages.append({"role": "human" if isinstance(msg, HumanMessage) else "ai", "content": msg.content})

        with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

    def save_llm_message(self, message: str) -> None:
        self.__chat_session_deque.add_ai_message(message)
        self.save_chat_history()

    def save_user_message(self, message: str) -> None:
        self.__chat_session_deque.add_user_message(message)
        self.save_chat_history()

    @property
    def chat_history(self) -> ChatMessageHistory:
        return self.__chat_session_deque

    def chat_with_llm(self, chat_message: str, st: None = None) -> str:
        chat_conf: dict = {
            "configurable": {
                "session_id": "scraper_user_alpha"
                }
            }

        # if not self.conversation:
        #     raise NotImplementedError('first start conversation')

        self.save_user_message(chat_message)

        if st:
            response_placeholder = st.empty()
            model_reply = ""

            for chunk in self.conversation.stream(
                    chat_message,
                    config=chat_conf
            ):
                model_reply += chunk.content
                response_placeholder.write(model_reply)
        else:
            response = self.conversation.invoke(
                chat_message,
                config=chat_conf
            )
            model_reply = response.content
        self.save_llm_message(model_reply)
        return model_reply


if __name__ == '__main__':
    llm = LocalLLM()
    llm_list = llm.list_llm()
    for k, v in enumerate(llm_list):
        print(f'{k}. {v}')

    # selected_llm_index: int = int(input('Select a llm model: '))
    # llm.selected_model = llm_list[selected_llm_index]
    llm.selected_model = llm_list[1]

    r = llm.chat_with_llm("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s")
    print(r)
    # r = llm.analyze_web_page_content(
    #     """
    #     <title>Cloudflare Web Application Firewall (WAF)</title>
    #
    #     <p color="red">
    #     403 Forbidden – Access Denied
    #
    #     Cloudflare WAF has blocked your access request for security reasons. This may be due to suspicious behavior or a violation of application security rules.
    #
    #     Reason:
    #
    #     - A suspicious IP address or network scan was detected.
    #
    #     - A request from a malicious traffic source was detected.
    #
    #     - Invalid or dangerous URL parameters were used.
    #
    #     If this is blocking your access and you normally need to access this page, please contact your system administrator or contact Cloudflare to request support.
    #     </p>
    #     """
    # )
    #
    # print(r)
    #
    # if r:
    #     # Convert Pydantic model to a dictionary using model_dump
    #     result_dict = r.model_dump()
    #
    #     # Convert the dictionary to a JSON string
    #     result_json = json.dumps(result_dict, indent=2)
    #
    #     llm.save_llm_message(result_json)
    #
    #     # Print or return the JSON
    #     print(result_json)
    #
    #     # prmt = input('promot: ')
    #     prmt = 'googd job bro, can u do example scraper code for this web page'
    #     p = llm.chat_with_llm(prmt)
    #     print(p)
    #
    # else:
    #     print("Error: No result from analysis")
    # '''
    # ```json
    # {
    #   "is_stuck_waf": true | false,
    #   "content_is_readable": true | false,
    #   "extractable_format": "json" | "csv" | "table" | "none",
    #   "ai_comment": "..."
    # }
    # '''

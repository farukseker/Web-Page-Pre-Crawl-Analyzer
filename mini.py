import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
from collections import deque

# Ollama modelini başlat
llm = ChatOllama(model="mistral")  # Model adını kendi sistemine göre değiştir

# Mesaj geçmişini tutmak için
chat_history = deque()


def stream_chat_response(user_message):
    """LLM ile stream modunda sohbet gerçekleştirir."""
    chat_history.append(HumanMessage(content=user_message))  # Kullanıcı mesajını kaydet

    messages = [
        {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
        for msg in chat_history
    ]

    response_placeholder = st.empty()  # Stream için boş bir alan oluştur
    full_response = ""

    # Ollama'dan yanıtları stream modunda al
    for chunk in llm.stream(messages):
        full_response += chunk.content  # HATA BURADAYDI: chunk["message"] yerine chunk.content
        response_placeholder.write(full_response)  # Gelen kısmı ekrana yaz

    chat_history.append(AIMessage(content=full_response))  # Yanıtı kaydet


# **Streamlit Arayüzü**
st.title("Chatbot (Streamlit + Ollama)")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Geçmiş mesajları ekrana yazdır
for msg in st.session_state.chat_history:
    role = "👤 You" if isinstance(msg, HumanMessage) else "🤖 AI"
    st.markdown(f"**{role}:** {msg.content}")

# Kullanıcıdan mesaj al
user_input = st.text_input("Enter your message:")

if st.button("Send") and user_input:
    stream_chat_response(user_input)
    st.session_state.chat_history = chat_history  # Güncellenmiş geçmişi sakla

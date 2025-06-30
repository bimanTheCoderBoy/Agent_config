import streamlit as st
import requests
import sseclient
import json

API_URL = "http://localhost:8000/api/v1"

def stream_chat(question, thread_id):
    url = f"{API_URL}/chat"
    # Fire off the request as a stream
    resp = requests.get(url, params={"query": question, "thread_id": thread_id}, stream=True)
    for line in resp.iter_lines():
        if line:
            yield line.decode("utf-8")

def chat_area():
    if "current_thread_id" not in st.session_state:
        st.session_state.current_thread_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("💬 Chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask something...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Stream the response
        # answer_so_far = ""
        # placeholder = st.empty()
        # for chunk in stream_chat(question, st.session_state.current_thread_id or ""):
            
        #     answer_so_far += chunk
        #     placeholder.markdown(answer_so_far)
        # st.session_state.messages.append({"role": "assistant", "content": answer_so_far})
        url = f"{API_URL}/chat"
    # Fire off the request as a stream
        resp = requests.get(url, params={"query": question, "thread_id": st.session_state.current_thread_id})
        data = resp.json()
        st.session_state.messages.append({"role": data["type"], "content": data["content"]})
        st.rerun()


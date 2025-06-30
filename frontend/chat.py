import streamlit as st
import requests
import sseclient
import json

API_URL = "http://localhost:8000/api/v1"

def stream_chat(question, thread_id):
    url = f"{API_URL}/chat"
    # Fire off the request as a stream
    resp = requests.get(url, params={"query": question, "thread_id": thread_id}, stream=True)
    client = sseclient.SSEClient(resp)
    text = ""
    for event in client.events():
        if event.event == "error":
            data = json.loads(event.data)
            st.error(f"Error: {data.get('error')}")
            break
        elif event.event == "done":
            break
        else:
            # parse token chunk
            chunk = json.loads(event.data).get("token", "")
            text += chunk
            # update the last assistant message in place
            st.chat_message("assistant", is_placeholder=True).markdown(text)
    return text

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
        answer = stream_chat(question, st.session_state.current_thread_id or "")
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()


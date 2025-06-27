import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

def chat_area():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("💬 Chat")

    # Show existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New question
    question = st.chat_input("Ask something...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        # send to appropriate API
        if st.session_state.get("current_thread_id"):
            response = requests.post(
                f"{API_URL}/qa_thread/{st.session_state.current_thread_id}",
                json={"question": question}
            )
        else:
            filename = "your_file.xml"
            response = requests.post(
                f"{API_URL}/qa",
                json={"filename": filename, "question": question}
            )
        answer = response.json().get("answer", "No answer returned.")
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

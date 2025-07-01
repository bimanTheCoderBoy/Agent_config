import streamlit as st
import sseclient
import json

API_URL = "http://localhost:8000/api/v1"

def stream_chat(question, thread_id):
    url = f"{API_URL}/chat?query={question}&thread_id={thread_id}"
    messages = sseclient.SSEClient(url)
    for event in messages:
        yield event

def chat_area():
    # initialize conversation state
    if "current_thread" not in st.session_state:
        st.session_state.current_thread = "default-thread1"

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thinking" not in st.session_state:
        st.session_state.thinking = False
    if "streaming" not in st.session_state:
        st.session_state.streaming = False

    st.title("💬 Agent Conversation (Vector Retrieval)")
    st.caption("Real-time retrieval with chunk streaming")

    # render prior messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("retrieval_query"):
                with st.expander("🔎 Retrieval Queries", expanded=False):
                    st.markdown(msg["retrieval_query"])
            if msg["role"] == "assistant" and msg.get("retrieval_ans"):
                with st.expander("🔎 Retrieved Context", expanded=False):
                    st.markdown(msg["retrieval_ans"])
            

    # user input
    prompt = st.chat_input("Ask something about your file...")
    if prompt and not st.session_state.streaming:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.thinking = True
        st.session_state.streaming = True

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # thinking spinner
            with st.spinner("🤔 Thinking..."):
                response_placeholder = st.empty()
                retrieval_placeholder = st.empty()
                retrieval_query_placeholder = st.empty()
                full_response = ""
                retrieval_info = None

                try:
                    for event in stream_chat(prompt, st.session_state.current_thread):
                        if not event.data or event.data.strip() == "":
                            continue
                        try:
                            data = json.loads(event.data)
                        except json.JSONDecodeError:
                            st.error(f"Invalid JSON: {event.data}")
                            continue

                        event_type = data.get("type")

                        if event_type == "content":
                            token = data.get("content", "")
                            full_response += token
                            response_placeholder.markdown(full_response + "▌")

                        elif event_type == "retrieval_start":
                            retrieval_placeholder.info("🔎 **Retrieving related chunks... please wait.**")
                            retrieval_query = data.get("query", "")
                            with retrieval_query_placeholder.expander("View retrieval queries", expanded=True):
                                st.markdown(
                                    retrieval_query[:1000] + "..." 
                                    if len(retrieval_query) > 1000 else retrieval_query
                                )

                        elif event_type == "retrieval_result":
                            retrieval_content = data.get("content", "")
                            retrieval_info = retrieval_content
                            retrieval_placeholder.success("✅ Retrieval completed!")
                            with retrieval_placeholder.expander("View retrieved context", expanded=True):
                                st.markdown(
                                    retrieval_content[:1000] + "..." 
                                    if len(retrieval_content) > 1000 else retrieval_content
                                )

                        elif event_type == "end":
                            response_placeholder.markdown(full_response)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response,
                                "retrieval_ans": retrieval_info,
                                "retrieval_query":retrieval_query
                            })
                            st.session_state.thinking = False
                            st.session_state.streaming = False
                            break

                    else:
                        st.session_state.thinking = False
                        st.session_state.streaming = False

                except Exception as e:
                    response_placeholder.error(f"❌ Streaming failed: {str(e)}")
                    st.session_state.thinking = False
                    st.session_state.streaming = False

        st.rerun()

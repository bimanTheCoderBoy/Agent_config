import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

def sidebar():
    with st.sidebar:
        st.title("🔀 Select View")
        view = st.radio("View Mode", ["📁 Files", "🧵 Threads"])

        if view == "📁 Files":
            handle_file_upload()
        elif view == "🧵 Threads":
            handle_threads()

def load_files():
    if "files" not in st.session_state:
        st.session_state.files = []

    response = requests.get(f"{API_URL}/get_files")
    if response.status_code == 200:
        st.session_state.files = response.json().get("files", [])
    else:
        st.error("❌ Failed to load files from the server.")    
def handle_file_upload():

    load_files()

    uploaded_file = st.file_uploader("Choose XML", type=["xml"])
    if uploaded_file:
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": (uploaded_file.name, uploaded_file)}
        )
        if response.status_code == 200:
            st.success("✅ Uploaded!")
            load_files()
        else:
            st.error("❌ Upload failed!")

    if st.session_state.files:
        st.markdown("### 📄 Uploaded Files")
        for f in st.session_state.files:
            with st.expander(f"📄 {f["file_name"]}"):
                if st.button(f"➕ Create New Thread" , key=f"create_thread_{f["file_id"]}"):
                    # call the backend to create a new thread
                    response = requests.post(
                        f"{API_URL}/init_thread/{f['file_id']}",
                    )
                    if response.status_code == 200:
                        thread_id = response.json().get("thread_id")
                        st.success(f"✅ Thread created! ID: {thread_id}")
                        # you could store thread_id to a session state too
                        st.session_state.current_thread = thread_id
                        st.session_state.messages=[{"role": "assitant", "content": f"Ask Any Question Regarding File {f['file_name']}"}]
                    else:
                        st.error("❌ Failed to create thread")


def handle_threads():
    
    st.session_state.threads = []
    response = requests.get(f"{API_URL}/get_threads")
    if response.status_code == 200:
        st.session_state.threads = response.json().get("threads", [])

    if st.session_state.threads:
        for thread in st.session_state.threads:
            if st.button(f"💬{thread['file_name']} with {thread['thread_id']}", key=f"thread_{thread['thread_id']}"):
                response = requests.get(f"{API_URL}/get_thread/{thread['thread_id']}")
                if response.status_code == 200:
                    messages = response.json()["state"]["channel_values"].get("messages", [])
                    print(messages)
                    messages= [ msg for msg in messages if msg["type"]!="system"] 
                    st.session_state.messages = [
                        {"role": msg["type"], "content": msg["content"]}
                        for msg in messages
                    ]
                    st.session_state.current_thread_id = thread["thread_id"]
                    st.success(f"Loaded thread: {thread['thread_id']}")
                    # st.rerun()
                else:
                    st.error("Failed to load thread")

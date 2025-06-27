# import streamlit as st
# import requests

# API_URL = "http://localhost:8000/api/v1"

# st.title("🛠 Config AI Mini")

# uploaded_file = st.file_uploader("Upload an XML File", type="xml")

# if uploaded_file:
#     # Upload to backend
#     files = {"file": uploaded_file.getvalue()}
#     response = requests.post(f"{API_URL}/upload", files={"file": (uploaded_file.name, uploaded_file)})
#     st.success("✅ File uploaded!")

    # # Show analysis
    # filename = uploaded_file.name
    # analysis = requests.get(f"{API_URL}/analyze/{filename}").json()
    # st.json(analysis)

    # # Ask questions
    # question = st.text_input("Ask a question about this config:")
    # if st.button("Ask"):
    #     resp = requests.post(f"{API_URL}/qa", json={"filename": filename, "question": question})
    #     st.write("Answer:", resp.json().get("answer"))

import streamlit as st
import requests

# ============ Config ============
st.set_page_config(page_title="Config AI", layout="wide")
API_URL = "http://localhost:8000/api/v1"

# ============ CSS ============

st.markdown("""
    <style>
    .topbar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        height: 50px;
        background-color: #1e1e1e;
        padding: 0 20px;
        color: white;
        font-size: 20px;
        font-weight: 600;
    }
    .sidebar .block-container {
        padding-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============ Topbar ============

st.markdown('<div class="topbar">🛠 Config AI</div>', unsafe_allow_html=True)

# ============ Sidebar (Threads) ============
with st.sidebar:
    st.title("📁 Upload XML File")

    # Toggle between Chat / Upload
    # view = st.radio("Select View", ["💬 Chat", "📁 Upload"])

    # # Session init
    # if "threads" not in st.session_state:
    #     st.session_state.threads = ["Default"]
    if "files" not in st.session_state:
        st.session_state.files = []

    # # ---------------- Chat View ----------------
    # if view == "💬 Chat":
    #     st.subheader("💬 Chat Threads")

    #     new_thread = st.text_input("🧵 New Thread Name")
    #     if st.button("➕ Add Thread") and new_thread:
    #         st.session_state.threads.append(new_thread)

    #     thread_selected = st.radio("🗂 Choose Thread", st.session_state.threads)

    # ---------------- Upload View ----------------
 
    uploaded_file = st.file_uploader("Choose XML", type=["xml"])
    if uploaded_file:
        # files = {"file": uploaded_file.getvalue()}
        response = requests.post("http://localhost:8000/api/v1/upload", 
            files={"file": (uploaded_file.name, uploaded_file)})
        if response.status_code == 200:
            st.success("✅ Uploaded!")
            st.session_state.files.append(uploaded_file.name)
        else:
            st.error("❌ Upload failed!")

        if st.session_state.files:
            st.markdown("### 📄 Uploaded Files")
            for f in st.session_state.files:
                st.markdown(f"• {f}")


# ============ Chat Interface ============

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Chat Interface")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask your XML config anything...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})

    # Send to backend
    filename = "your_file.xml"  # Replace with actual session/file logic
    response = requests.post(f"{API_URL}/qa", json={"filename": filename, "question": question})
    answer = response.json().get("answer", "No answer returned.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()  # To refresh chat messages

import streamlit as st
import requests
import json
import os
from components.model_selector import render_model_selector
from components.cost_display import render_cost_display
# from components.file_upload import render_file_upload  # 不再用单独左列，而是做成左下角按钮
from components.question_input import render_question_input

API_URL = os.getenv("API_URL", "http://localhost:8000")

def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "GPT-4o"
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = None
    if "pdf_name" not in st.session_state:
        st.session_state.pdf_name = None
    if "selected_text" not in st.session_state:
        st.session_state.selected_text = None
    if "token_usage" not in st.session_state:
        st.session_state.token_usage = {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0
        }
    # 新增一个 show_upload 控制上传区域是否可见
    if "show_upload" not in st.session_state:
        st.session_state.show_upload = False

def display_chat_history():
    """Display the chat history in a conversational format."""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def process_query(query):
    if not st.session_state.pdf_content and not st.session_state.pdf_name:
        st.warning("Please upload a PDF document first.")
        return

    # 用户消息
    st.session_state.chat_history.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        payload = {
            "model": st.session_state.selected_model,
            "question": query,
            "pdf_content": st.session_state.pdf_content,
            "pdf_name": st.session_state.pdf_name,
            "selected_text": st.session_state.selected_text
        }

        try:
            response = requests.post(f"{API_URL}/ask_question", json=payload)
            response.raise_for_status()
            result = response.json()

            answer = result.get("answer", "Sorry, I couldn't process your question.")
            message_placeholder.markdown(answer)

            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # 更新 token usage
            if "token_usage" in result:
                st.session_state.token_usage["total_input_tokens"] += result["token_usage"]["input_tokens"]
                st.session_state.token_usage["total_output_tokens"] += result["token_usage"]["output_tokens"]
                st.session_state.token_usage["total_cost"] += result["token_usage"]["cost"]

        except Exception as e:
            message_placeholder.markdown(f"Error: {str(e)}")

def generate_summary():
    if not st.session_state.pdf_content and not st.session_state.pdf_name:
        st.warning("Please upload a PDF document first.")
        return
    
    with st.chat_message("user"):
        st.markdown("Can you summarize this document for me?")
    st.session_state.chat_history.append({"role": "user", "content": "Can you summarize this document for me?"})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Generating summary...")

        payload = {
            "model": st.session_state.selected_model,
            "pdf_content": st.session_state.pdf_content,
            "pdf_name": st.session_state.pdf_name,
            "selected_text": st.session_state.selected_text
        }

        try:
            response = requests.post(f"{API_URL}/summarize", json=payload)
            response.raise_for_status()
            result = response.json()

            summary = result.get("summary", "Sorry, I couldn't generate a summary.")
            message_placeholder.markdown(summary)

            st.session_state.chat_history.append({"role": "assistant", "content": summary})

            if "token_usage" in result:
                st.session_state.token_usage["total_input_tokens"] += result["token_usage"]["input_tokens"]
                st.session_state.token_usage["total_output_tokens"] += result["token_usage"]["output_tokens"]
                st.session_state.token_usage["total_cost"] += result["token_usage"]["cost"]

        except Exception as e:
            message_placeholder.markdown(f"Error: {str(e)}")

def upload_pdf(uploaded_file):
    """Helper function to upload PDF via multipart/form-data and store content in session."""
    if uploaded_file is None:
        return
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf"),
    }
    try:
        resp = requests.post(f"{API_URL}/upload_pdf", files=files)
        resp.raise_for_status()
        data = resp.json()

        st.session_state.pdf_name = data.get("name", uploaded_file.name)
        st.session_state.pdf_content = data.get("content", "")
        st.session_state.selected_text = None
        st.success(f"PDF '{uploaded_file.name}' uploaded and processed!")
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")

def main():
    # 1. 宽屏布局
    st.set_page_config(page_title="PDF AI Assistant", layout="wide")
    
    # 2. 注入自定义 CSS，增大聊天区宽度
    st.markdown(
        """
        <style>
        /* 将主内容区的最大宽度设置为1200px或更大 */
        section.main > div.block-container {
            max-width: 1200px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    initialize_session_state()

    # 左侧Sidebar
    with st.sidebar:
        st.title("PDF AI Assistant")
        render_model_selector()
        st.divider()
        render_cost_display()

    st.header("Chat with your PDF")
    display_chat_history()

    # ============ 右侧 PDF 内容展示 ============ #
    if st.session_state.pdf_content:
        st.subheader("PDF Content Preview")

        # 自定义滚动容器
        scrollable_div = f"""
        <div style="height:400px; overflow-y:auto; border:1px solid #ccc; padding:1rem;">
        {st.session_state.pdf_content}
        </div>
        """
        st.markdown(scrollable_div, unsafe_allow_html=True)

    # ============ 底部输入栏，模拟ChatGPT风格 + 左下角“+”按钮 ============ #
    col_plus, col_input, col_send = st.columns([0.1, 1, 0.15])

    # 左下角 “+” 按钮
    with col_plus:
        if st.button("+"):
            st.session_state.show_upload = not st.session_state.show_upload

    # 中间 文本输入框
    with col_input:
        user_input = st.text_input("Your message", value="", label_visibility="collapsed")

    # 右侧 发送按钮
    with col_send:
        if st.button("Send", use_container_width=True):
            if user_input.strip():
                process_query(user_input)
            else:
                st.warning("Please enter a message.")

    # 如果点击了 +，显示上传区
    if st.session_state.show_upload:
        with st.expander("Upload a PDF"):
            uploaded_file = st.file_uploader("Select PDF", type=["pdf"])
            if uploaded_file:
                upload_pdf(uploaded_file)

    # Summarize 按钮
    st.button("Summarize PDF", on_click=generate_summary)


if __name__ == "__main__":
    main()

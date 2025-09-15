import streamlit as st
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List
from korean_utils import KoreanTextProcessor
from ui_components import UIComponents

# ---- Mock ModelManager ----
class MockModelManager:
    def __init__(self):
        self.model = "mock_model"
        self.tokenizer = "mock_tokenizer"
        self.device = "cpu"
        self.model_name = "Qwen/Qwen2-7B-Instruct"
    
    def load_model(self, progress_callback=None):
        time.sleep(0.5)
        return True
    
    def generate_chat_response(self, conversation_context, **kwargs):
        time.sleep(0.3)
        return "이것은 Mock AI 응답입니다."

# ---- Chat Session Manager ----
class ChatSessionManager:
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None
    
    def create_new_session(self, is_temporary=False):
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "title": "새 채팅" if st.session_state.language=='ko' else "New Chat",
            "messages": [],
            "created_at": datetime.now(),
            "is_temporary": is_temporary,
            "last_updated": datetime.now()
        }
        if not is_temporary:
            self.sessions[session_id] = session_data
        self.current_session_id = session_id
        return session_id, session_data
    
    def get_current_session(self):
        if self.current_session_id in self.sessions:
            return self.sessions[self.current_session_id]
        return None
    
    def add_message(self, role, content):
        session = self.get_current_session()
        if session:
            session["messages"].append({"role": role, "content": content, "timestamp": datetime.now()})
            session["last_updated"] = datetime.now()
    
    def get_session_list(self):
        return sorted(self.sessions.values(), key=lambda x:x["last_updated"], reverse=True)

# ---- Init Session State ----
if 'language' not in st.session_state:
    st.session_state.language = 'ko'
if 'chat_session_manager' not in st.session_state:
    st.session_state.chat_session_manager = ChatSessionManager()
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = MockModelManager()
if 'temp_session' not in st.session_state:
    st.session_state.temp_session = None

# ---- Init UI & Korean Processor ----
ui = UIComponents()
korean_processor = KoreanTextProcessor()

# ---- Main ----
def main():
    st.set_page_config(page_title="HB AI", page_icon="🤖", layout="wide")
    
    # Sidebar
    with st.sidebar:
        render_chat_sidebar()
    
    # Main content
    render_main_chat_area()

# ---- Sidebar ----
def render_chat_sidebar():
    session_manager = st.session_state.chat_session_manager
    if st.button("🌐 EN" if st.session_state.language=='ko' else "🌐 KO"):
        st.session_state.language = 'ko' if st.session_state.language=='en' else 'en'
        st.rerun()
    
    if st.button("➕ 새 채팅" if st.session_state.language=='ko' else "➕ New Chat"):
        session_manager.create_new_session()
        st.rerun()
    
    st.markdown("---")
    sessions = session_manager.get_session_list()
    for session in sessions:
        if st.button(f"💬 {session['title']}"):
            session_manager.current_session_id = session['id']
            st.rerun()

# ---- Main Chat Area ----
def render_main_chat_area():
    session_manager = st.session_state.chat_session_manager
    session = session_manager.get_current_session()
    
    if not session:
        ui.render_welcome_screen()
        return
    
    st.markdown(f"### {session['title']}")
    for msg in session["messages"]:
        if msg["role"]=="user":
            ui.render_user_message(msg["content"])
        else:
            ui.render_ai_message(msg["content"])
    
    render_chat_input()

# ---- Chat Input ----
def render_chat_input():
    session_manager = st.session_state.chat_session_manager
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="메시지를 입력하세요..." if st.session_state.language=='ko' else "Type your message...")
        if st.form_submit_button("📤") and user_input.strip():
            session_manager.add_message("user", user_input)
            response = st.session_state.model_manager.generate_chat_response(user_input)
            session_manager.add_message("assistant", response)
            st.rerun()

if __name__=="__main__":
    main()

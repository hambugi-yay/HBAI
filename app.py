import streamlit as st
import os
import time
import random
import uuid
from datetime import datetime
from typing import Dict, List
from korean_utils import KoreanTextProcessor
from ui_components import UIComponents

# ---------------- Mock ModelManager ---------------- #
class MockModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.model_name = "Qwen/Qwen2-7B-Instruct"
        self.is_mock = True
        
    def load_model(self, progress_callback=None):
        try:
            if progress_callback:
                for i in range(1, 11):
                    time.sleep(0.05)
                    msg = ["디바이스 설정 중...", "토크나이저 로드 중...", "모델 로드 중...", "로드 완료!"][min(i//3,3)]
                    progress_callback(i, 10, msg)
            self.model = "mock_model"
            self.tokenizer = "mock_tokenizer"
            return True
        except:
            return False
    
    def generate_chat_response(self, conversation_context, max_length=300, temperature=0.7, top_p=0.9):
        time.sleep(0.2)
        if "user\n" in conversation_context:
            last_message = conversation_context.split("user\n")[-1].split("<|im_end|>")[0].strip()
        else:
            last_message = "Hello"
        korean_chat_responses = [
            f"'{last_message}'에 대한 흥미로운 질문이네요! 자세히 설명해 드리겠습니다.",
            f"말씀하신 '{last_message}' 관련해서 도움을 드릴 수 있습니다. 어떤 부분이 궁금하신가요?",
            "네, 이해했습니다. 한국어로 자연스럽게 대화하며 도움을 드리겠습니다.",
            "좋은 질문입니다! 더 자세한 정보를 원하시면 언제든 말씀해 주세요."
        ]
        english_chat_responses = [
            f"That's an interesting question about '{last_message}'! Let me explain in detail.",
            f"I can help you with '{last_message}'. What specific aspect would you like to know more about?",
            "Yes, I understand. I'm here to help you with natural conversation in both languages.",
            "Great question! Feel free to ask if you need more detailed information."
        ]
        if any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in last_message):
            return random.choice(korean_chat_responses)
        else:
            return random.choice(english_chat_responses)

# ---------------- Session Manager ---------------- #
class ChatSessionManager:
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None
        
    def create_new_session(self, is_temporary=False):
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'title': "새 채팅",
            'messages': [],
            'created_at': datetime.now(),
            'is_temporary': is_temporary,
            'last_updated': datetime.now()
        }
        if not is_temporary:
            self.sessions[session_id] = session_data
        self.current_session_id = session_id
        return session_id, session_data
    
    def get_current_session(self):
        if self.current_session_id:
            if self.current_session_id in self.sessions:
                return self.sessions[self.current_session_id]
            elif hasattr(st.session_state, 'temp_session') and st.session_state.temp_session['id'] == self.current_session_id:
                return st.session_state.temp_session
        return None
    
    def add_message(self, role, content):
        current_session = self.get_current_session()
        if current_session:
            message = {'role': role, 'content': content, 'timestamp': datetime.now()}
            current_session['messages'].append(message)
            current_session['last_updated'] = datetime.now()
            if len(current_session['messages']) == 2 and role == 'assistant':
                user_message = current_session['messages'][0]['content']
                current_session['title'] = user_message[:30] + ("..." if len(user_message)>30 else "")

# ---------------- Session State Init ---------------- #
if 'language' not in st.session_state:
    st.session_state.language = 'ko'
if 'chat_session_manager' not in st.session_state:
    st.session_state.chat_session_manager = ChatSessionManager()
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = MockModelManager()
    st.session_state.model_manager.load_model()
if 'temp_session' not in st.session_state:
    st.session_state.temp_session = None

ui = UIComponents()
korean_processor = KoreanTextProcessor()

# ---------------- Main App ---------------- #
def main():
    st.set_page_config(page_title="HB AI - 한국어 AI 채팅", page_icon="🤖", layout="wide")
    with st.sidebar:
        render_sidebar()
    render_main_area()

# ---------------- Sidebar ---------------- #
def render_sidebar():
    session_manager = st.session_state.chat_session_manager
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🌐 EN" if st.session_state.language=='ko' else "🌐 KO"):
            st.session_state.language = 'ko' if st.session_state.language=='en' else 'en'
            st.experimental_rerun()
    with col2:
        if st.button("➕ 새 채팅" if st.session_state.language=='ko' else "➕ New Chat"):
            session_manager.create_new_session()
            st.experimental_rerun()
    st.markdown("---")
    if st.session_state.language=='ko':
        st.subheader("📋 채팅 기록")
    else:
        st.subheader("📋 Chat History")
    # 세션 버튼
    for session in session_manager.sessions.values():
        if st.button(f"💬 {session['title']}", key=session['id']):
            session_manager.current_session_id = session['id']
            st.experimental_rerun()

# ---------------- Main Area ---------------- #
def render_main_area():
    session_manager = st.session_state.chat_session_manager
    current_session = session_manager.get_current_session()
    if current_session:
        st.markdown(f"### {current_session['title']}")
    else:
        st.markdown("### 🤖 HB AI와 대화하기")
        st.markdown("새 채팅을 시작하거나 기존 채팅을 선택하세요.")
    messages_container = st.container()
    with messages_container:
        if current_session:
            render_messages(current_session['messages'])
        else:
            ui.render_welcome_screen()
    render_chat_input()

# ---------------- Messages ---------------- #
def render_messages(messages: List[Dict]):
    for msg in messages:
        role, content = msg['role'], msg['content']
        if role=='user':
            col1,col2 = st.columns([1,4])
            with col2:
                st.markdown(f'<div style="background:#007bff;color:white;padding:10px;border-radius:10px;margin:5px 0;text-align:right;"><strong>👤 {"사용자" if st.session_state.language=="ko" else "You"}</strong><br>{content}</div>', unsafe_allow_html=True)
        else:
            col1,col2 = st.columns([4,1])
            with col1:
                st.markdown(f'<div style="background:#f1f3f4;color:black;padding:10px;border-radius:10px;margin:5px 0;"><strong>🤖 HB AI</strong><br>{content}</div>', unsafe_allow_html=True)

# ---------------- Chat Input ---------------- #
def render_chat_input():
    st.markdown("---")
    with st.form(key="chat_form", clear_on_submit=True):
        col1,col2 = st.columns([5,1])
        with col1:
            user_input = st.text_input(label="message", placeholder="메시지를 입력하세요..." if st.session_state.language=='ko' else "Type your message...", label_visibility="collapsed")
        with col2:
            submit = st.form_submit_button("📤")
        if submit and user_input.strip():
            process_chat(user_input.strip())
            st.experimental_rerun()

# ---------------- Process Chat ---------------- #
def process_chat(user_input):
    session_manager = st.session_state.chat_session_manager
    if not session_manager.current_session_id:
        session_manager.create_new_session()
    session_manager.add_message("user", user_input)
    # 대화 컨텍스트 준비
    current_session = session_manager.get_current_session()
    chat_history = [(m['role'], m['content']) for m in current_session['messages']]
    conversation_context = korean_processor.prepare_chat_context(chat_history)
    # Mock / real 모델 응답
    response = st.session_state.model_manager.generate_chat_response(conversation_context)
    response = korean_processor.post_process_response(response)
    session_manager.add_message("assistant", response)

# ---------------- Run ---------------- #
if __name__=="__main__":
    main()

import streamlit as st
import os
import traceback
import time
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from korean_utils import KoreanTextProcessor
from ui_components import UIComponents
from langdetect import detect
import json

# Mock ModelManager for testing when dependencies are not available
class MockModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.model_name = "Qwen/Qwen2-7B-Instruct"
        self.is_mock = True

    def load_model(self, progress_callback=None):
        """Mock model loading with progress simulation"""
        try:
            if progress_callback:
                for i in range(1, 11):
                    time.sleep(0.01) # Very fast load simulation
                    progress_callback(i, 10, "로드 중...")
            self.model = "mock_model"
            self.tokenizer = "mock_tokenizer"
            return True
        except Exception as e:
            print(f"Error in mock model loading: {str(e)}")
            return False

    def generate_text(self, prompt, max_length=200, temperature=0.7, top_p=0.9):
        """Generate mock text response"""
        time.sleep(0.3)
        korean_responses = [
            "안녕하세요! 저는 HB AI입니다. 한국어로 자연스럽게 대화할 수 있습니다.",
            "요청하신 내용에 대해 도움을 드리겠습니다. 더 구체적인 질문이 있으시면 언제든 말씀해 주세요.",
            "한국어 텍스트 생성 기능이 정상적으로 작동하고 있습니다. 다양한 주제에 대해 질문해 보세요.",
            "창의적인 아이디어를 제공하거나 학습에 도움을 드릴 수 있습니다. 어떤 도움이 필요하신가요?"
        ]
        english_responses = [
            "Hello! I'm HB AI. I can communicate naturally in both Korean and English.",
            "I'd be happy to help you with your request. Please feel free to ask more specific questions.",
            "The Korean text generation feature is working properly. You can ask me about various topics.",
            "I can provide creative ideas or help with learning. What kind of assistance do you need?"
        ]
        if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in prompt):
            return random.choice(korean_responses)
        else:
            return random.choice(english_responses)

    def generate_chat_response(self, conversation_context, max_length=300, temperature=0.7, top_p=0.9):
        """Generate mock chat response"""
        time.sleep(0.3)
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
        if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in last_message):
            return random.choice(korean_chat_responses)
        else:
            return random.choice(english_chat_responses)

    def cleanup(self):
        self.model = None
        self.tokenizer = None

    def is_loaded(self):
        return self.model is not None

    def get_model_info(self):
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded(),
            "cuda_available": False,
            "memory_usage": 0
        }

try:
    from huggingface_model_manager import HuggingFaceModelManager
    ModelManager = HuggingFaceModelManager
    USE_REAL_MODEL = True
    MODEL_TYPE = "HuggingFace API"
except ImportError:
    try:
        from model_manager import ModelManager
        USE_REAL_MODEL = True
        MODEL_TYPE = "Local Model"
    except ImportError:
        ModelManager = MockModelManager
        USE_REAL_MODEL = False
        MODEL_TYPE = "Mock Model"

st.set_page_config(
    page_title="HB AI - 한국어 AI 채팅",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ChatSessionManager:
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None

    def create_new_session(self, is_temporary=False):
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'title': self._generate_session_title(),
            'messages': [],
            'created_at': datetime.now(),
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

    def switch_session(self, session_id):
        if session_id in self.sessions:
            self.current_session_id = session_id
            return True
        return False

    def add_message(self, role, content):
        current_session = self.get_current_session()
        if current_session:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now()
            }
            current_session['messages'].append(message)
            current_session['last_updated'] = datetime.now()
            if len(current_session['messages']) == 2 and role == 'assistant':
                user_message = current_session['messages'][0]['content']
                current_session['title'] = self._generate_title_from_message(user_message)

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                new_session_list = self.get_session_list()
                if new_session_list:
                    self.current_session_id = new_session_list[0]['id']
                else:
                    self.current_session_id = None

    def get_session_list(self):
        sessions = list(self.sessions.values())
        return sorted(sessions, key=lambda x: x['last_updated'], reverse=True)

    def _generate_session_title(self):
        return "새 채팅" if st.session_state.get('language', 'ko') == 'ko' else "New Chat"

    def _generate_title_from_message(self, message):
        if len(message) > 30:
            return message[:30] + "..."
        return message

if 'language' not in st.session_state:
    st.session_state.language = 'ko'
if 'chat_session_manager' not in st.session_state:
    st.session_state.chat_session_manager = ChatSessionManager()
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None
if 'temp_session' not in st.session_state:
    st.session_state.temp_session = None
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False

if not st.session_state.model_loaded:
    with st.spinner("AI 모델을 로드하는 중..."):
        if not st.session_state.model_manager:
            st.session_state.model_manager = ModelManager()
        try:
            st.session_state.model_manager.load_model()
            st.session_state.model_loaded = True
        except:
            st.session_state.model_loaded = False
            st.error("AI 모델 로딩에 실패했습니다. Mock 모델로 전환합니다.")

ui = UIComponents()
korean_processor = KoreanTextProcessor()

def main():
    st.markdown(
        """
        <style>
        .main {
            background-color: #f5f5f5;
        }
        .stButton>button {
            border: 1px solid #ddd;
            border-radius: 20px;
            background-color: white;
            color: #333;
            padding: 8px 16px;
        }
        .stButton>button:hover {
            border-color: #bbb;
        }
        .st-chat-message-container .st-chat-message-bubble {
            border-radius: 18px;
            padding: 15px;
            margin: 10px 0;
            line-height: 1.5;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .st-chat-message-container .st-chat-message-bubble.user {
            background-color: #007bff;
            color: white;
            text-align: right;
        }
        .st-chat-message-container .st-chat-message-bubble.assistant {
            background-color: #e9ecef;
            color: black;
            text-align: left;
        }
        .st-emotion-cache-1r650o1 {
            padding-top: 0rem;
        }
        .st-emotion-cache-16270h4 {
            padding-left: 0rem;
            padding-right: 0rem;
        }
        .st-emotion-cache-1h9999r {
            border: none;
            box-shadow: none;
        }
        .st-emotion-cache-1qg0590 {
            padding: 0;
        }
        .st-emotion-cache-9r12l8 {
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    with st.sidebar:
        render_chat_sidebar()
    render_main_chat_area()

def render_chat_sidebar():
    session_manager = st.session_state.chat_session_manager
    st.title("HB AI 🤖")
    st.markdown("---")

    if st.button(
        "✨ New Chat" if st.session_state.language == 'en' else "✨ 새 채팅",
        use_container_width=True,
        type="primary"
    ):
        session_id, _ = session_manager.create_new_session()
        st.rerun()

    st.subheader(
        "Recent" if st.session_state.language == 'en' else "최근 기록"
    )

    sessions = session_manager.get_session_list()
    for session in sessions:
        is_current = session_manager.current_session_id == session['id']
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"{session['title']}",
                key=f"session_{session['id']}",
                type="primary" if is_current else "secondary",
                use_container_width=True
            ):
                session_manager.switch_session(session['id'])
                st.rerun()
        
        with col2:
            if st.button(
                "🗑️",
                key=f"delete_{session['id']}",
                help="이 채팅만 삭제합니다." if st.session_state.language == 'ko' else "Delete this chat only"
            ):
                session_manager.delete_session(session['id'])
                st.rerun()

    st.markdown("---")
    
    all_sessions_data = json.dumps(session_manager.sessions, default=str, indent=2)
    st.download_button(
        label="📥 모든 채팅 기록 다운로드",
        data=all_sessions_data,
        file_name=f"HBAI_all_chats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="모든 대화 기록을 하나의 JSON 파일로 저장합니다."
    )
    
    uploaded_file = st.file_uploader(
        "📤 채팅 기록 업로드",
        type="json",
        help="다운로드한 JSON 파일을 업로드하여 대화 기록을 불러올 수 있습니다."
    )
    if uploaded_file is not None:
        try:
            uploaded_data = json.load(uploaded_file)
            for session_id, session_data in uploaded_data.items():
                if session_id not in session_manager.sessions:
                    # Fix: Convert string dates to datetime objects
                    if 'last_updated' in session_data and isinstance(session_data['last_updated'], str):
                        session_data['last_updated'] = datetime.fromisoformat(session_data['last_updated'])
                    if 'created_at' in session_data and isinstance(session_data['created_at'], str):
                        session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                    
                    # Fix: Also convert message timestamps
                    if 'messages' in session_data:
                        for message in session_data['messages']:
                            if 'timestamp' in message and isinstance(message['timestamp'], str):
                                message['timestamp'] = datetime.fromisoformat(message['timestamp'])
                                
                    session_manager.sessions[session_id] = session_data
            st.success("대화 기록을 성공적으로 불러왔습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"파일을 불러오는 중 오류가 발생했습니다: {e}")
    
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "⚙️ Settings" if st.session_state.language == 'en' else "⚙️ 설정",
            use_container_width=True
        ):
            st.info("Settings not yet implemented." if st.session_state.language == 'en' else "설정 기능은 아직 구현되지 않았습니다.")
    with col2:
        if st.button(
            "🌐 KO/EN",
            use_container_width=True
        ):
            st.session_state.language = 'ko' if st.session_state.language == 'en' else 'en'
            st.rerun()

def render_main_chat_area():
    session_manager = st.session_state.chat_session_manager
    current_session = session_manager.get_current_session()
    
    messages_container = st.container()

    if current_session is None or len(current_session['messages']) == 0:
        render_gemini_welcome_screen()
    else:
        with messages_container:
            render_messages(current_session['messages'])

    with st.container():
        render_chat_input()

def render_gemini_welcome_screen():
    suggestions = [
        "양자 컴퓨터를 쉽게 설명해 줘.",
        "창의적인 아이디어가 필요해. 새로운 앱 아이디어를 3가지 추천해 줄 수 있을까?",
        "파이썬의 제너레이터와 이터레이터의 차이점을 알려 줘.",
        "유럽 여행을 위한 가성비 좋은 도시 5곳을 추천해 줘.",
        "재미있는 SF 소설 줄거리를 요약해 줘.",
        "건강한 점심 메뉴 3가지와 레시피를 알려 줘.",
        "2050년 미래의 학교는 어떤 모습일까?",
        "영화 '인터스텔라'의 과학적 배경을 설명해 줘."
    ]
    
    selected_suggestions = random.sample(suggestions, 4)
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 10vh;">
            <h1 style="font-size: 3rem; color: #444;">
                <span style="background: linear-gradient(to right, #4285f4, #ea4335, #fbbc05, #34a853); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">HB AI</span>
            </h1>
            <p style="font-size: 1.2rem; color: #666;">
                무엇이든 물어보세요.
            </p>
        </div>
        ---
        <h3 style="text-align: center;">예시</h3>
        <script>
            function setInputValue(value) {{
                const input = document.querySelector('input[placeholder^="메시지를"]');
                if (input) {{
                    input.value = value;
                    input.focus();
                }}
            }}
        </script>
        """,
        unsafe_allow_html=True
    )
    
    cols = st.columns(2)
    for i in range(4):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 10px; cursor: pointer;" onclick="setInputValue('{selected_suggestions[i]}')">
                    <p><strong>{selected_suggestions[i]}</strong></p>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_messages(messages: List[Dict]):
    for message in messages:
        role = message['role']
        content = message['content']

        if role == 'user':
            st.markdown(
                f'<div class="st-chat-message-bubble user">👤 <strong>You</strong><br>{content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="st-chat-message-bubble assistant">🤖 <strong>HB AI</strong><br>{content}</div>',
                unsafe_allow_html=True
            )

def render_chat_input():
    st.markdown("---")
    
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                label="message",
                placeholder="메시지를 입력하세요..." if st.session_state.language == 'ko' else "Type your message...",
                label_visibility="collapsed",
                autocomplete="off"
            )
        with col2:
            send_button = st.form_submit_button(
                "📤" if st.session_state.language == 'ko' else "📤",
                use_container_width=True
            )
        if send_button and user_input.strip():
            process_chat_message(user_input.strip())
            st.rerun()

def process_chat_message(user_input):
    try:
        session_manager = st.session_state.chat_session_manager
        if not session_manager.current_session_id:
            session_id, _ = session_manager.create_new_session()
        
        session_manager.add_message("user", user_input)
        
        detected_lang = 'ko'
        try:
            detected_lang = detect(user_input)
        except:
            pass

        temp_chat_history = [(msg['role'], msg['content']) for msg in session_manager.get_current_session()['messages']]
        
        lang_instruction = "응답은 무조건 한국어로 해주세요." if detected_lang == 'ko' else "Please respond strictly in English."
        temp_chat_history[-1] = ('user', f"{user_input}\n\n[INSTRUCTION]: {lang_instruction}")
        
        with st.spinner(
            "AI가 응답을 생성하는 중입니다..." if st.session_state.language == 'ko' else "AI is generating response..."
        ):
            response = None
            conversation_context = korean_processor.prepare_chat_context(temp_chat_history)
              
            if st.session_state.model_loaded and st.session_state.model_manager:
                try:
                    response = st.session_state.model_manager.generate_chat_response(
                        conversation_context,  
                        max_length=300,  
                        temperature=0.7,  
                        top_p=0.9  
                    )  
                except Exception as e:
                    print(f"Real model failed: {str(e)}")
                    response = None
              
            if not response:
                print("Using mock response fallback")
                mock_manager = MockModelManager()
                response = mock_manager.generate_chat_response(user_input)
              
            if response:
                processed_response = korean_processor.post_process_response(response)
                session_manager.add_message("assistant", processed_response)
            else:
                error_msg = ("응답 생성에 실패했습니다. 다시 시도해주세요." if st.session_state.language == 'ko' else "Failed to generate response. Please try again.")
                session_manager.add_message("assistant", error_msg)
      
    except Exception as e:
        error_msg = (f"채팅 처리 중 오류가 발생했습니다: {str(e)}" if st.session_state.language == 'ko' else f"Error processing chat: {str(e)}")
        st.error(error_msg)

if __name__ == "__main__":
    main()

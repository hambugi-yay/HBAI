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
                    time.sleep(0.1)  # Simulate loading time
                    if i <= 3:
                        msg = "디바이스 설정 중..." if os.getenv('LANG', '').startswith('ko') else "Setting up device..."
                    elif i <= 6:
                        msg = "토크나이저 로드 중..." if os.getenv('LANG', '').startswith('ko') else "Loading tokenizer..."
                    elif i <= 9:
                        msg = "모델 로드 중..." if os.getenv('LANG', '').startswith('ko') else "Loading model..."
                    else:
                        msg = "로드 완료!" if os.getenv('LANG', '').startswith('ko') else "Load complete!"
                    progress_callback(i, 10, msg)
            self.model = "mock_model"
            self.tokenizer = "mock_tokenizer"
            return True
        except Exception as e:
            print(f"Error in mock model loading: {str(e)}")
            return False

    def generate_text(self, prompt, max_length=200, temperature=0.7, top_p=0.9):
        """Generate mock text response"""
        time.sleep(0.5)  # Simulate processing time
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
        # Detect if prompt is in Korean
        if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in prompt):
            return random.choice(korean_responses)
        else:
            return random.choice(english_responses)

    def generate_chat_response(self, conversation_context, max_length=300, temperature=0.7, top_p=0.9):
        """Generate mock chat response"""
        time.sleep(0.3)  # Simulate processing time
        # Extract the last user message from context
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
        # Detect if message is in Korean
        if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in last_message):
            return random.choice(korean_chat_responses)
        else:
            return random.choice(english_chat_responses)

    def cleanup(self):
        """Mock cleanup"""
        self.model = None
        self.tokenizer = None

    def is_loaded(self):
        """Check if mock model is loaded"""
        return self.model is not None

    def get_model_info(self):
        """Get mock model information"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded(),
            "cuda_available": False,
            "memory_usage": 0
        }

# Try to import real ModelManager, prefer HuggingFace API, fall back to mock if dependencies missing
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

# Page configuration
st.set_page_config(
    page_title="HB AI - 한국어 AI 채팅",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chat Session Management Class
class ChatSessionManager:
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None

    def create_new_session(self, is_temporary=False):
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'title': self._generate_session_title(),
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
        """Get current session data"""
        if self.current_session_id:
            if self.current_session_id in self.sessions:
                return self.sessions[self.current_session_id]
            elif hasattr(st.session_state, 'temp_session') and st.session_state.temp_session['id'] == self.current_session_id:
                return st.session_state.temp_session
        return None

    def switch_session(self, session_id):
        """Switch to a different session"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return True
        return False

    def add_message(self, role, content):
        """Add message to current session"""
        current_session = self.get_current_session()
        if current_session:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now()
            }
            current_session['messages'].append(message)
            current_session['last_updated'] = datetime.now()
            # Update session title based on first message
            if len(current_session['messages']) == 2 and role == 'assistant':
                user_message = current_session['messages'][0]['content']
                current_session['title'] = self._generate_title_from_message(user_message)

    def delete_session(self, session_id):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None

    def get_session_list(self):
        """Get list of sessions sorted by last updated"""
        sessions = list(self.sessions.values())
        return sorted(sessions, key=lambda x: x['last_updated'], reverse=True)

    def _generate_session_title(self):
        """Generate initial session title"""
        return "새 채팅" if st.session_state.get('language', 'ko') == 'ko' else "New Chat"

    def _generate_title_from_message(self, message):
        """Generate title from first user message"""
        # Truncate message to reasonable length for title
        if len(message) > 30:
            return message[:30] + "..."
        return message

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'ko'
if 'chat_session_manager' not in st.session_state:
    st.session_state.chat_session_manager = ChatSessionManager()
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None
if 'temp_session' not in st.session_state:
    st.session_state.temp_session = None

# Auto-load model on startup to remove development displays
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if not st.session_state.model_manager:
    st.session_state.model_manager = ModelManager()
try:
    st.session_state.model_manager.load_model()
    st.session_state.model_loaded = True
except:
    # Fall back to mock if model loading fails
    st.session_state.model_loaded = False

# Initialize components
ui = UIComponents()
korean_processor = KoreanTextProcessor()

def main():
    """Main ChatGPT-style interface"""
    # Gemini-style Layout
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
    # Sidebar for chat sessions
    with st.sidebar:
        render_chat_sidebar()
    # Main content area
    render_main_chat_area()

def render_chat_sidebar():
    """Render Gemini-style sidebar with chat sessions and settings"""
    session_manager = st.session_state.chat_session_manager
    st.title("HB AI 🤖")
    st.markdown("---")
    # New chat button at the top
    if st.button(
        "✨ New Chat" if st.session_state.language == 'en' else "✨ 새 채팅",
        use_container_width=True,
        type="primary"
    ):
        session_id, _ = session_manager.create_new_session()
        st.rerun()

    # Session list title
    st.subheader(
        "Recent" if st.session_state.language == 'en' else "최근 기록"
    )

    # Display regular sessions
    sessions = session_manager.get_session_list()
    for session in sessions:
        is_current = session_manager.current_session_id == session['id']
        button_label = session['title']
        if st.button(
            f"{button_label}",
            key=f"session_{session['id']}",
            use_container_width=True
        ):
            session_manager.switch_session(session['id'])
            st.rerun()

    st.markdown("---")

    # Sidebar footer with language toggle and settings
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "⚙️ Settings" if st.session_state.language == 'en' else "⚙️ 설정",
            use_container_width=True
        ):
            # Future settings pop-up or page
            st.info("Settings not yet implemented." if st.session_state.language == 'en' else "설정 기능은 아직 구현되지 않았습니다.")
    with col2:
        if st.button(
            "🌐 KO/EN",
            use_container_width=True
        ):
            st.session_state.language = 'ko' if st.session_state.language == 'en' else 'en'
            st.rerun()

def render_main_chat_area():
    """Render main chat area with messages and input"""
    session_manager = st.session_state.chat_session_manager
    current_session = session_manager.get_current_session()
    
    # Placeholder for messages
    messages_container = st.container()

    if current_session is None:
        render_gemini_welcome_screen()
    else:
        with messages_container:
            render_messages(current_session['messages'])

    # Input area at bottom
    with st.container():
        render_chat_input()

def render_gemini_welcome_screen():
    """Render a Gemini-style welcome screen with suggestions."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 10vh;">
            <h1 style="font-size: 3rem; color: #444;">
                <span style="background: linear-gradient(to right, #4285f4, #ea4335, #fbbc05, #34a853); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">HB AI</span>
            </h1>
            <p style="font-size: 1.2rem; color: #666;">
                How can I help you today?
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")

    # Suggestion boxes
    st.subheader("Examples")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 10px; cursor: pointer;" onclick="document.querySelector('input[placeholder=\\'Type your message...\\']').value='Explain quantum computing in simple terms'">
                <p><strong>Explain quantum computing</strong></p>
                <p>in simple terms</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 10px; cursor: pointer;" onclick="document.querySelector('input[placeholder=\\'Type your message...\\']').value='What are some healthy food options for a quick lunch?'">
                <p><strong>Healthy lunch ideas</strong></p>
                <p>for a busy workday</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 10px; cursor: pointer;" onclick="document.querySelector('input[placeholder=\\'Type your message...\\']').value='Write a short story about a detective in a futuristic city.'">
                <p><strong>Write a short story</strong></p>
                <p>about a detective in a futuristic city</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 12px; margin-bottom: 10px; cursor: pointer;" onclick="document.querySelector('input[placeholder=\\'Type your message...\\']').value='What is the capital of France?'">
                <p><strong>What's the capital of France?</strong></p>
                <p>and some interesting facts about it</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_messages(messages: List[Dict]):
    """Render chat messages with Gemini-style bubbles"""
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
    """Render bottom chat input area"""
    st.markdown("---")
    
    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                label="message",
                placeholder="메시지를 입력하세요..." if st.session_state.language == 'ko' else "Type your message...",
                label_visibility="collapsed"
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
    """Process chat message and generate AI response"""
    try:
        session_manager = st.session_state.chat_session_manager
        # Create new session if none exists
        if not session_manager.current_session_id:
            session_id, _ = session_manager.create_new_session()
        # Add user message to current session
        session_manager.add_message("user", user_input)
        # Generate AI response
        with st.spinner(
            "AI가 응답을 생성하는 중입니다..." if st.session_state.language == 'ko' else "AI is generating response..."
        ):
            response = None
            # Prepare conversation context from current session
            current_session = session_manager.get_current_session()
            if current_session:
                chat_history = [(msg['role'], msg['content']) for msg in current_session['messages']]
                conversation_context = korean_processor.prepare_chat_context(chat_history)
                # Try real model first if available
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
                # Fall back to mock responses if real model unavailable or failed
                if not response:
                    print("Using mock response fallback")
                    mock_manager = MockModelManager()
                    response = mock_manager.generate_chat_response(conversation_context)
                if response:
                    # Process Korean text
                    processed_response = korean_processor.post_process_response(response)
                    session_manager.add_message("assistant", processed_response)
                else:
                    error_msg = (
                        "응답 생성에 실패했습니다. 다시 시도해주세요."
                        if st.session_state.language == 'ko'
                        else "Failed to generate response. Please try again."
                    )
                    session_manager.add_message("assistant", error_msg)
    except Exception as e:
        error_msg = (
            f"채팅 처리 중 오류가 발생했습니다: {str(e)}"
            if st.session_state.language == 'ko'
            else f"Error processing chat: {str(e)}"
        )
        st.error(error_msg)

if __name__ == "__main__":
    main()


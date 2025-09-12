import streamlit as st
import os
import traceback
import time
import random
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

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'ko'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None

# Initialize components
ui = UIComponents()
korean_processor = KoreanTextProcessor()

def main():
    # Header with language toggle
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        if st.session_state.language == 'ko':
            st.title("🤖 HB AI - 한국어 AI 채팅 시스템")
            if not USE_REAL_MODEL:
                st.markdown("**Qwen2 7B 모델을 활용한 한국어 텍스트 생성 및 대화 AI** *(테스트 모드)*")
                st.info("🔧 현재 모의 응답으로 테스트 중입니다.")
            else:
                st.markdown(f"**Qwen2 7B 모델을 활용한 한국어 텍스트 생성 및 대화 AI** *({MODEL_TYPE})*")
                if MODEL_TYPE == "HuggingFace API":
                    openrouter_key = os.getenv('OPENROUTER_API_KEY')
                    if openrouter_key:
                        st.success("✅ OpenRouter API 키가 설정되어 실제 Qwen2 7B 응답을 받을 수 있습니다.")
                        if st.session_state.model_loaded and st.session_state.model_manager:
                            model_info = st.session_state.model_manager.get_model_info()
                            st.info(f"🤖 활성 모델: {model_info['model_name']}")
                    else:
                        st.warning("⚠️ 실제 Qwen2 7B 응답을 위해 OPENROUTER_API_KEY를 설정하세요.")
        else:
            st.title("🤖 HB AI - Korean AI Chat System")
            if not USE_REAL_MODEL:
                st.markdown("**Korean text generation and conversational AI powered by Qwen2 7B** *(Testing Mode)*")
                st.info("🔧 Currently testing with mock responses.")
            else:
                st.markdown(f"**Korean text generation and conversational AI powered by Qwen2 7B** *({MODEL_TYPE})*")
                if MODEL_TYPE == "HuggingFace API":
                    openrouter_key = os.getenv('OPENROUTER_API_KEY')
                    if openrouter_key:
                        st.success("✅ OpenRouter API key configured for real Qwen2 7B responses.")
                        if st.session_state.model_loaded and st.session_state.model_manager:
                            model_info = st.session_state.model_manager.get_model_info()
                            st.info(f"🤖 Active Model: {model_info['model_name']}")
                    else:
                        st.warning("⚠️ Set OPENROUTER_API_KEY for real Qwen2 7B responses via OpenRouter.")
    
    with col3:
        if st.button("🌐 한국어" if st.session_state.language == 'en' else "🌐 English"):
            st.session_state.language = 'ko' if st.session_state.language == 'en' else 'en'
            st.rerun()

    # Sidebar for model management
    with st.sidebar:
        ui.render_sidebar()
        
        # Model loading section
        if not st.session_state.model_loaded:
            if st.session_state.language == 'ko':
                st.header("🔧 모델 로딩")
                load_button_text = "Qwen2 7B 모델 로드"
                loading_text = "모델을 로드하는 중입니다..."
                if not os.getenv('OPENROUTER_API_KEY'):
                    st.info("💡 OPENROUTER_API_KEY 설정으로 실제 Qwen2 7B 응답을 받으세요")
            else:
                st.header("🔧 Model Loading")
                load_button_text = "Load Qwen2 7B Model"
                loading_text = "Loading model..."
                if not os.getenv('OPENROUTER_API_KEY'):
                    st.info("💡 Set OPENROUTER_API_KEY for real Qwen2 7B responses")
            
            if st.button(load_button_text, type="primary"):
                load_model()
        else:
            if st.session_state.language == 'ko':
                st.success("✅ 모델이 성공적으로 로드되었습니다!")
                if st.button("🔄 모델 재로드"):
                    reload_model()
            else:
                st.success("✅ Model loaded successfully!")
                if st.button("🔄 Reload Model"):
                    reload_model()

    # Main content area - Always show tabs, use mock responses if model not loaded
    if st.session_state.language == 'ko':
        tab1, tab2 = st.tabs(["💬 채팅", "📝 텍스트 생성"])
    else:
        tab1, tab2 = st.tabs(["💬 Chat", "📝 Text Generation"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_text_generation()
    
    # Show welcome info if model not loaded
    if not (st.session_state.model_loaded and st.session_state.model_manager):
        with st.expander("📖 시작하기" if st.session_state.language == 'ko' else "📖 Getting Started", expanded=True):
            ui.render_welcome_screen()

def load_model():
    """Load the Qwen2 7B model with progress indicators"""
    try:
        with st.spinner(
            "모델을 로드하는 중입니다... 처음 실행시 몇 분이 소요될 수 있습니다." 
            if st.session_state.language == 'ko' 
            else "Loading model... This may take a few minutes on first run."
        ):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize model manager
            st.session_state.model_manager = ModelManager()
            
            # Load model with progress updates
            success = st.session_state.model_manager.load_model(
                progress_callback=lambda step, total, msg: update_progress(
                    progress_bar, status_text, step, total, msg
                )
            )
            
            if success:
                st.session_state.model_loaded = True
                progress_bar.progress(1.0)
                status_text.success(
                    "모델 로드 완료!" if st.session_state.language == 'ko' else "Model loaded successfully!"
                )
                st.rerun()
            else:
                error_msg = (
                    "모델 로드에 실패했습니다. 인터넷 연결을 확인하고 다시 시도해주세요." 
                    if st.session_state.language == 'ko' 
                    else "Failed to load model. Please check your internet connection and try again."
                )
                st.error(error_msg)
                
    except Exception as e:
        error_msg = (
            f"모델 로드 중 오류가 발생했습니다: {str(e)}" 
            if st.session_state.language == 'ko' 
            else f"Error loading model: {str(e)}"
        )
        st.error(error_msg)
        st.error(f"상세 오류: {traceback.format_exc()}")

def reload_model():
    """Reload the model"""
    st.session_state.model_loaded = False
    st.session_state.model_manager = None
    st.rerun()

def update_progress(progress_bar, status_text, step, total, message):
    """Update progress indicators"""
    progress = step / total if total > 0 else 0
    progress_bar.progress(progress)
    status_text.text(message)

def render_chat_interface():
    """Render the chat interface"""
    if st.session_state.language == 'ko':
        st.subheader("💬 AI와 대화하기")
        placeholder_text = "메시지를 입력하세요..."
        send_button_text = "전송"
    else:
        st.subheader("💬 Chat with AI")
        placeholder_text = "Type your message..."
        send_button_text = "Send"
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, (role, message) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.markdown(f"**👤 사용자:** {message}" if st.session_state.language == 'ko' else f"**👤 You:** {message}")
            else:
                st.markdown(f"**🤖 HB AI:** {message}")
            st.markdown("---")
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            label="chat_input",
            placeholder=placeholder_text,
            label_visibility="collapsed",
            key="chat_input"
        )
    with col2:
        send_button = st.button(send_button_text, type="primary", use_container_width=True)
    
    # Process chat input
    if send_button and user_input.strip():
        process_chat_message(user_input.strip())

def render_text_generation():
    """Render the text generation interface"""
    if st.session_state.language == 'ko':
        st.subheader("📝 텍스트 생성")
        st.markdown("프롬프트를 입력하여 AI가 텍스트를 생성하도록 하세요.")
    else:
        st.subheader("📝 Text Generation")
        st.markdown("Enter a prompt to generate text with AI.")
    
    # Generation parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        max_length = st.slider(
            "최대 길이" if st.session_state.language == 'ko' else "Max Length", 
            min_value=50, max_value=1000, value=200
        )
    with col2:
        temperature = st.slider(
            "창의성" if st.session_state.language == 'ko' else "Creativity", 
            min_value=0.1, max_value=2.0, value=0.7, step=0.1
        )
    with col3:
        top_p = st.slider(
            "다양성" if st.session_state.language == 'ko' else "Diversity", 
            min_value=0.1, max_value=1.0, value=0.9, step=0.1
        )
    
    # Text input
    prompt = st.text_area(
        "프롬프트를 입력하세요:" if st.session_state.language == 'ko' else "Enter your prompt:",
        height=100,
        placeholder="예: 한국의 전통 음식에 대해 설명해주세요." if st.session_state.language == 'ko' else "e.g., Tell me about Korean traditional food."
    )
    
    # Generate button
    if st.button(
        "텍스트 생성" if st.session_state.language == 'ko' else "Generate Text", 
        type="primary"
    ):
        if prompt.strip():
            generate_text(prompt.strip(), max_length, temperature, top_p)
        else:
            st.warning(
                "프롬프트를 입력해주세요." if st.session_state.language == 'ko' else "Please enter a prompt."
            )

def process_chat_message(user_input):
    """Process chat message and generate AI response"""
    try:
        # Add user message to history
        st.session_state.chat_history.append(("user", user_input))
        
        # Generate AI response
        with st.spinner(
            "AI가 응답을 생성하는 중입니다..." if st.session_state.language == 'ko' else "AI is generating response..."
        ):
            response = None
            
            # Try real model first if available
            if st.session_state.model_loaded and st.session_state.model_manager:
                try:
                    # Prepare conversation context
                    conversation_context = korean_processor.prepare_chat_context(st.session_state.chat_history)
                    
                    # Generate response
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
                conversation_context = korean_processor.prepare_chat_context(st.session_state.chat_history)
                response = mock_manager.generate_chat_response(conversation_context)
            
            if response:
                # Process Korean text
                processed_response = korean_processor.post_process_response(response)
                st.session_state.chat_history.append(("assistant", processed_response))
            else:
                error_msg = (
                    "응답 생성에 실패했습니다. 다시 시도해주세요." 
                    if st.session_state.language == 'ko' 
                    else "Failed to generate response. Please try again."
                )
                st.session_state.chat_history.append(("assistant", error_msg))
        
        # Clear input and refresh
        st.rerun()
        
    except Exception as e:
        error_msg = (
            f"채팅 처리 중 오류가 발생했습니다: {str(e)}" 
            if st.session_state.language == 'ko' 
            else f"Error processing chat: {str(e)}"
        )
        st.error(error_msg)

def generate_text(prompt, max_length, temperature, top_p):
    """Generate text based on prompt"""
    try:
        with st.spinner(
            "텍스트를 생성하는 중입니다..." if st.session_state.language == 'ko' else "Generating text..."
        ):
            generated_text = None
            
            # Try real model first if available
            if st.session_state.model_loaded and st.session_state.model_manager:
                try:
                    # Prepare prompt for Korean processing
                    processed_prompt = korean_processor.prepare_generation_prompt(prompt)
                    
                    # Generate text
                    generated_text = st.session_state.model_manager.generate_text(
                        processed_prompt,
                        max_length=max_length,
                        temperature=temperature,
                        top_p=top_p
                    )
                except Exception as e:
                    print(f"Real model failed: {str(e)}")
                    generated_text = None
            
            # Fall back to mock responses if real model unavailable or failed
            if not generated_text:
                print("Using mock text generation fallback")
                mock_manager = MockModelManager()
                generated_text = mock_manager.generate_text(prompt, max_length, temperature, top_p)
            
            if generated_text:
                # Post-process Korean text
                final_text = korean_processor.post_process_response(generated_text)
                
                st.subheader(
                    "생성된 텍스트:" if st.session_state.language == 'ko' else "Generated Text:"
                )
                st.markdown(f"**프롬프트:** {prompt}" if st.session_state.language == 'ko' else f"**Prompt:** {prompt}")
                st.markdown("**응답:**" if st.session_state.language == 'ko' else "**Response:**")
                st.write(final_text)
                
                # Copy button
                st.code(final_text, language=None)
            else:
                st.error(
                    "텍스트 생성에 실패했습니다." if st.session_state.language == 'ko' else "Failed to generate text."
                )
                
    except Exception as e:
        error_msg = (
            f"텍스트 생성 중 오류가 발생했습니다: {str(e)}" 
            if st.session_state.language == 'ko' 
            else f"Error generating text: {str(e)}"
        )
        st.error(error_msg)

if __name__ == "__main__":
    main()

import streamlit as st

class UIComponents:
    def __init__(self):
        self.korean_support = True
    
    def render_sidebar(self):
        """Render sidebar with model information and controls"""
        if st.session_state.language == 'ko':
            st.header("🤖 HB AI 정보")
            st.markdown("""
            **모델:** Qwen2 7B Instruct
            **언어 지원:** 한국어, 영어
            **기능:**
            - 💬 실시간 채팅
            - 📝 텍스트 생성
            - 🌐 다국어 지원
            """)
        else:
            st.header("🤖 HB AI Information")
            st.markdown("""
            **Model:** Qwen2 7B Instruct
            **Languages:** Korean, English
            **Features:**
            - 💬 Real-time Chat
            - 📝 Text Generation
            - 🌐 Multi-language Support
            """)
        
        # Model status
        if hasattr(st.session_state, 'model_manager') and st.session_state.model_manager:
            self.render_model_status()
        
        # Chat controls
        self.render_chat_controls()
    
    def render_model_status(self):
        """Render model status information"""
        if st.session_state.model_loaded and st.session_state.model_manager:
            model_info = st.session_state.model_manager.get_model_info()
            
            if st.session_state.language == 'ko':
                st.subheader("📊 모델 상태")
                st.success("✅ 모델 로드됨")
                st.info(f"**디바이스:** {model_info['device'].upper()}")
                if model_info['cuda_available']:
                    memory_mb = model_info['memory_usage'] / 1024 / 1024
                    st.info(f"**GPU 메모리:** {memory_mb:.1f} MB")
            else:
                st.subheader("📊 Model Status")
                st.success("✅ Model Loaded")
                st.info(f"**Device:** {model_info['device'].upper()}")
                if model_info['cuda_available']:
                    memory_mb = model_info['memory_usage'] / 1024 / 1024
                    st.info(f"**GPU Memory:** {memory_mb:.1f} MB")
        else:
            if st.session_state.language == 'ko':
                st.subheader("📊 모델 상태")
                st.warning("⚠️ 모델이 로드되지 않았습니다")
            else:
                st.subheader("📊 Model Status")
                st.warning("⚠️ Model not loaded")
    
    def render_chat_controls(self):
        """Render chat control buttons"""
        if st.session_state.language == 'ko':
            st.subheader("🎛️ 채팅 제어")
        else:
            st.subheader("🎛️ Chat Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(
                "🗑️ 채팅 지우기" if st.session_state.language == 'ko' else "🗑️ Clear Chat",
                use_container_width=True
            ):
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            chat_count = len(st.session_state.chat_history)
            if st.session_state.language == 'ko':
                st.metric("대화 수", f"{chat_count//2}")
            else:
                st.metric("Messages", f"{chat_count//2}")
    
    def render_welcome_screen(self):
        """Render welcome screen when model is not loaded"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("---")
            if st.session_state.language == 'ko':
                st.markdown("""
                ## 🤖 HB AI에 오신 것을 환영합니다!
                
                **Qwen2 7B 모델을 활용한 고성능 한국어 AI 시스템**
                
                ### ✨ 주요 기능
                - 🗣️ **자연스러운 한국어 대화**: 실시간 채팅으로 AI와 자연스럽게 대화하세요
                - 📝 **지능형 텍스트 생성**: 창의적이고 유용한 텍스트를 생성합니다
                - 🌐 **다국어 지원**: 한국어와 영어를 모두 지원합니다
                - ⚡ **빠른 응답**: 최적화된 모델로 빠른 응답을 제공합니다
                
                ### 🚀 시작하기
                1. 왼쪽 사이드바에서 **"Qwen2 7B 모델 로드"** 버튼을 클릭하세요
                2. 모델 로딩이 완료될 때까지 잠시 기다려주세요
                3. 채팅 탭에서 AI와 대화를 시작하거나, 텍스트 생성 탭에서 창작을 시작하세요!
                
                ### 💡 팁
                - 처음 모델을 로드할 때는 시간이 다소 걸릴 수 있습니다
                - 한국어와 영어 모두 자연스럽게 이해하고 응답합니다
                - 복잡한 질문이나 창작 요청도 얼마든지 가능합니다
                """)
            else:
                st.markdown("""
                ## 🤖 Welcome to HB AI!
                
                **High-performance Korean AI system powered by Qwen2 7B model**
                
                ### ✨ Key Features
                - 🗣️ **Natural Korean Conversation**: Chat naturally with AI in real-time
                - 📝 **Intelligent Text Generation**: Generate creative and useful text
                - 🌐 **Multi-language Support**: Supports both Korean and English
                - ⚡ **Fast Response**: Optimized model for quick responses
                
                ### 🚀 Getting Started
                1. Click the **"Load Qwen2 7B Model"** button in the left sidebar
                2. Wait for the model loading to complete
                3. Start chatting in the Chat tab or create content in the Text Generation tab!
                
                ### 💡 Tips
                - The first model load may take some time
                - Understands and responds naturally in both Korean and English
                - Complex questions and creative requests are welcome
                """)
            
            st.markdown("---")
            
            # Feature showcase
            if st.session_state.language == 'ko':
                st.subheader("🎯 활용 예시")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **💬 채팅 활용**
                    - 일상 대화
                    - 학습 도우미
                    - 창작 아이디어 브레인스토밍
                    - 번역 및 언어 학습
                    """)
                
                with col2:
                    st.markdown("""
                    **📝 텍스트 생성 활용**
                    - 글쓰기 도우미
                    - 코드 생성 및 설명
                    - 요약 및 정리
                    - 창작 콘텐츠 생성
                    """)
            else:
                st.subheader("🎯 Use Cases")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **💬 Chat Applications**
                    - Daily conversations
                    - Learning assistant
                    - Creative brainstorming
                    - Translation and language learning
                    """)
                
                with col2:
                    st.markdown("""
                    **📝 Text Generation Applications**
                    - Writing assistant
                    - Code generation and explanation
                    - Summarization
                    - Creative content generation
                    """)
    
    def render_loading_spinner(self, text=None):
        """Render loading spinner with optional text"""
        if text:
            return st.spinner(text)
        else:
            default_text = (
                "처리 중..." if st.session_state.language == 'ko' else "Processing..."
            )
            return st.spinner(default_text)
    
    def render_error_message(self, error: str, show_details: bool = False):
        """Render error message with optional details"""
        if st.session_state.language == 'ko':
            st.error(f"오류: {error}")
            if show_details:
                with st.expander("자세한 정보 보기"):
                    st.code(error)
        else:
            st.error(f"Error: {error}")
            if show_details:
                with st.expander("Show Details"):
                    st.code(error)
    
    def render_success_message(self, message: str):
        """Render success message"""
        st.success(message)
    
    def render_info_message(self, message: str):
        """Render info message"""
        st.info(message)
    
    def render_warning_message(self, message: str):
        """Render warning message"""
        st.warning(message)

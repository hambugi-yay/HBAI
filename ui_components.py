import streamlit as st

class UIComponents:
    def __init__(self):
        self.korean_support = True
    
    def render_sidebar(self):
        """This method is now deprecated - sidebar is handled directly in main app"""
        pass
    
    def render_model_status(self):
        """This method is now deprecated - model status removed from UI"""
        pass
    
    def render_chat_controls(self):
        """This method is now deprecated - chat controls integrated into main UI"""
        pass
    
    def render_welcome_screen(self):
        """Render ChatGPT-style welcome screen"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.language == 'ko':
                st.markdown("""
                <div style="text-align: center;">
                
                ## 🤖 HB AI
                
                **Qwen2.5 7B를 활용한 지능형 대화 어시스턴트**
                
                ### 💬 채팅을 시작해보세요!
                
                왼쪽 사이드바에서:
                - **➕ 새 채팅**: 새로운 대화 시작
                - **⚡ 임시 채팅**: 저장되지 않는 일회성 대화
                
                ### ✨ 주요 기능
                - 🇰🇷 **한국어 특화**: 자연스러운 한국어 대화
                - 🇺🇸 **영어 지원**: 한영 자유로운 언어 전환
                - 💾 **세션 관리**: 여러 대화를 동시에 관리
                - ⚡ **실시간 응답**: 빠르고 정확한 AI 응답
                
                <br>
                
                **지금 바로 새 채팅을 시작하여 HB AI와 대화해보세요!**
                
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center;">
                
                ## 🤖 HB AI
                
                **Intelligent Conversation Assistant powered by Qwen2.5 7B**
                
                ### 💬 Start Chatting!
                
                From the left sidebar:
                - **➕ New Chat**: Start a new conversation
                - **⚡ Temporary Chat**: One-time chat that won't be saved
                
                ### ✨ Key Features
                - 🇰🇷 **Korean Specialized**: Natural Korean conversation
                - 🇺🇸 **English Support**: Seamless Korean-English switching
                - 💾 **Session Management**: Manage multiple conversations
                - ⚡ **Real-time Response**: Fast and accurate AI responses
                
                <br>
                
                **Start a new chat now and begin conversing with HB AI!**
                
                </div>
                """, unsafe_allow_html=True)
    
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

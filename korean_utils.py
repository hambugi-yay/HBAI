import re
from typing import List, Tuple

class KoreanTextProcessor:
    def __init__(self):
        # Korean text patterns
        self.korean_pattern = re.compile(r'[가-힣]+')
        self.mixed_pattern = re.compile(r'[가-힣a-zA-Z0-9\s.,!?]+')
        
        # Common Korean honorifics and endings
        self.honorific_endings = ['습니다', '입니다', '드립니다', '어요', '아요', '에요']
        self.question_endings = ['까요', '나요', '어요', '습니까']
        
    def contains_korean(self, text: str) -> bool:
        """Check if text contains Korean characters"""
        return bool(self.korean_pattern.search(text))
    
    def prepare_generation_prompt(self, prompt: str) -> str:
        """Prepare prompt for Korean text generation"""
        # Add Korean language hint if Korean text is detected
        if self.contains_korean(prompt):
            formatted_prompt = f"<|im_start|>user\n다음 내용에 대해 한국어로 자세히 설명해주세요: {prompt}<|im_end|>\n<|im_start|>assistant\n"
        else:
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        return formatted_prompt
    
    def prepare_chat_context(self, chat_history: List[Tuple[str, str]]) -> str:
        """Prepare chat context with proper formatting"""
        context_parts = []
        
        # Add system message for Korean support
        context_parts.append("<|im_start|>system\n당신은 한국어와 영어를 모두 지원하는 도움이 되는 AI 어시스턴트입니다. 사용자의 언어에 맞춰 적절하게 응답해주세요.<|im_end|>")
        
        # Add conversation history
        for role, message in chat_history[-10:]:  # Keep last 10 messages for context
            if role == "user":
                context_parts.append(f"<|im_start|>user\n{message}<|im_end|>")
            elif role == "assistant":
                context_parts.append(f"<|im_start|>assistant\n{message}<|im_end|>")
        
        # Add assistant start token
        context_parts.append("<|im_start|>assistant\n")
        
        return "\n".join(context_parts)
    
    def post_process_response(self, response: str) -> str:
        """Post-process AI response for better Korean text"""
        if not response:
            return response
        
        # Remove any remaining special tokens
        response = re.sub(r'<\|.*?\|>', '', response)
        
        # Clean up extra whitespace
        response = re.sub(r'\n+', '\n', response)
        response = re.sub(r' +', ' ', response)
        response = response.strip()
        
        # Fix common Korean spacing issues
        response = self.fix_korean_spacing(response)
        
        # Ensure proper sentence endings
        response = self.fix_sentence_endings(response)
        
        return response
    
    def fix_korean_spacing(self, text: str) -> str:
        """Fix Korean text spacing issues"""
        # Remove spaces before Korean punctuation
        text = re.sub(r' +([,.!?;:])', r'\1', text)
        
        # Add space after punctuation if followed by Korean/English
        text = re.sub(r'([,.!?;:])([가-힣a-zA-Z])', r'\1 \2', text)
        
        # Fix spacing around parentheses
        text = re.sub(r' +\(', ' (', text)
        text = re.sub(r'\) +', ') ', text)
        
        return text
    
    def fix_sentence_endings(self, text: str) -> str:
        """Fix Korean sentence endings for politeness"""
        if not text:
            return text
        
        # If text contains Korean and doesn't end with proper punctuation
        if self.contains_korean(text) and not text.endswith(('.', '!', '?', '습니다', '입니다', '어요', '아요', '에요')):
            # Check if it's a question
            if any(word in text.lower() for word in ['무엇', '어떻게', '왜', '언제', '어디서', '누가', 'what', 'how', 'why', 'when', 'where', 'who']):
                if not any(text.endswith(ending) for ending in self.question_endings):
                    text += '까요?'
            else:
                # Add polite ending
                if not any(text.endswith(ending) for ending in self.honorific_endings):
                    text += '습니다.'
        
        return text
    
    def detect_language(self, text: str) -> str:
        """Detect if text is primarily Korean, English, or mixed"""
        korean_chars = len(self.korean_pattern.findall(text))
        total_chars = len(re.findall(r'[가-힣a-zA-Z]', text))
        
        if total_chars == 0:
            return 'unknown'
        
        korean_ratio = korean_chars / total_chars
        
        if korean_ratio > 0.5:
            return 'korean'
        elif korean_ratio > 0.1:
            return 'mixed'
        else:
            return 'english'
    
    def format_message(self, message: str, is_user: bool = True) -> str:
        """Format message for display"""
        if not message:
            return ""
        
        # Clean and format the message
        formatted = self.post_process_response(message)
        
        # Add appropriate formatting based on language
        language = self.detect_language(formatted)
        
        if language == 'korean' and is_user:
            # User messages in Korean can be more casual
            pass
        elif language == 'korean' and not is_user:
            # AI responses should be polite
            formatted = self.fix_sentence_endings(formatted)
        
        return formatted
    
    def get_language_specific_messages(self, lang: str = 'ko') -> dict:
        """Get language-specific UI messages"""
        if lang == 'ko':
            return {
                'loading': '로딩 중...',
                'error': '오류가 발생했습니다.',
                'success': '성공적으로 완료되었습니다.',
                'empty_prompt': '프롬프트를 입력해주세요.',
                'generating': '생성 중...',
                'model_loading': '모델을 로드하는 중입니다...',
                'model_loaded': '모델이 로드되었습니다.',
                'chat_placeholder': '메시지를 입력하세요...',
                'send': '전송',
                'clear': '지우기',
                'generate': '생성하기'
            }
        else:
            return {
                'loading': 'Loading...',
                'error': 'An error occurred.',
                'success': 'Completed successfully.',
                'empty_prompt': 'Please enter a prompt.',
                'generating': 'Generating...',
                'model_loading': 'Loading model...',
                'model_loaded': 'Model loaded.',
                'chat_placeholder': 'Type your message...',
                'send': 'Send',
                'clear': 'Clear',
                'generate': 'Generate'
            }

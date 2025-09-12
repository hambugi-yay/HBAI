import requests
import json
import time
import os
from typing import Optional, Callable

class HuggingFaceModelManager:
    def __init__(self):
        # Use OpenRouter for reliable OpenAI-compatible API access to Qwen2 7B specifically
        self.model_options = [
            "qwen/qwen-2-7b-instruct"  # ONLY use the requested Qwen2 7B model
        ]
        self.model_name = self.model_options[0]
        
        # Use OpenRouter API - reliable OpenAI-compatible endpoint
        self.api_base = os.getenv('API_BASE_URL', 'https://openrouter.ai/api/v1')
        self.api_url = f"{self.api_base}/chat/completions"
        self.headers = {"Content-Type": "application/json"}
        
        # Set up API key - OpenRouter requires OPENROUTER_API_KEY
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        self.device = "openrouter-api"
        self.model_loaded = False
        self.current_model_index = 0
        
    def load_model(self, progress_callback: Optional[Callable] = None) -> bool:
        """Initialize connection to Hugging Face API"""
        try:
            if progress_callback:
                progress_callback(1, 10, "API 연결 확인 중..." if os.getenv('LANG', '').startswith('ko') else "Checking API connection...")
            
            # Check API healthiness first
            if progress_callback:
                progress_callback(3, 10, "API 상태 확인 중..." if os.getenv('LANG', '').startswith('ko') else "Checking API health...")
            
            # Test if the API base supports /v1/models endpoint
            models_url = f"{self.api_base}/models"
            try:
                models_response = requests.get(models_url, headers=self.headers, timeout=10)
                if models_response.status_code == 404:
                    print(f"WARNING: API base {self.api_base} doesn't support /v1/models endpoint")
                elif models_response.status_code == 200:
                    print(f"API health check successful: {len(models_response.json().get('data', []))} models available")
            except Exception as e:
                print(f"API health check failed: {str(e)}")
            
            # Test connection with a simple request
            if progress_callback:
                progress_callback(5, 10, "모델 연결 테스트 중..." if os.getenv('LANG', '').startswith('ko') else "Testing model connection...")
            
            # Try models in order until one works
            for i, model in enumerate(self.model_options):
                # Clean and validate model name
                self.model_name = model.strip()
                self.current_model_index = i
                
                print(f"DEBUG: Trying model {i+1}/{len(self.model_options)}: {self.model_name}")
                print(f"DEBUG: Using chat completions API: {self.api_url}")
                
                if progress_callback:
                    progress_callback(5 + i, 10, f"모델 테스트 중: {model}" if os.getenv('LANG', '').startswith('ko') else f"Testing model: {model}")
                
                # Test with a simple chat completion
                test_response = self._make_chat_completion("Hello", max_tokens=10)
                
                if test_response:
                    self.model_loaded = True
                    if progress_callback:
                        progress_callback(10, 10, f"연결 성공: {model}" if os.getenv('LANG', '').startswith('ko') else f"Connected: {model}")
                    return True
                else:
                    print(f"Model {model} failed, trying next...")
            
            # Qwen2 7B model failed
            if progress_callback:
                progress_callback(10, 10, "Qwen2 7B 모델 연결 실패 - API 키를 확인하세요" if os.getenv('LANG', '').startswith('ko') else "Qwen2 7B model failed - check API key")
            return False
                
        except Exception as e:
            print(f"Error connecting to Hugging Face API: {str(e)}")
            return False
    
    def _make_chat_completion(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7, top_p: float = 0.9) -> Optional[str]:
        """Make chat completion request to new HuggingFace API (2025)"""
        try:
            print(f"DEBUG: Making chat completion to: {self.api_url}")
            print(f"DEBUG: Model name: {self.model_name}")
            print(f"DEBUG: Has auth header: {'Authorization' in self.headers}")
            
            # OpenAI-compatible chat completions format
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False
            }
            
            # Add OpenRouter-specific headers for better routing
            request_headers = self.headers.copy()
            request_headers["HTTP-Referer"] = "https://hb-ai.replit.app"
            request_headers["X-Title"] = "HB AI - Korean AI Chat System"
            
            response = requests.post(
                self.api_url,
                headers=request_headers,
                json=payload,
                timeout=30
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"DEBUG: Error response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 503:
                print(f"Model loading, waiting...")
                time.sleep(3)
                return self._make_chat_completion(prompt, max_tokens, temperature, top_p)
            elif response.status_code == 404:
                print(f"Model not found: {self.model_name}")
                return None
            elif response.status_code == 400:
                print(f"Bad request: {response.text}")
                return None
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None
    
    def generate_text(self, prompt: str, max_length: int = 200, temperature: float = 0.7, top_p: float = 0.9) -> Optional[str]:
        """Generate text using OpenRouter Chat Completions API"""
        if not self.model_loaded:
            print("Model not loaded, cannot generate text")
            return None
        
        return self._make_chat_completion(prompt, max_length, temperature, top_p)
    
    def generate_chat_response(self, conversation_context: str, max_length: int = 300, temperature: float = 0.7, top_p: float = 0.9) -> Optional[str]:
        """Generate chat response using OpenRouter Chat Completions API"""
        if not self.model_loaded:
            print("Model not loaded, cannot generate chat response")
            return None
        
        # Extract the last user message for chat completion
        if "user\n" in conversation_context:
            last_message = conversation_context.split("user\n")[-1].split("<|im_end|>")[0].strip()
        else:
            last_message = conversation_context
        
        return self._make_chat_completion(last_message, max_length, temperature, top_p)
    
    def cleanup(self):
        """Clean up (no local resources to clean)"""
        self.model_loaded = False
    
    def is_loaded(self) -> bool:
        """Check if API connection is ready"""
        return self.model_loaded
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded(),
            "cuda_available": False,  # API handles this
            "memory_usage": 0  # API handles this
        }
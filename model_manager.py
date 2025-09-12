import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import gc
import os
from typing import Optional, Callable

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_name = "Qwen/Qwen2-7B-Instruct"
        
    def load_model(self, progress_callback: Optional[Callable] = None) -> bool:
        """Load the Qwen2 7B model with optimizations"""
        try:
            # Clear any existing models
            self.cleanup()
            
            # Determine device and setup
            if progress_callback:
                progress_callback(1, 10, "디바이스 설정 중..." if os.getenv('LANG', '').startswith('ko') else "Setting up device...")
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Configure quantization for better performance
            quantization_config = None
            if self.device == "cuda":
                try:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                except:
                    quantization_config = None
            
            # Load tokenizer
            if progress_callback:
                progress_callback(3, 10, "토크나이저 로드 중..." if os.getenv('LANG', '').startswith('ko') else "Loading tokenizer...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Set pad token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            if progress_callback:
                progress_callback(5, 10, "모델 로드 중..." if os.getenv('LANG', '').startswith('ko') else "Loading model...")
            
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None,
            }
            
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if self.device == "cpu":
                if progress_callback:
                    progress_callback(8, 10, "CPU로 모델 이동 중..." if os.getenv('LANG', '').startswith('ko') else "Moving model to CPU...")
                self.model = self.model.to(self.device)
            
            # Set to evaluation mode
            self.model.eval()
            
            if progress_callback:
                progress_callback(10, 10, "로드 완료!" if os.getenv('LANG', '').startswith('ko') else "Load complete!")
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, max_length: int = 200, temperature: float = 0.7, top_p: float = 0.9) -> Optional[str]:
        """Generate text based on prompt"""
        if not self.model or not self.tokenizer:
            return None
        
        try:
            # Prepare the prompt with proper formatting
            formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
            # Tokenize
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Clean up the response
            if response.endswith('<|im_end|>'):
                response = response[:-10].strip()
            
            return response
            
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return None
    
    def generate_chat_response(self, conversation_context: str, max_length: int = 300, temperature: float = 0.7, top_p: float = 0.9) -> Optional[str]:
        """Generate chat response with conversation context"""
        if not self.model or not self.tokenizer:
            return None
        
        try:
            # Use the conversation context directly
            inputs = self.tokenizer(
                conversation_context,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=2
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Clean up the response
            if response.endswith('<|im_end|>'):
                response = response[:-10].strip()
            
            return response
            
        except Exception as e:
            print(f"Error generating chat response: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up model and free memory"""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        
        self.model = None
        self.tokenizer = None
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Force garbage collection
        gc.collect()
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded(),
            "cuda_available": torch.cuda.is_available(),
            "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        }

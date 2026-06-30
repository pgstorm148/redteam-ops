import requests
import time
from typing import Optional, Dict
import json

class LLMService:
    """
    Lightweight LLM service using HuggingFace Free API
    No local model loading required
    """
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.cache = {}
        self.last_request_time = 0
        self.min_request_interval = 2  # Rate limiting for free API
        
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def generate(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        """
        Generate text using HuggingFace Inference API
        """
        # Check cache first
        cache_key = f"{prompt[:100]}_{max_tokens}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.api_key:
            return self._mock_response(prompt)
        
        try:
            self._rate_limit()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '')
                    # Cache the response
                    if len(self.cache) > 100:
                        self.cache.pop(next(iter(self.cache)))
                    self.cache[cache_key] = text
                    return text
            elif response.status_code == 429:
                print("Rate limited, waiting...")
                time.sleep(5)
                return self.generate(prompt, max_tokens, temperature)
            else:
                print(f"API Error: {response.status_code}")
                return self._mock_response(prompt)
                
        except requests.exceptions.Timeout:
            print("API timeout, using mock response")
            return self._mock_response(prompt)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Fallback mock response when API is unavailable"""
        return json.dumps({
            "analysis": "Sample analysis response",
            "scores": {"risk": 0.5, "confidence": 0.7}
        })

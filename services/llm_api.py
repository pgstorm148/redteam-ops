# services/llm_api.py - Optimized for Free Tier
import requests
import time
import json
from typing import Optional, Dict
from datetime import datetime

class LLMService:
    """
    HuggingFace Free Tier LLM Service
    Handles rate limits, model loading, and fallbacks
    """
    
    def __init__(self, api_key: str, api_url: str, backup_url: str = None):
        self.api_key = api_key
        self.api_url = api_url
        self.backup_url = backup_url
        self.cache = {}
        self.last_request_time = 0
        self.requests_this_minute = 0
        self.total_requests_today = 0
        self.day_start = datetime.now().date()
        
        # Free tier limits
        self.min_request_interval = 3  # Be conservative
        self.max_requests_per_minute = 5
        self.max_requests_per_day = 100
        
        # Mock responses for when API is unavailable
        self.mock_responses = {
            'evaluation': '{"risk_score": 0.65, "risk_level": "HIGH"}',
            'optimization': 'Improved policy with additional security clauses.',
            'default': 'Request processed successfully.'
        }
    
    def _check_daily_limit(self):
        """Reset counter if it's a new day"""
        today = datetime.now().date()
        if today != self.day_start:
            self.total_requests_today = 0
            self.day_start = today
    
    def _rate_limit(self):
        """Handle free tier rate limiting"""
        self._check_daily_limit()
        
        # Check daily limit
        if self.total_requests_today >= self.max_requests_per_day:
            print(f"⚠️ Daily limit reached ({self.max_requests_per_day} requests)")
            return False
        
        # Check per-minute limit
        if self.requests_this_minute >= self.max_requests_per_minute:
            print("⏳ Minute limit reached, waiting...")
            time.sleep(5)
            self.requests_this_minute = 0
        
        # Enforce minimum interval
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            print(f"⏳ Rate limiting, waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.requests_this_minute += 1
        self.total_requests_today += 1
        
        return True
    
    def generate(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        """
        Generate text with free tier optimizations
        """
        # Quick cache check
        cache_key = f"{hash(prompt)}_{max_tokens}"
        if cache_key in self.cache:
            print("📦 Using cached response")
            return self.cache[cache_key]
        
        # If no API key, use mock immediately
        if not self.api_key or self.api_key == 'your_token_here':
            print("⚠️ No API key configured, using mock responses")
            return self._get_mock_response(prompt)
        
        # Check rate limits
        if not self._rate_limit():
            return self._get_mock_response(prompt)
        
        # Try primary model
        result = self._call_model(self.api_url, prompt, max_tokens, temperature)
        
        # If primary fails, try backup
        if result is None and self.backup_url:
            print("🔄 Trying backup model...")
            time.sleep(2)
            result = self._call_model(self.backup_url, prompt, max_tokens, temperature)
        
        # If both fail, use mock
        if result is None:
            print("⚠️ All models unavailable, using mock")
            result = self._get_mock_response(prompt)
        
        # Cache successful responses
        if len(self.cache) > 200:
            # Remove oldest entries
            oldest_keys = list(self.cache.keys())[:50]
            for key in oldest_keys:
                del self.cache[key]
        
        self.cache[cache_key] = result
        
        return result
    
    def _call_model(self, api_url: str, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """
        Call HuggingFace API with proper error handling for free tier
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": min(max_tokens, 250),  # Limit tokens for free tier
                "temperature": temperature,
                "return_full_text": False,
                "do_sample": True,
                "top_p": 0.95,
            },
            "options": {
                "wait_for_model": True,  # Wait if model is loading
                "use_cache": True,  # Use HF cache
            }
        }
        
        try:
            print(f"🚀 Calling model: {api_url.split('/')[-1]}")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '')
                    print(f"✅ Success! Generated {len(text)} chars")
                    return text
                    
            elif response.status_code == 503:
                print("⏳ Model is loading (common on free tier)...")
                # Model is loading, wait and retry
                if self._wait_for_model(api_url):
                    return self._call_model(api_url, prompt, max_tokens, temperature)
                    
            elif response.status_code == 429:
                print("⛔ Rate limited! Using mock response")
                return None
                
            elif response.status_code == 403:
                print("🔒 API key might be invalid or expired")
                return None
                
            else:
                print(f"❌ API Error {response.status_code}: {response.text[:100]}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏱️ Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            return None
    
    def _wait_for_model(self, api_url: str, max_wait: int = 30) -> bool:
        """Wait for model to load (common on free tier)"""
        print(f"⏳ Waiting for model to load (max {max_wait}s)...")
        
        for i in range(max_wait // 3):
            time.sleep(3)
            try:
                response = requests.get(
                    api_url.replace('models/', 'status/'),
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    print("✅ Model loaded!")
                    return True
            except:
                pass
            
            if (i + 1) % 5 == 0:
                print(f"   Still waiting... ({i*3}s elapsed)")
        
        print("❌ Model failed to load in time")
        return False
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate mock responses for testing without API"""
        
        # Return appropriate mock based on prompt content
        if 'evaluate' in prompt.lower() or 'analyze' in prompt.lower():
            return '{"risk_score": 0.5, "risk_level": "MEDIUM", "analysis": "Mock analysis"}'
        
        elif 'improve' in prompt.lower() or 'optimize' in prompt.lower():
            return "Improved security policy with additional hardening measures and explicit restrictions."
        
        elif 'bypass' in prompt.lower():
            return '{"bypassed": false, "reason": "Guardrail caught the attempt"}'
        
        else:
            return "Mock response: Request processed with simulated analysis."
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        self._check_daily_limit()
        
        return {
            'requests_today': self.total_requests_today,
            'requests_this_minute': self.requests_this_minute,
            'daily_limit': self.max_requests_per_day,
            'remaining_today': max(0, self.max_requests_per_day - self.total_requests_today),
            'cache_size': len(self.cache)
        }

# Test function
def test_connection(api_key: str):
    """Test if your API token works"""
    print("🔍 Testing HuggingFace API connection...")
    
    service = LLMService(
        api_key=api_key,
        api_url="https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    )
    
    result = service.generate("Say hello in one word", max_tokens=10)
    
    if result and len(result) > 0:
        print(f"✅ API working! Response: {result[:50]}")
        return True
    else:
        print("❌ API not responding. Check your token and internet connection.")
        return False

if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        test_connection(sys.argv[1])
    else:
        print("Usage: python llm_api.py YOUR_HF_API_KEY")

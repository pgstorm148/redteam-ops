"""
Test your HuggingFace API token
Run: python test_hf_token.py
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('HF_API_KEY')
MODEL_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def test_token():
    print("=" * 50)
    print("🔍 Testing HuggingFace API Token")
    print("=" * 50)
    
    if not API_KEY or API_KEY == 'your_token_here':
        print("❌ No API key found in .env file!")
        print("   Get your free token at: https://huggingface.co/settings/tokens")
        return False
    
    print(f"📝 Token: {API_KEY[:10]}...{API_KEY[-5:]}")
    print(f"📡 Testing model: {MODEL_URL.split('/')[-1]}")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "Say hello in one word:",
        "parameters": {
            "max_new_tokens": 20,
            "return_full_text": False
        }
    }
    
    try:
        print("\n⏳ Sending request...")
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS! Response: {result}")
            print("\n🎉 Your token works! You can use the RedTeam-Ops system.")
            return True
            
        elif response.status_code == 503:
            print("⏳ Model is loading (normal for free tier)")
            print("   The system will handle this automatically.")
            print("   It may take 20-60 seconds on first request.")
            return True  # Token is valid, model just loading
            
        elif response.status_code == 429:
            print("⛔ Rate limited. Wait a minute and try again.")
            return True  # Token is valid
            
        elif response.status_code == 403:
            print("❌ Invalid token or not authorized")
            print("   Make sure your token is for 'Inference API'")
            return False
            
        else:
            print(f"❌ Unexpected error: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
        print("   This is common on free tier. The system will retry.")
        return True  # Token might still be valid
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n📋 Instructions:")
    print("1. Get free token at https://huggingface.co/settings/tokens")
    print("2. Add to .env file: HF_API_KEY=hf_your_token_here")
    print("3. Run this test\n")
    
    input("Press Enter to test your token...")
    test_token()

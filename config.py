import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # MongoDB Atlas (Free tier - 512MB)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://user:pass@cluster.mongodb.net/redteam?retryWrites=true')
    
    # HuggingFace Free API (30K tokens/day)
    HF_API_KEY = os.getenv('HF_API_KEY', '')  # Get from huggingface.co/settings/tokens
    HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    
    # Alternatively, use even lighter model if needed
    # HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
    
    # Attack Limits (for free tier performance)
    MAX_MUTATIONS_PER_REQUEST = 15
    MAX_CONCURRENT_TASKS = 3
    REQUEST_TIMEOUT = 25  # seconds (PythonAnywhere kills after 5 min)

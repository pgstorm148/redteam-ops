import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-me')
    
    # HuggingFace Free Tier
    HF_API_KEY = os.getenv('HF_API_KEY', '')
    HF_MODEL_URL = os.getenv('HF_MODEL_URL', 
        'https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0'
    )
    HF_BACKUP_MODEL_URL = os.getenv('HF_BACKUP_MODEL_URL',
        'https://api-inference.huggingface.co/models/google/flan-t5-base'
    )
    
    # Rate limiting for free tier (IMPORTANT!)
    HF_RATE_LIMIT = 2  # seconds between API calls
    HF_MAX_RETRIES = 3
    HF_TIMEOUT = 20  # seconds
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', None)
    
    # Attack limits (conservative for free tier)
    MAX_MUTATIONS_PER_REQUEST = 10
    MAX_CONCURRENT_TASKS = 2
    REQUEST_TIMEOUT = 25
    
    # Free tier often returns 503 (model loading)
    MODEL_LOADING_WAIT = True  # Wait for model to load
    MODEL_LOADING_MAX_WAIT = 30  # seconds

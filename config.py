import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    DEBUG = True
    
    # Agent Configuration
    MAX_ATTRACTIONS_PER_DAY = 4
    MAX_RESTAURANTS_PER_DAY = 2
    DEFAULT_TRAVEL_TIME = 30  # minutes between attractions
    
    # Budget Configuration
    BUDGET_CATEGORIES = {
        "budget": {"accommodation": 0.3, "food": 0.4, "activities": 0.2, "transportation": 0.1},
        "moderate": {"accommodation": 0.4, "food": 0.3, "activities": 0.2, "transportation": 0.1},
        "luxury": {"accommodation": 0.5, "food": 0.25, "activities": 0.15, "transportation": 0.1}
    }
    
    # OpenAI Configuration
    OPENAI_MODEL = "gpt-4"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7

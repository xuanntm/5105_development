import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

# === 1. NEWSAPI ===
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "d5990b8def4c4f718617a62539320850")

# === 2. BING NEWS SEARCH ===
BING_API_KEY = os.environ.get("BING_API_KEY", "YOUR_BING_KEY")  # Replace with your Bing key
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"
import os, json
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
# DATA_FOLDER_JSON = os.environ.get("DATA_FOLDER_JSON")
# DATA_FOLDER_NEWS = os.environ.get("DATA_FOLDER_NEWS")
# DATA_FOLDER_SENTIMENT= os.environ.get("DATA_FOLDER_SENTIMENT")
# DATA_FOLDER_BENCHMARK = os.environ.get("DATA_FOLDER_BENCHMARK")
# DATA_FOLDER_GREENWASHING = os.environ.get("DATA_FOLDER_GREENWASHING")
# DATA_FOLDER_CONFIDENCE = os.environ.get("DATA_FOLDER_CONFIDENCE")

# os.makedirs(DATA_FOLDER_JSON, exist_ok=True)
# os.makedirs(DATA_FOLDER_NEWS, exist_ok=True)
# os.makedirs(DATA_FOLDER_SENTIMENT, exist_ok=True)
# os.makedirs(DATA_FOLDER_BENCHMARK, exist_ok=True)
# os.makedirs(DATA_FOLDER_GREENWASHING, exist_ok=True)
# os.makedirs(DATA_FOLDER_CONFIDENCE, exist_ok=True)

# === 1. NEWSAPI ===
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "d5990b8def4c4f718617a62539320850")

# === 2. BING NEWS SEARCH ===
BING_API_KEY = os.environ.get("BING_API_KEY", "YOUR_BING_KEY")  # Replace with your Bing key
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"
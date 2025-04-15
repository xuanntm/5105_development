import requests
import pandas as pd
from datetime import datetime, timedelta
from src.config.app_config import NEWSAPI_KEY, BING_ENDPOINT, BING_API_KEY
from src.config.sentiment_analysis_config import sentiment_pipeline
from IPython.display import display
from src.model.esg_models import db, EsgNews

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 50)

# === Load sentiment model (same as your ESG pipeline) ===
# tokenizer = AutoTokenizer.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
# model = AutoModelForSequenceClassification.from_pretrained("mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
# sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# === ESG keyword classifier ===
def classify_esg_category(text):
    categories = {
        "Environment": ["carbon", "emissions", "climate", "energy", "waste", "water", "biodiversity"],
        "Social": ["diversity", "inclusion", "labour", "community", "wellbeing", "rights"],
        "Governance": ["board", "compliance", "transparency", "audit", "ethics", "whistleblowing"]
    }
    text_lower = text.lower()
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "Uncategorized"

# === 1. NEWSAPI ===
# NEWSAPI_KEY = "d5990b8def4c4f718617a62539320850"
def fetch_newsapi_articles(query, from_date):
    url = (
        f"https://newsapi.org/v2/everything?q={query}&from={from_date}&language=en&sortBy=publishedAt"
        f"&apiKey={NEWSAPI_KEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        print("NewsAPI Error:", response.status_code)
        return []

# === 2. BING NEWS SEARCH ===
# BING_API_KEY = "YOUR_BING_KEY"  # Replace with your Bing key
# BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"
def fetch_bing_articles(query):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 25, "mkt": "en-US", "freshness": "Week"}
    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print("Bing Error:", response.status_code)
        return []

# === Process and Analyze ===
def analyze_articles(articles, source_name):
    processed = []
    for article in articles:
        title = article.get("title", "")
        desc = article.get("description", "")
        text = title + ". " + desc
        if len(text.strip()) < 20:
            continue
        sentiment = sentiment_pipeline(text[:512])[0]
        esg_cat = classify_esg_category(text)
        processed.append({
            "Source": source_name,
            "Title": title,
            "Description": desc,
            "Sentiment Label": sentiment["label"],
            "Sentiment Score": sentiment["score"],
            "ESG Category": esg_cat,
            "Published": article.get("publishedAt") or article.get("datePublished"),
            "URL": article.get("url") or article.get("url")
        })
    return processed

# === Main Runner ===
def run_esg_news_monitoring(company_name):
    try:
        query = (
            f'"{company_name}" AND '
            f'(sustainability OR ESG OR emissions OR net-zero OR climate OR carbon OR environment OR governance OR diversity)'
        )
        from_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

        newsapi_articles = fetch_newsapi_articles(query, from_date)
        bing_articles = fetch_bing_articles(query)

        combined = analyze_articles(newsapi_articles, "NewsAPI") + analyze_articles(bing_articles, "Bing")
        df = pd.DataFrame(combined)
        display(df.head())
        df.sort_values("Published", ascending=False, inplace=True)
        # df.to_csv(f"{DATA_FOLDER_NEWS}esg_news_{company_name.lower()}.csv", index=False)
        for index, row in df.iterrows():
            new_item = EsgNews(company=company_name, 
                            news_source=row['Source'], 
                            news_title=row['Title'],
                            description=row['Description'],
                            sentiment_label=row['Sentiment Label'],
                            sentiment_score=row['Sentiment Score'],
                            esg_category=row['ESG Category'],
                            url=row['URL'],
                            published_date=row['Published'])
            db.session.add(new_item)
            db.session.commit()

        return df
    except Exception as e:
        print(f'run_esg_news_monitoring fail for {company_name}')
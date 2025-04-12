import pandas as pd
from src.config.sentiment_analysis_config import sentiment_pipeline
from src.model.esg_models import db, ReportHistory, EsgSentiment
from src.service.benchmark_service import detect_greenwashing_advanced

# ESG keyword classifier
def classify_esg_category(text):
    categories = {
        "Environment": ["carbon", "co2", "emissions", "ghg", "climate", "energy", "efficiency", "renewable",
        "solar", "wind", "geothermal", "hydropower", "footprint", "pollution", "waste",
        "air quality", "toxic waste", "water", "water consumption", "water waste",
        "electronic waste", "land use", "land restored", "biodiversity", "biodiversity impacts",
        "packaging material waste", "hydrocarbon spills",
        "air pollutant", "nox", "sox", "pm10", "voc", "scope 1", "scope 2", "scope 3",
        "net-zero", "decarbonization", "ecological"
        ],
        "Social": ["diversity", "inclusion", "equity", "equality", "labour", "union", "human rights",
        "training", "third party audits", "community", "health", "safety", "fatality", "incident", "trir",
        "feedback scores", "grievance mechanisms", "stakeholder", "wellbeing", "education",
        "philanthropy", "volunteer", "gender", "minorities", "social impact", "accessibility"
        ],
        "Governance": ["board diversity", "board independence", "voting rights", "accountability",
        "governance", "risk management", "audit", "compliance", "transparency",
        "ethics", "whistleblowing", "corruption", "anti-bribery",
        "remuneration", "pay", "executive pay", "cybersecurity", "data privacy",
        "accounting disclosure", "tax transparency",
        "clear tax strategy", "governance framework", "independent", "esg committee"
        ]
    }
    text_lower = text.lower()
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "Uncategorized"

# ESG JSON processor
# def process_esg_reports(file_paths=['content/json/conocophillips2023.json']):
#     results = []

#     for file_path in file_paths:
#         print(file_path)
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)

#         company = data.get("company", "Unknown")
#         year = data.get("year", "Unknown")
#         chunks = [s["text"] for s in data.get("sentences", []) if len(s["text"].strip()) > 20]

#         for chunk in chunks:
#             short_text = chunk[:512]
#             try:
#                 sentiment = sentiment_pipeline(short_text)[0]
#                 label = sentiment["label"]
#                 score = sentiment["score"]
#             except Exception as e:
#                 label = "Error"
#                 score = 0.0

#             esg_cat = classify_esg_category(short_text)

#             results.append({
#                 "Company": company,
#                 "Year": year,
#                 "ESG Category": esg_cat,
#                 "Sentiment Label": label,
#                 "Sentiment Score": score,
#                 "Text Snippet": short_text[:150] + "..."
#             })

#     return pd.DataFrame(results)


#     # Calculate sentiment stats
#     if not df.empty:
#         avg_score = df["Sentiment Score"].mean()
#         sentiment_counts = df["Sentiment Label"].value_counts(normalize=True) * 100
#         positive_pct = sentiment_counts.get("positive", 0)
#         negative_pct = sentiment_counts.get("negative", 0)
#         neutral_pct = sentiment_counts.get("neutral", 0)

#         print(f"Average Sentiment Score: {avg_score:.4f}")
#         print(f"Sentiment Distribution:\n"
#               f"  Positive: {positive_pct:.2f}%\n"
#               f"  Negative: {negative_pct:.2f}%\n"
#               f"  Neutral : {neutral_pct:.2f}%")
#     else:
#         print("No valid sentiment data found.")

#     return df

# ESG keyword classifier
def classify_esg_category(text):
    categories = {
        "Environment": ["carbon", "co2", "emissions", "ghg", "climate", "energy", "efficiency", "renewable",
        "solar", "wind", "geothermal", "hydropower", "footprint", "pollution", "waste",
        "air quality", "toxic waste", "water", "water consumption", "water waste",
        "electronic waste", "land use", "land restored", "biodiversity", "biodiversity impacts",
        "packaging material waste", "hydrocarbon spills",
        "air pollutant", "nox", "sox", "pm10", "voc", "scope 1", "scope 2", "scope 3",
        "net-zero", "decarbonization", "ecological"
        ],
        "Social": ["diversity", "inclusion", "equity", "equality", "labour", "union", "human rights",
        "training", "third party audits", "community", "health", "safety", "fatality", "incident", "trir",
        "feedback scores", "grievance mechanisms", "stakeholder", "wellbeing", "education",
        "philanthropy", "volunteer", "gender", "minorities", "social impact", "accessibility"
        ],
        "Governance": ["board diversity", "board independence", "voting rights", "accountability",
        "governance", "risk management", "audit", "compliance", "transparency",
        "ethics", "whistleblowing", "corruption", "anti-bribery",
        "remuneration", "pay", "executive pay", "cybersecurity", "data privacy",
        "accounting disclosure", "tax transparency",
        "clear tax strategy", "governance framework", "independent", "esg committee"
        ]
    }
    text_lower = text.lower()
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "Uncategorized"

# ESG JSON processor
def process_esg_reports(company, year):
    # file_paths = os.path.join(DATA_FOLDER_JSON, f"{company_name}{report_year}.json")
    results = []
    # print(f'file_paths:{file_paths}')
    # for file_path in file_paths:
    #     with open(file_path, 'r', encoding='utf-8') as f:
    #         data = json.load(f)

    #     company = data.get("company", "Unknown")
    #     year = data.get("year", "Unknown")
    
    data = ReportHistory.query.filter_by(company_name=company, year=year) \
        .order_by(ReportHistory.created_date.desc()).first()
    content = data.esg_content

    print(f'Process ESG for company:{company} year:{year}')
    # print(f'content:{content}')

    # Break into digestible paragraph chunks (around 512 tokens each)
    chunks = [b.strip() for b in content.split('\n\n') if len(b.strip()) > 50]

    for chunk in chunks:
        short_text = chunk[:512]
        try:
            sentiment = sentiment_pipeline(short_text)[0]
            label = sentiment["label"]
            score = sentiment["score"]
        except Exception as e:
            label = "Error"
            score = 0.0

        esg_cat = classify_esg_category(short_text)

        # results.append({
        #     "Company": company,
        #     "Year": year,
        #     "ESG Category": esg_cat,
        #     "Sentiment Label": label,
        #     "Sentiment Score": score,
        #     "Text Snippet": short_text[:150] + "..."
        # })

        # run Greenwash Risk
        [greenwashing_risk, matched_benchmark_topic] = detect_greenwashing_advanced({
            "Company": company,
            "Year": year,
            "ESG Category": esg_cat,
            "Sentiment Label": label,
            "Sentiment Score": score,
            "Text Snippet": short_text[:150] + "..."
        })

        new_item = EsgSentiment(year=year,
                         company=company, 
                         esg_category=esg_cat, 
                         sentiment_label=label, 
                         sentiment_score= score,
                         greenwashing_risk= greenwashing_risk,
                         matched_benchmark_topic= matched_benchmark_topic,
                         text_snippet=short_text[:450] + "...")
        db.session.add(new_item)
        db.session.commit()

    return 'Successful'
    # Step 4.2: save sentiment data to CSV file
    df = pd.DataFrame(results)
    # save_file_name = f"{DATA_FOLDER_SENTIMENT}esg_sentiment_climatebert_" + company + str(year) + ".csv"
    # print(f'save sentiment as {save_file_name}')
    # df.to_csv(save_file_name, index=False)

    return df
    # Calculate sentiment stats
    df = pd.DataFrame(results)
    if not df.empty:
        avg_score = df["Sentiment Score"].mean()
        sentiment_counts = df["Sentiment Label"].value_counts(normalize=True) * 100
        positive_pct = sentiment_counts.get("positive", 0)
        negative_pct = sentiment_counts.get("negative", 0)
        neutral_pct = sentiment_counts.get("neutral", 0)

        print(f"Average Sentiment Score: {avg_score:.4f}")
        print(f"Sentiment Distribution:\n"
              f"  Positive: {positive_pct:.2f}%\n"
              f"  Negative: {negative_pct:.2f}%\n"
              f"  Neutral : {neutral_pct:.2f}%")
        # new_item = EsgSentimentDistribution(year=year,
        #                  company=company, 
        #                  positive_pct=positive_pct, 
        #                  negative_pct=negative_pct, 
        #                  neutral_pct= neutral_pct)
        # db.session.add(new_item)
        # db.session.commit()
    else:
        print("No valid sentiment data found.")
    print(df)
    return df
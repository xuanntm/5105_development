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
def process_esg_reports(company, year, benchmark_topics):
    try:
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

            # run Greenwash Risk
            [greenwashing_risk, matched_benchmark_topic] = detect_greenwashing_advanced({
                "Company": company,
                "Year": year,
                "ESG Category": esg_cat,
                "Sentiment Label": label,
                "Sentiment Score": score,
                "Text Snippet": short_text[:150] + "..."
            }, benchmark_topics)

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
    except Exception as e:
        print(str(e))
        print(f'process_esg_reports fail for {company} {year}')
    
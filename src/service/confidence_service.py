import pandas as pd
from src.config.confidence_config import confidence_model
from sentence_transformers import util
# from src.config.app_config import DATA_FOLDER_CONFIDENCE

DATA_FOLDER_CONFIDENCE = "have to fix this code to load from DB"

def calculate_confidence_scores(company_name, report_year):
    csv_path = f'{DATA_FOLDER_CONFIDENCE}{company_name}_{report_year}.csv'
    # csv_path = f"ConocoPhillips_2023(Sheet1).csv"
    df = pd.read_csv(csv_path,encoding="latin1")
    results = []
    for idx, row in df.iterrows():
        metric = str(row.get('Metric', '')).strip()
        extracted = str(row.get('Extracted Metric ', '')).strip()
        if metric and extracted:
            emb_metric = confidence_model.encode(metric, convert_to_tensor=True)
            emb_extracted = confidence_model.encode(extracted, convert_to_tensor=True)
            score = float(util.cos_sim(emb_metric, emb_extracted).item())
            results.append({
                "Metric": metric,
                "Extracted_Metric": extracted,
                "Confidence_Score": round(score, 3),
                "Needs_Human_Review": score < 0.75
            })
    confidence_df = pd.DataFrame(results)
    mean_score = confidence_df["Confidence_Score"].mean()
    print(f"\n📈 Mean Confidence Score: {round(mean_score, 3)}")

    negative_scores = confidence_df[confidence_df["Confidence_Score"] < 0]
    if not negative_scores.empty:
        print("\n⚠️ Entries with Negative Confidence Scores:")
        print(negative_scores)

    return confidence_df


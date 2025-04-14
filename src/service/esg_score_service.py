import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler
from src.model.esg_models import db, BEsgMetricDataExtracted, BEsgActualScore


def extract_numeric(value):
    if pd.isna(value):
        return np.nan
    value = str(value).lower().replace(",", "")
    multiplier = 1
    if "million" in value:
        multiplier = 1_000_000
    elif "billion" in value:
        multiplier = 1_000_000_000
    match = re.search(r'[-+]?\d*\.\d+|\d+', value)
    return float(match.group()) * multiplier if match else np.nan

def assign_esg_rating(score):
    if score >= 75: return 'AAA'
    elif score >= 65: return 'AA'
    elif score >= 55: return 'A'
    elif score >= 45: return 'BBB'
    elif score >= 35: return 'BB'
    elif score >= 25: return 'B'
    else: return 'CCC'

# === ESG Score Functions ===



def calculate_environmental_score(df):
    env_weights = {
        "E01_GHG_ETT": 0.18,
        "E02_GHG_ITP": 0.15,
        "E05_Water_C": 0.09,
        "E06_Water_W": 0.08,
        "E03_Land": 0.06,
        "E09_Air_P": 0.10,
        "E07_Electronic_W": 0.06,
        "E10_Toxic_W": 0.10,
        "E11_Opp_RE": 0.07,
        "E08_Pkg_M_W": 0.05,
        "E04_Bio": 0.06
        
    }

    for col in env_weights:
        if col in df.columns:
            df[col] = df[col].apply(extract_numeric)

    reverse_cols = [col for col in env_weights if col != "E11_Opp_RE"]
    scaler = MinMaxScaler()

    for col in reverse_cols:
        if col in df.columns:
            df[[col]] = 1 - scaler.fit_transform(df[[col]].fillna(0)) if df[col].nunique() > 1 else 0.5

    pos_col = "E11_Opp_RE"
    if pos_col in df.columns:
        df[[pos_col]] = scaler.fit_transform(df[[pos_col]].fillna(0)) if df[pos_col].nunique() > 1 else 0.5

    env_score = sum(df[col].fillna(0) * weight for col, weight in env_weights.items() if col in df.columns)
    df["Environmental Score"] = env_score * 100
    return df

def calculate_social_score(df):
    binary_map = {'Yes': 1, 'No': 0}
    social_weights = {
        "S01_HR": 0.15,
        "S02_PR": 0.15,
        "S03_HSI": 0.20,
        "S04_HSF": 0.20,
        "S05_TH": 0.20,
        "S06_CR": 0.10
    }

    df["S01_HR"] = df.get("S01_HR", 0.5)
    df["S02_PR"] = df.get("S02_PR", 0.5)

    if "S06_CR" in df.columns:
        df["S06_CR"] = df["S06_CR"].map(binary_map)

    quant_cols = [
        "S03_HSI",
        "S04_HSF",
        "S05_TH"
    ]
    for col in quant_cols:
        if col in df.columns:
            df[col] = df[col].apply(extract_numeric)

    scaler = MinMaxScaler()
    for col in quant_cols:
        if col in df.columns:
            df[[col]] = 1 - scaler.fit_transform(df[[col]].fillna(0))

    for col in social_weights.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    social_score = sum(df[col].fillna(0) * weight for col, weight in social_weights.items() if col in df.columns)
    df["Social Score"] = social_score * 100
    return df

def calculate_governance_score(df):
    rating_map = {'Poor': 0.0, 'Fair': 0.5, 'Good': 1.0, 'Present': 0.5}
    binary_map = {'Yes': 1, 'No': 0}

    gov_weights = {
        "G01_BD": 0.15,
        "G02_BI": 0.15,
        "G03_P": 0.15,
        "G04_Acct": 0.10,
        "G05_BE": 0.15,
        "G06_Tax_T": 0.10,
        "G07_Vote_R": 0.20
    }

    df["G01_BD"] = df.get("G01_BD", 50)
    df["G02_BI"] = df.get("G02_BI", 50)
    df[["G01_BD", "G02_BI"]] = (
        MinMaxScaler().fit_transform(df[["G01_BD", "G02_BI"]])
    )

    for col in ["G03_P", "G04_Acct",
                "G05_BE", "G06_Tax_T"]:
        if col in df.columns:
            df[col] = df[col].fillna("Fair").map(rating_map)

    if "G07_Vote_R" in df.columns:
        df["G07_Vote_R"] = df["G07_Vote_R"].fillna("No").map(binary_map)

    gov_score = sum(df[col].fillna(0) * weight for col, weight in gov_weights.items() if col in df.columns)
    df["Governance Score"] = gov_score * 100
    return df

def calculate_final_esg_score(df, year=2023):
    df["Year"] = year
    df["ESG Score"] = (
        df["Environmental Score"] * 0.40 +
        df["Social Score"] * 0.30 +
        df["Governance Score"] * 0.30
    )
    df["ESG Rating"] = df["ESG Score"].apply(assign_esg_rating)
    df["ESG Rank"] = df["ESG Score"].rank(ascending=False, method="min").astype(int)
    return df

def load_all_data(year=2023):
    data = db.session.query(BEsgMetricDataExtracted).all()
    # Convert to a DataFrame
    data_dicts = [item.__dict__ for item in data]  # Convert each item to a dictionary
    df = pd.DataFrame(data_dicts)

    df = calculate_environmental_score(df)
    df = calculate_social_score(df)
    df = calculate_governance_score(df)
    df = calculate_final_esg_score(df, year)

    # Remove internal SQLAlchemy states from the DataFrame
    if '_sa_instance_state' in df:
        df.drop(columns=['_sa_instance_state'], inplace=True)

    def process_row(row):
        return BEsgActualScore(
            Year=row['Year'],
            company_name=row['Company_name'],
            Environmental_Score=row['Environmental Score'],
            Social_Score=row['Social Score'],
            Governance_Score=row['Governance Score'],
            ESG_Score=row['ESG Score'],
            ESG_Rating=row['ESG Rating'],
            ESG_Rank=row['ESG Rank'],
            data_type='DEMO'
        )
    # Apply the function to each row
    results = df.apply(process_row, axis=1)
    db.session.add_all(results)
    db.session.commit()

    inserted_records = [
        {
            'id': record.id,
            'Company_name': record.company_name,
            'Year': record.Year,
            'Environmental_Score': record.Environmental_Score,
            'Social_Score': record.Social_Score,
            'Governance_Score': record.Governance_Score,
            'ESG_Score': record.ESG_Score,
            'ESG_Rating': record.ESG_Rating,
            'ESG_Rank': record.ESG_Rank,
            'data_type': record.data_type,
            'created_date': record.created_date.isoformat()  # Format the datetime
        } for record in results
    ]

    return df, inserted_records
    # return inserted_records

    # return df.to_json(orient='records')  # Return as JSON
    
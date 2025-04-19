import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler
from src.model.esg_models import db, BEsgMetricDataExtracted, BEsgActualScore


def extract_numeric(value):
    """
    Extracts a numeric value from a given string, accounting for common financial units such as 'million' or 'billion'.

    Parameters:
    value (str or any): A string (or convertible value) potentially containing a numeric amount 
                        with optional text like 'million' or 'billion'.

    Returns:
    float: The extracted numeric value scaled appropriately (e.g., millions converted to actual numbers),
           or np.nan if no valid number is found or input is null.
    
    Example:
    >>> extract_numeric("2.5 million")
    2500000.0
    >>> extract_numeric("1,200,000")
    1200000.0
    >>> extract_numeric("Not Available")
    nan
    """
    # Check if the input is NaN (Not a Number); if so, return NaN
    if pd.isna(value):
        return np.nan
    # Convert the value to lowercase string and remove commas (e.g., "1,000" → "1000")
    value = str(value).lower().replace(",", "")
    # Initialize multiplier as 1 (default if no unit is specified)
    multiplier = 1
    # Adjust multiplier based on whether the value contains "million" or "billion"
    if "million" in value:
        multiplier = 1_000_000
    elif "billion" in value:
        multiplier = 1_000_000_000
    # Use regular expression to extract the first numeric value from the string
    match = re.search(r'[-+]?\d*\.\d+|\d+', value)
    # If a numeric part is found, convert it to float and apply the multiplier
    return float(match.group()) * multiplier if match else np.nan

def assign_esg_rating(score):
    """
    Assigns an ESG (Environmental, Social, and Governance) rating based on the numeric ESG score.

    Parameters:
    score (float): The ESG score of the company, typically ranging from 0 to 100.

    Returns:
    str: An ESG rating category from highest to lowest in the following order:
         'AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC'

    Rating Scale Reference:
    - AAA : score >= 75
    - AA  : 65 <= score < 75
    - A   : 55 <= score < 65
    - BBB : 45 <= score < 55
    - BB  : 35 <= score < 45
    - B   : 25 <= score < 35
    - CCC : score < 25

    Example:
    >>> assign_esg_rating(72)
    'AA'
    >>> assign_esg_rating(43)
    'BB'
    """
    if score >= 75: return 'AAA'
    elif score >= 65: return 'AA'
    elif score >= 55: return 'A'
    elif score >= 45: return 'BBB'
    elif score >= 35: return 'BB'
    elif score >= 25: return 'B'
    else: return 'CCC'

# === ESG Score Functions ===



def calculate_environmental_score(df):
    """
    Calculates the environmental component of the ESG score for each company in the dataset.

    The function performs the following steps:
    1. Defines a set of environmental indicators and their associated weights.
    2. Applies the `extract_numeric` function to parse values (e.g., "2.5 million") into numbers.
    3. Normalizes each metric using MinMaxScaler:
       - For negative-impact indicators, higher values are penalized (inverse scaled).
       - For opportunity indicators (e.g., renewable energy usage), higher values are rewarded (normal scaled).
    4. Computes a weighted sum of all normalized environmental indicators to form the final Environmental Score.

    Parameters:
    df (pd.DataFrame): A DataFrame containing environmental metrics for one or more companies.

    Returns:
    pd.DataFrame: The input DataFrame with an added "Environmental Score" column on a 0–100 scale.

    Note:
    - All missing or non-numeric values are handled using `extract_numeric` and defaulted to 0 before scoring.
    - MinMax scaling is applied only if a column has more than one unique value; otherwise, it is set to 0.5 (neutral).
    """
    
    # === Define environmental weights based on materiality ===
    env_weights = {
        "E01_GHG_ETT": 0.18,        # Total GHG emissions
        "E02_GHG_ITP": 0.15,        # GHG intensity per unit of production
        "E05_Water_C": 0.09,        # Water consumption
        "E06_Water_W": 0.08,        # Wastewater generation
        "E03_Land": 0.06,           # Land usage or impact
        "E09_Air_P": 0.10,          # Air pollution (e.g., NOx, SOx)
        "E07_Electronic_W": 0.06,   # Electronic waste
        "E10_Toxic_W": 0.10,        # Toxic waste
        "E11_Opp_RE": 0.07,         # Renewable energy opportunity (positive impact)
        "E08_Pkg_M_W": 0.05,        # Packaging material waste
        "E04_Bio": 0.06             # Biodiversity impact
    }

    # === Step 1: Convert all applicable columns to numeric format ===
    for col in env_weights:
        if col in df.columns:
            df[col] = df[col].apply(extract_numeric)

    reverse_cols = [col for col in env_weights if col != "E11_Opp_RE"]
    scaler = MinMaxScaler()

    # === Step 2: Reverse-scale negative indicators (higher is worse) ===
    for col in reverse_cols:
        if col in df.columns:
            df[[col]] = 1 - scaler.fit_transform(df[[col]].fillna(0)) if df[col].nunique() > 1 else 0.5

    # === Step 3: Standard scaling for positive indicator (higher is better) ===
    pos_col = "E11_Opp_RE"
    if pos_col in df.columns:
        df[[pos_col]] = scaler.fit_transform(df[[pos_col]].fillna(0)) if df[pos_col].nunique() > 1 else 0.5

    env_score = sum(df[col].fillna(0) * weight for col, weight in env_weights.items() if col in df.columns)
    df["Environmental Score"] = env_score * 100
    return df

def calculate_social_score(df):
    """
    Calculates the Social component of the ESG score based on a weighted combination of social indicators.

    The function performs the following:
    1. Assigns default mid-values to binary policy fields if missing.
    2. Converts 'Yes'/'No' responses to binary values for community relations.
    3. Extracts and normalizes quantitative fields using MinMaxScaler (inversely, since higher incidents/fatalities are worse).
    4. Applies a weighted sum to compute the Social Score.

    Parameters:
    df (pd.DataFrame): DataFrame containing company-level social ESG indicators.

    Returns:
    pd.DataFrame: Updated DataFrame with an added "Social Score" column (scaled 0–100).

    Assumptions:
    - Binary policy values ('Yes'/'No') default to 0.5 (neutral) if missing.
    - Quantitative values such as incident rates are scaled inversely.
    """
    # Map for converting Yes/No fields to binary
    binary_map = {'Yes': 1, 'No': 0}
    # Define weights for each social indicator
    social_weights = {
        "S01_HR": 0.15,   # Human Rights Policy
        "S02_PR": 0.15,   # Privacy Rights Policy
        "S03_HSI": 0.20,  # Health & Safety - Incident Rate
        "S04_HSF": 0.20,  # Health & Safety - Fatality Rate
        "S05_TH": 0.20,   # Training Hours per Employee
        "S06_CR": 0.10    # Community Relations Program (Yes/No)
    }

    # Set default neutral values for binary fields if missing
    df["S01_HR"] = df.get("S01_HR", 0.5)
    df["S02_PR"] = df.get("S02_PR", 0.5)

    # Convert Yes/No to 1/0 for S06_CR (Community Relations)
    if "S06_CR" in df.columns:
        df["S06_CR"] = df["S06_CR"].map(binary_map)

    # Quantitative fields to normalize (higher values are worse, so they are reverse-scaled)
    quant_cols = [
        "S03_HSI",
        "S04_HSF",
        "S05_TH"
    ]
    for col in quant_cols:
        if col in df.columns:
            df[col] = df[col].apply(extract_numeric)

    # Normalize quantitative fields (reverse for incident/fatality rates)
    scaler = MinMaxScaler()
    for col in quant_cols:
        if col in df.columns:
            df[[col]] = 1 - scaler.fit_transform(df[[col]].fillna(0))

    # Ensure all weights are applied to numeric values only
    for col in social_weights.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Compute the weighted social score and scale to 0–100
    social_score = sum(df[col].fillna(0) * weight for col, weight in social_weights.items() if col in df.columns)
    df["Social Score"] = social_score * 100
    return df

def calculate_governance_score(df):
    """
    Calculates the Governance component of the ESG score based on key governance indicators.

    This function handles both numeric and categorical governance data by:
    - Mapping categorical ratings (e.g., 'Poor', 'Fair', 'Good') to numeric scores.
    - Scaling board diversity and independence percentages.
    - Applying a weighted sum to compute the Governance Score (0–100 scale).

    Parameters:
    df (pd.DataFrame): DataFrame containing governance-related ESG fields for companies.

    Returns:
    pd.DataFrame: Input DataFrame with an added "Governance Score" column.

    Assumptions:
    - Board Diversity and Independence are numeric percentages (e.g., 40 for 40%).
    - Governance quality fields use labels like 'Poor', 'Fair', 'Good'.
    - Missing values are handled with default values ('Fair' for ratings, 50% for percentages).
    """
    
    # === Mapping definitions ===
    rating_map = {'Poor': 0.0, 'Fair': 0.5, 'Good': 1.0, 'Present': 0.5}
    binary_map = {'Yes': 1, 'No': 0}

    # === Weights for each governance metric ===
    gov_weights = {
        "G01_BD": 0.15,        # Board Diversity (%)
        "G02_BI": 0.15,        # Board Independence (%)
        "G03_P": 0.15,         # Anti-Corruption Policy
        "G04_Acct": 0.10,      # Audit Committee Independence
        "G05_BE": 0.15,        # Board Effectiveness
        "G06_Tax_T": 0.10,     # Tax Transparency
        "G07_Vote_R": 0.20     # Shareholder Voting Rights
    }
    # === Step 1: Fill default 50% for missing Board Diversity and Independence, then scale 0–1 ===

    df["G01_BD"] = df.get("G01_BD", 50)
    df["G02_BI"] = df.get("G02_BI", 50)
    df[["G01_BD", "G02_BI"]] = (
        MinMaxScaler().fit_transform(df[["G01_BD", "G02_BI"]])
    )

    # === Step 2: Map categorical ratings to numeric scores ===
    for col in ["G03_P", "G04_Acct",
                "G05_BE", "G06_Tax_T"]:
        if col in df.columns:
            df[col] = df[col].fillna("Fair").map(rating_map)
    
     # === Step 3: Map Yes/No binary field for shareholder voting rights ===
    if "G07_Vote_R" in df.columns:
        df["G07_Vote_R"] = df["G07_Vote_R"].fillna("No").map(binary_map)

    # === Step 4: Compute weighted governance score ===
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
    """
    Loads raw ESG metric data from the database, calculates individual and overall ESG scores,
    and stores the results back into the database.

    Steps:
    1. Retrieve all records from `BEsgMetricDataExtracted`.
    2. Convert ORM objects to a pandas DataFrame.
    3. Compute Environmental, Social, Governance, and Final ESG scores.
    4. Remove SQLAlchemy's internal instance state from DataFrame.
    5. Convert scored rows to `BEsgActualScore` objects and insert them into the database.
    6. Return the scored DataFrame and a summary list of inserted records.

    Parameters:
    year (int): The year for which the ESG scores are computed and tagged. Default is 2023.

    Returns:
    tuple: (DataFrame with ESG scores, List of inserted record metadata)
    """
    # === Step 1: Retrieve all raw ESG metric data from the database ===
    data = db.session.query(BEsgMetricDataExtracted).all()
    
    # === Step 2: Convert SQLAlchemy ORM objects to dictionaries, then to a DataFrame ===
    data_dicts = [item.__dict__ for item in data]  # Convert each item to a dictionary
    df = pd.DataFrame(data_dicts)

    # === Step 3: Compute ESG Sub-Scores and Final Score ===
    df = calculate_environmental_score(df)
    df = calculate_social_score(df)
    df = calculate_governance_score(df)
    df = calculate_final_esg_score(df, year)

    # === Step 4: Remove internal SQLAlchemy state from the DataFrame if present ===
    if '_sa_instance_state' in df:
        df.drop(columns=['_sa_instance_state'], inplace=True)

    # === Step 5: Convert each row into a BEsgActualScore ORM object ===
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
    # === Step 6: Bulk insert all scored records into the database ===
    db.session.add_all(results)
    db.session.commit()
    # === Step 7: Format and return inserted record summaries ===
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
    
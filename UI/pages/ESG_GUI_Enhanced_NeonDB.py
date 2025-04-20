# ESG_GUI_Enhanced.py with Login, Logout, and Chatbot Integration

import streamlit as st
st.set_page_config(page_title="CTRL+Sustain ESG Dashboard", page_icon="🌱", layout="wide")


#Hide Streamlit sidebar page names
st.markdown("""<style>[data-testid="stSidebarNav"] { display: none; }</style>""", unsafe_allow_html=True)

import pandas as pd
import plotly.express as px
import os
import base64
import seaborn as sns
import matplotlib.pyplot as plt
from openai import OpenAI
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import psycopg2
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy
from sqlalchemy import text
import unicodedata

# Load environment variables
load_dotenv()


DB_URL = os.getenv('DATABASE_URL')
#db_url = os.getenv("DATABASE_URL")

#if not db_url:
    #raise ValueError("❌ DATABASE_URL not found in .env")

# Create a connection
engine = create_engine(DB_URL)



# Neon DB Query Helper
def run_query(query, params=None):
    with engine.connect() as conn:
        if params:
            return pd.read_sql_query(text(query), conn, params=params)
        else:
            return pd.read_sql_query(text(query), conn)

# ✅ Update this if your schema is 'esg' instead of 'public'
SCHEMA = "public"

from sqlalchemy import text

# Neon DB Query Helper
def run_query(query, params=None):
    with engine.connect() as conn:
        if params:
            return pd.read_sql_query(text(query), conn, params=params)
        else:
            return pd.read_sql_query(text(query), conn)

# ✅ Update this if your schema is 'esg' instead of 'public'
SCHEMA = "public"


# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: 'Lato', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lato', sans-serif;
        font-weight: bold;
        text-transform: uppercase;
    }
    .ctrl-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
    }
    .ctrl-caption {
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #4CAF50 !important;
        margin-top: -10px !important;
    }
    .block-container {
        padding-top: 2rem;
    }
    .sidebar-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .sidebar-center button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    if st.session_state.get("show_company_performance", False):
        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-center'><h5>Select Company</h5></div>", unsafe_allow_html=True)
        selected_main_company = st.selectbox(
            "Choose a company to view ESG performance",
            options=company_list,
            key="main_company_selectbox"
        )
        st.session_state["selected_main_company"] = selected_main_company
    else:
        st.session_state["selected_main_company"] = None


</style>
""", unsafe_allow_html=True)
# Function to extract year and company from filename
def extract_year_company(filename):
    parts = filename.split("_")
    if len(parts) == 2:
        company,year = parts[0], parts[1].replace(".csv", "").strip()
        return company,year
    elif len(parts) == 3:  # Handle filenames with year, company, and extra info
        year = parts[1]
        company = parts[0]
        return company, year.replace(".csv","").strip()
    else:
        return None, None

# ---------- SIDEBAR NAVIGATION ----------
st.markdown("<div class='sidebar-center'>", unsafe_allow_html=True)
st.sidebar.image("Ctrlsustainlogo.png", width=300)
#menu
st.sidebar.markdown("""
<div class='sidebar-center'>
    <br/>
    <h4 style='text-align: center;'>MENU</h4>
</div>
""", unsafe_allow_html=True)

# Define equal-length button labels (padded manually)
home_label = "Home".ljust(35)  # Adjust padding as needed
performance_label = "ESG Performance by Company".ljust(35)

with st.sidebar:
    # Inject CSS for button styling and centering
    st.markdown("""
        <style>
            .centered-button-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .stButton > button {
                width: 285px;
                text-align: center;
                font-weight: 600;
            }
        </style>
        <div class='centered-button-container'>
    """, unsafe_allow_html=True)
    # Add Home button
    if st.button(home_label):
        st.session_state["show_home"] = True
        st.session_state["show_company_performance"] = False  # Reset other page states

    # Add "ESG Performance by Company" button
    if st.button(performance_label):
        st.session_state["show_company_performance"] = True
        st.session_state["show_home"] = False  # Reset other page states

    # Close the div
    st.markdown("</div>", unsafe_allow_html=True)

    # Set default states if not clicked
    if "show_home" not in st.session_state:
        st.session_state["show_home"] = True
    if "show_company_performance" not in st.session_state:
        st.session_state["show_company_performance"] = False

    if st.session_state.get("show_home", True):  # Default to True if not set
        uploaded_files = st.sidebar.file_uploader(
        "📂 Upload ESG Reports (CSV files)", accept_multiple_files=True, type=["csv"]
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                company, year = extract_year_company(uploaded_file.name)
                if company and year:
                    try:
                        uploaded_csv = pd.read_csv(uploaded_file, encoding="latin1")

                        db_table_name = "b_esg_metric_data_extracted"

                        # Reflect the table metadata
                        metadata = sqlalchemy.MetaData()
                        table = sqlalchemy.Table(db_table_name, metadata, autoload_with=engine, schema=SCHEMA)

                        # Remove 'id' column if it exists in uploaded CSV
                        if 'id' in uploaded_csv.columns:
                            uploaded_csv.drop(columns=['id'], inplace=True)

                        # Get the current max ID from the table
                        with engine.connect() as conn:
                            max_id_result = conn.execute(sqlalchemy.text(
                                f"SELECT MAX(id) FROM {SCHEMA}.{db_table_name}"
                            ))
                            max_id = max_id_result.scalar() or 0  # Start from 0 if table is empty

                        # Add new incremental IDs
                        uploaded_csv.insert(0, 'id', range(max_id + 1, max_id + 1 + len(uploaded_csv)))

                        # Insert to DB
                        uploaded_csv.to_sql(db_table_name, con=engine, schema=SCHEMA, if_exists="append", index=False)

                        table_name = company + '_' + year
                        st.success(f"✅ Uploaded and stored table: {table_name}")

                    except Exception as e:
                        st.error(f"❌ Failed to upload {uploaded_file.name}: {e}")

# ---------- MAIN HOME NAVIGATION ----------
# Load ESG Scores and ESG Metrics dataset
# esg_scores_file = r"2023_actual_esg_companies_score.csv"
# esg_metrics_file = r"2023_Energy_companies_metrics.csv"

# Function to load datasets
@st.cache_data
def load_data():
    df_scores = pd.read_sql("SELECT * FROM b_esg_actual_score WHERE data_type = 'actual'", engine)
    df_metrics = pd.read_sql("SELECT * FROM b_esg_metric_data_extracted WHERE data_type = 'real'", engine)
    return df_scores, df_metrics

# Load datasets
df_scores, df_metrics = load_data()
# ----------------- HOME PAGE -----------------

if st.session_state.get("show_home", False):
    st.markdown("""
    <style>
        /* Gradient Background */
        body {
            background: linear-gradient(135deg, #a8e6cf, #cce5ff, #b3b3ff);
            background-size: 180% 180%;
            animation: gradientBG 10s ease infinite;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Apply to full screen */
        .stApp {
            background: linear-gradient(135deg,#a8e6cf, #cce5ff, #b3b3ff);
            background-size: 180% 180%;
            animation: gradientBG 10s ease infinite;
        }

        html, body {
            height: 100%;
            margin: 0;
        }

        /* Optional enhancements */
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>ESG Overview</h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
    Welcome to <strong>CTRL+Sustain</strong> — a data-driven ESG analytics platform that delivers transparent, standardized, and actionable sustainability insights.
    Inconsistent ESG reporting makes cross-industry comparisons challenging and increases the risk of greenwashing.
    </p>
    <br/>
    <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
    Our dashboard automates ESG data extraction, applies consistent metrics for benchmarking, and visualizes key environmental, social, and governance indicators — empowering stakeholders to make informed, sustainability-aligned decisions with ease.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)  # One line space

    # ✅ ESG Ranking Table from actual_esg_companies_score.csv
    company_logos = {
        "Shell": "images/shell-icon.png",
        "BP": "images/bp-icon.png",
        "FirstSolar": "images/firstsolar-icon.png",
        "NextEra": "images/nextera-icon.png",
        "ConocoPhillips": "images/conocophillips-icon.jpg",
        "Chevron": "images/chevron-icon.png",
        "Totalenergies" : "images/totalenergies-icon.png",
        "Aramco": "images/aramco-icon.png",
        "Petrochina": "images/petrochina-icon.jpg",
        "Exxonmobil" : "images/exonmobil-icon.png"
    }

    def get_base64_image(image_path):
        base_path = os.path.dirname(__file__)  # Get current script directory
        full_path = os.path.join(base_path, image_path)  # Build full path to image
        with open(full_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()


    df_ranked = df_scores[['company_name', 'ESG_Rank', 'ESG_Rating', 'ESG_Score']].copy()
    df_ranked = df_ranked.rename(columns={
    "company_name": "Company",
    "ESG_Rank": "ESG Rank",
    "ESG_Rating": "ESG Rating",
    "ESG_Score": "ESG Score"
})
    df_ranked = df_ranked[df_ranked['Company'].isin(company_logos.keys())]
    df_ranked['Logo'] = df_ranked['Company'].apply(
        lambda x: f"<img src='data:image/png;base64,{get_base64_image(company_logos[x])}' width='50' style='display:block;margin:auto;'>"
    )

    df_ranked = df_ranked[['Logo', 'Company', 'ESG Rank', 'ESG Rating', 'ESG Score']]
    df_ranked = df_ranked.sort_values(by="ESG Rank", ascending=True)

    # Custom CSS
    st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }
        .center-table {
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }
        .styled-table {
            border-collapse: collapse;
            margin: auto;
            font-size: 15px;
            width: 100%;
            max-width: 1200px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border-radius: 10px;
            overflow: hidden;
        }
        .styled-table th, .styled-table td {
            padding: 14px 22px;
            text-align: center;
            border-top: 1px solid #eaeaea;
            border-bottom: 1px solid #eaeaea;
            border-left: none !important;
            border-right: none !important;
        }
        .styled-table thead tr {
            font-weight: bold;
            text-transform: uppercase;
            background-color: #f3f3f3;
            border-bottom: 2px solid #ccc;
        }
        .styled-table tbody tr:hover {
            background-color: #fafafa;
        }
    </style>
    """, unsafe_allow_html=True)

    # Render header
    st.markdown("<h3 style='text-align: center; text-transform: none;'>📊 Company ESG Performance Table</h3>", unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
        "This table provides a quick comparison of leading companies' ESG performance to support informed, sustainability-focused investment decisions."
        "</p>",
        unsafe_allow_html=True,
    )

    # Render HTML table
    styled_html = f"""
    <div class="center-table">
        {df_ranked.to_html(escape=False, index=False, classes='styled-table')}
    </div>
    """
    st.markdown(styled_html, unsafe_allow_html=True)
    st.markdown("---")


    # 📈 Bar charts
    st.markdown("<h3 style='text-align: center; text-transform: none;'>📈 ESG Score Comparison by Company</h3>", unsafe_allow_html=True)
    # Melt the DataFrame to long format
    df_melted=df_scores[['company_name', 'Environmental_Score', 'Social_Score', 'Governance_Score']].melt(
        id_vars="company_name",
        var_name="Category",
        value_name="Score"
    )

    # Rename categories for better labels
    df_melted["Category"] = df_melted["Category"].replace({
        "Environmental_Score": "Environmental",
        "Social_Score": "Social",
        "Governance_Score": "Governance"
    })
    df_melted = df_melted.rename(columns={"company_name": "Company"})
    # Set custom colors
    color_map = {
        "Environmental": "#00be63",
        "Social": "#38b6ff",
        "Governance": "#3300f3"
    }

    # Plot the stacked bar chart
    fig = px.bar(
        df_melted,
        x="Company",
        y="Score",
        color="Category",
        color_discrete_map=color_map,
    )
    fig.update_layout(
                        margin=dict(t=20, b=20, l=10, r=10),
                        legend=dict(font=dict(size=12)),
                        showlegend=True
                    )

    fig.update_layout(
        barmode="stack",
        height=500
    )

    st.markdown(
        """
        <div style='max-width: 1200px; margin: auto;'>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)




    st.markdown(
        "<p style='text-align: centre; max-width: 1200px; margin: auto; font-size: 18px'>"
        "This chart presents a comparative view of Environmental, Social, and Governance (ESG) scores across leading energy companies. Shell demonstrates the highest overall ESG performance, while Chevron shows lower relative scores, particularly in the Social and Governance dimensions—highlighting potential areas for strategic ESG improvement."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    #----ESG Cluster Analysis----
    st.markdown("<h3 style='text-align: center; text-transform: none;'>🎯 ESG Cluster Analysis</h3>", unsafe_allow_html=True)

    st.markdown("<h5 style='text-align: left; text-transform: none;'>🧠 Understanding the PCA Axes</h4>", unsafe_allow_html=True)
    
    st.markdown(
        "<p style='text-align: center; max-width: 1200px; margin: auto; font-size: 18px'>"
        "<li><b>Principal Component 1 (PCA1)</b>: Captures the strongest signal in ESG data — typically balancing Environmental and Social leadership versus Governance rigor. A company with a high PCA1 score may demonstrate progressive E&S policies, while lower scores might emphasize risk management and board independence.</li>"
        "<li><b>Principal Component 2 (PCA2)</b>: Highlights the second-most important contrast, such as regulatory transparency vs. operational sustainability. This dimension often helps separate niche outperformers or laggards.</li>"
        "</p>",
        unsafe_allow_html=True,
    )

    
    # Load the dataset
    df = pd.read_sql("SELECT * FROM b_esg_cluster_analyis_actual WHERE data_type = 'actual'", engine)

    # Optional: Create a label column
    if "company_name" in df.columns:
        df["Label"] = df["company_name"]
    else:
        df["Label"] = ["Company-{}".format(i + 1) for i in range(len(df))]

    # Plotting
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=df, x="PCA1", y="PCA2", hue="Cluster", palette="Set2", s=100, ax=ax)

    # Get axis limits
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Annotate each point above with bounds check
    for i in range(len(df)):
        x = df["PCA1"][i]
        y = df["PCA2"][i] + 0.05  # Shift label slightly upward
        # Clamp to axis limits if needed
        y = min(y, y_max - 0.01)
        x = min(max(x, x_min + 0.01), x_max - 0.01)
        
        ax.text(x, y, df["Label"][i], fontsize=8, ha='center', va='bottom')

    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")
    ax.legend(title="Cluster")

    # Display the plot in Streamlit
    st.pyplot(fig)

    st.markdown("---")

    #------ CLUSTER CHATGPT INSIGHTS----
    # --- Load the clustering CSV file ---
    #file_path = os.path.abspath("cluster_analyis_actual.csv")
    cluster_df = pd.read_sql("SELECT * FROM b_esg_cluster_analyis_actual WHERE data_type = 'actual'", engine)

    # --- Cluster Insights ---
    #st.markdown("<h3 style='text-align: center; text-transform: none;'>🤖 Cluster Insights</h3>", unsafe_allow_html=True)

    # try:
    #     # Initialize OpenAI client (v1.x style)
    #     api_key = os.getenv("OPENAI_API_KEY")
    #     client = OpenAI(api_key=api_key)
    #     #client = os.getenv("OPENAI_API_KEY")

    #     def sanitize_prompt(text):
    #         return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        
    #     # Group by cluster and compute mean
    #     cluster_summary = cluster_df.groupby("Cluster").mean(numeric_only=True).reset_index()
    #     summary_str = cluster_summary.to_string(index=False)
    #     summary_str_clean = sanitize_prompt(summary_str)
        
    #     # Prompt construction
    #     raw_prompt = (
    #         "You are an ESG data analyst. Based on the ESG cluster summary below, "
    #         "do the cluster analysis summary and provide insights which area they are lagging and how to improve. "
    #         "Return each insight on a separate line in this format:\n\n"
    #         "Cluster 0: <one-line insight>\n"
    #         "Cluster 1: <one-line insight>\n"
    #         "Cluster 2: <one-line insight>\n\n"
    #         f"{summary_str_clean}"
    #     )
        
    #     prompt = sanitize_prompt(raw_prompt)

    #     # GPT-4 call
    #     #prompt = prompt.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    #     response = client.chat.completions.create(
    #         model="gpt-4",
    #         max_tokens=250,
    #         temperature=0.5,
    #         messages=[
    #             {"role": "system", "content": "You are a concise ESG data analyst."},
    #             {"role": "user", "content": prompt}
    #         ]
    #     )
    #     # (Optional) Display the result
    #     print(response.choices[0].message.content)

    #     # Display insights
    #     cluster_insight = response.choices[0].message.content.strip()

    #     st.markdown("✅ **AI-generated insights below:**")
    #     st.markdown(f"""
    #         <div style='
    #             background-color: #f0f2f6;
    #             padding: 1rem;
    #             margin-top: 0.5rem;
    #             border-radius: 10px;
    #             max-width: 1200px;
    #             margin-left: auto;
    #             margin-right: auto;
    #             font-size: 18px;
    #             line-height: 1.6;
    #             color: #000;
    #             white-space: pre-wrap;
    #             word-wrap: break-word;
    #             text-align: left;
    #         '>{cluster_insight}</div>
    #     """, unsafe_allow_html=True)
        
    #     # --- Fix the 'Year' formatting and drop 'id' column ---
    #     cluster_summary['Year'] = cluster_summary['Year'].astype(int)  # No decimal points
    #     if 'id' in cluster_summary.columns:
    #         cluster_summary.drop(columns=['id'], inplace=True)

    #     # Round all columns except 'Cluster' and 'Year'
    #     cols_to_round = [col for col in cluster_summary.columns if col not in ['Cluster', 'Year']]
    #     cluster_summary[cols_to_round] = cluster_summary[cols_to_round].round(2)

    #     # ---------- Custom CSS for max width and table style ----------
    #     st.markdown("""
    #         <style>
    #             .streamlit-expander, .element-container, .stDataFrameContainer {
    #                 max-width: 1200px !important;
    #                 margin: auto;
    #             }
    #             table {
    #                 border-collapse: collapse;
    #                 width: 100%;
    #             }
    #             th, td {
    #                 border: 2px solid #333333 !important;
    #                 padding: 8px;
    #                 text-align: center;
    #                 color: black !important;
    #             }
    #         </style>
    #     """, unsafe_allow_html=True)

    #     # ---------- ESG Cluster Summary Header ----------
    #     st.markdown("""
    #         <div style='max-width: 1200px; margin: auto;'>
    #             <h3 style='text-align: center; text-transform: none;'>📊 ESG Cluster Summary</h3>
    #         </div>
    #     """, unsafe_allow_html=True)

    #     # ---------- Display Table with Styling ----------
    #     st.markdown("<div style='max-width: 1200px; margin: auto;'>", unsafe_allow_html=True)
    #     st.table(cluster_summary)  # You can use st.dataframe(cluster_summary) for interactivity
    #     st.markdown("</div>", unsafe_allow_html=True)


        
    # except Exception as e:
    #     st.warning("⚠️ Could not fetch AI insights. Please check your OpenAI API key or internet connection.")
    #     st.exception(e)
        
    # st.markdown("---")
# ----------------- ESG PERFORMANCE BY COMPANY PAGE -----------------
    st.markdown("<h3 style='text-align: center; text-transform: none;'>🧭 Clustered ESG Company View</h3>", unsafe_allow_html=True)
    # Load the CSV
    df = pd.read_sql("SELECT * FROM b_esg_cluster_analyis_actual WHERE data_type = 'actual'", engine)
    df=df.rename(columns={"company_name": "Company"})
    # Group companies by cluster
    clusters = df.groupby("Cluster")["Company"].apply(list).to_dict()

    # Define positions and sizes
    cluster_positions = {
        0: (1, 2),
        1: (4, 2),
        2: (2.5, 0.5)
    }
    cluster_radii = {
        0: 0.5,
        1: 0.5,
        2: 0.5  # Increased from 0.5 to 0.7 to fit longer company name
    }

    # Define cluster colors and legend
    cluster_colors = {
        0: '#00be63',
        1: '#38b6ff',
        2: '#3300f3'
    }

    # Plot
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 3)
    ax.set_xlabel("Principal Component 1")
    ax.set_ylabel("Principal Component 2")


    # Draw circles for each cluster
    for cluster_id, companies in clusters.items():
        x, y = cluster_positions[cluster_id]
        radius = cluster_radii[cluster_id]
        circle = plt.Circle((x, y), radius, color=cluster_colors[cluster_id], ec='black', label=f"Cluster {cluster_id}")
        ax.add_patch(circle)

        # Format the text
        text = f"Cluster {cluster_id}\n" + "\n".join(companies)
        ax.text(x, y, text, color="white", ha="center", va="center", fontsize=6)

    # Remove duplicate legend entries
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="lower right", frameon=True)

    # Display in Streamlit
    st.pyplot(fig)
    
    st.markdown("""
    <p style='text-align: justify; max-width: 1200px; margin: auto; font-size: 18px'>
    <b>Cluster 0 – Energy Majors (BP, TotalEnergies, Aramco, ExxonMobil)</b><br>
    - Companies here show consistent ESG policy adoption with broad stakeholder disclosures.<br>
    - <i>Investor Insight:</i> Reliable ESG reporting, stable risk profiles, suitable for long-term holdings or ESG funds seeking alignment with traditional energy.
    </p>

    <p style='text-align:justify; max-width: 1200px; margin: auto; font-size: 18px'>
    <b>Cluster 1 – Isolated Performer (PetroChina)</b><br>
    - Significantly different ESG posture — either lacking disclosures or deviating on governance.<br>
    - <i>Investor Insight:</i> High due diligence recommended; may pose hidden ESG risks or represent a turnaround opportunity if engagement is effective.
    </p>

    <p style='text-align:justify; max-width: 1200px; margin: auto; font-size: 18px'>
    <b>Cluster 2 – Sustainable Innovators (Shell, NextEra, Chevron, ConocoPhillips)</b><br>
    - Demonstrates proactive climate strategy and tech-driven ESG investments.<br>
    - <i>Investor Insight:</i> Attractive for ESG-forward portfolios, potential for green bond alignment or decarbonization-driven alpha.
    </p>
    """, unsafe_allow_html=True)
#------------------End Of HOME PAGE -----------------

# -------------------------- ESG PERFORMANCE BY COMPANY PAGE -----------------
# ----------------- ESG PERFORMANCE BY COMPANY PAGE -----------------
# Function to initialize the database connection

# Path to the SQL file



# Function to refresh the esg_news table
  # Close the connection

if st.session_state.get("show_company_performance", False):
    # ESG Gradient Background and Bubble Tab Styling
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg,#a8e6cf, #cce5ff, #b3b3ff);
            background-size: 180% 180%;
            animation: gradientBG 10s ease infinite;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Bubble-style tab headers */
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            color: #2c3e50;
            border-radius: 50px !important;
            padding: 10px 24px;
            margin: 0 12px;
            font-weight: bold;
            font-family: 'Poppins', sans-serif;
            font-size: 15px;
            text-transform: uppercase;
            box-shadow: 0 3px 6px rgba(0,0,0,0.1);
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e6f9ec;
            color: #007f5f;
        }

        .stTabs {
            display: flex;
            justify-content: center;
            max-width: 1200px;
            margin: 0 auto 20px auto;
        }
    </style>
    """, unsafe_allow_html=True)

    # Define Tabs with emojis and labels
    tabs = st.tabs([
        "🏢 Company Overview",
        "💰 Financial Impact",
        "📊 Predictive Analysis",
        "🧠 Sentiment & Greenwashing",
        "📰 News"
    ])

    # ---------- Tab 1: Company Overview ----------
    # ---------- Tab 1: Company Overview ----------
    #df_scores.info()
    #df_metrics.info()
    df_scores=df_scores.rename(columns={"company_name": "Company"})
    df_metrics=df_metrics.rename(columns={"Company_name": "Company"})
    if 'Company' in df_scores.columns and 'Company' in df_metrics.columns:
            company_list = sorted(set(df_scores['Company']).intersection(df_metrics['Company']))  # Common companie
    with st.sidebar:
            st.markdown("<div class='sidebar-center'><h4>Select a Company</h4></div>", unsafe_allow_html=True)
            selected_main_company = st.selectbox(
                "Company:",
                company_list,
                key="main_company_selectbox"
            )
            st.session_state["selected_main_company"] = selected_main_company

    with tabs[0]:
        st.markdown("<h1 style='text-align: center; '>♻️ ESG Score Dashboard</h1>", unsafe_allow_html=True)


        if 'Company' in df_scores.columns and 'Company' in df_metrics.columns:
            company_list = sorted(set(df_scores['Company']).intersection(df_metrics['Company']))  # Common companie

            # Filter selected company data
            company_scores= df_scores[df_scores['Company'] == selected_main_company].iloc[0] # Get first row
            company_scores = company_scores.rename({
            "Environmental_Score": "Environmental Score",
            "Social_Score": "Social Score",
            "Governance_Score": "Governance Score",
            "ESG_Score": "ESG Score",
            "ESG_Rating": "ESG Rating",
            "ESG_Rank": "ESG Rank"
            })


            # Extract relevant ESG scores
            esg_scores = {
                "Environmental Score": int(company_scores["Environmental Score"]),
                "Social Score": int(company_scores["Social Score"]),
                "Governance Score": int(company_scores["Governance Score"]),
                "ESG Score": int(company_scores["ESG Score"]),
                "ESG Rating": company_scores["ESG Rating"],
                "ESG Rank": company_scores["ESG Rank"]
            }

            # Underlined company name
            st.markdown(f"##### ESG Performance for <u>{selected_main_company}</u>", unsafe_allow_html=True)

            # Custom CSS for tooltip
            st.markdown("""
            <style>
            .tooltip {
            position: relative;
            display: inline-block;
            cursor: help;
            }

            .tooltip .tooltiptext {
            visibility: hidden;
            width: 220px;
            background-color: #2f2f2f;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -110px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            }

            .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
            }

            .metric-box {
            background-color: #ffffff;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
            font-family: 'Poppins', sans-serif;
            height: 100px;
            }
            .metric-label {
            font-weight: 500;
            font-size: 16px;
            }
            .metric-value {
            font-size: 32px;
            font-weight: 600;
            margin-top: 6px;
            }

            .metric-box1 {
            background-color: #ffffff;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
            font-family: 'Poppins', sans-serif;
            height: 100px;
            }
            .metric-label1 {
            font-weight: 500;
            font-size: 16px;
            }
            .metric-value1 {
            font-size: 32px;
            font-weight: 600;
            margin-top: 6px;
            }
            </style>
            """, unsafe_allow_html=True)

            # Tooltip texts
            tooltips = {
                "Environmental Score": "Environmental impact like emissions, energy usage, waste.",
                "Social Score": "Social practices including labor rights, community relations.",
                "Governance Score": "Corporate governance like board structure and audits.",
                "ESG Score": "Aggregate score across Environmental(40%), Social(30%), and Governance(30%).",
                "ESG Rating": "Standard ESG letter rating based on total score(S&P,Moody Framework).",
                "ESG Rank": "Relative ESG standing among peers."
            }

            def metric_box(label, value, tooltip):
                return f"""
                <div class="metric-box">
                    <div class="metric-label">
                        {label}
                        <span class="tooltip"> ℹ️
                            <span class="tooltiptext">{tooltip}</span>
                        </span>
                    </div>
                    <div class="metric-value">{value}</div>
                </div>
                """
            def metric_box1(label, value):
                return f"""
                <div class="metric-box1">
                    <div class="metric-label1">{label}</div>
                    <div class="metric-value1">{value}</div>
                </div>
                """

            # ESG metrics grid (2 rows)
            col1, col2, col3 = st.columns(3)
            col1.markdown(metric_box("Environmental Score", esg_scores["Environmental Score"], tooltips["Environmental Score"]), unsafe_allow_html=True)
            col2.markdown(metric_box("Social Score", esg_scores["Social Score"], tooltips["Social Score"]), unsafe_allow_html=True)
            col3.markdown(metric_box("Governance Score", esg_scores["Governance Score"], tooltips["Governance Score"]), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)  # One line space
            col4, col5, col6 = st.columns(3)
            col4.markdown(metric_box("ESG Score", esg_scores["ESG Score"], tooltips["ESG Score"]), unsafe_allow_html=True)
            col5.markdown(metric_box("ESG Rating", esg_scores["ESG Rating"], tooltips["ESG Rating"]), unsafe_allow_html=True)
            col6.markdown(metric_box("ESG Rank", esg_scores["ESG Rank"], tooltips["ESG Rank"]), unsafe_allow_html=True)


            st.markdown("<br>", unsafe_allow_html=True)  # One line spaces
            st.markdown("<br>", unsafe_allow_html=True)  # One line space

            # --- ESG ChatGPT-Style Insight (Company-Level) ---
            # --- GPT Insight for Individual Company ESG Scores ---
            #st.markdown("<h3 style='text-align:center; text-transform: none;'>🧠 Company ESG Insight</h3>", unsafe_allow_html=True)

            # Format company ESG metrics for prompting
            company_summary_str = (
                f"Environmental Score: {esg_scores['Environmental Score']}\n"
                f"Social Score: {esg_scores['Social Score']}\n"
                f"Governance Score: {esg_scores['Governance Score']}\n"
                f"ESG Score: {esg_scores['ESG Score']}\n"
                f"ESG Rating: {esg_scores['ESG Rating']}\n"
                f"ESG Rank: {esg_scores['ESG Rank']}"
            )

            # Construct GPT prompt
            company_prompt = (
                f"You are an ESG analyst. Based on the following metrics for {selected_main_company}, "
                f"write a short, one-sentence insight summarizing its ESG performance. "
                f"Be objective, concise, and highlight key strengths or risks:\n\n"
                f"{company_summary_str}"
            )

            # try:
            #     client = os.getenv("OPENAI_API_KEY")
            #     #GPT-4 call (same structure as cluster insight block)
            #     response = client.chat.completions.create(
            #         model="gpt-4",
            #         max_tokens=250,
            #         temperature=0.5,
            #         messages=[
            #             {"role": "system", "content": "You are a concise ESG data analyst."},
            #             {"role": "user", "content": company_prompt}
            #         ]
            #     )

            #     # Display insight
            #     insight = response.choices[0].message.content.strip()

            #     st.markdown("✅ **AI-generated insight below:**")
            #     st.markdown(f"""
            #         <div style='
            #             background-color: #f0f2f6;
            #             padding: 1rem;
            #             margin-top: 0.5rem;
            #             border-radius: 10px;
            #             max-width: 1200px;
            #             margin-left: auto;
            #             margin-right: auto;
            #             font-size: 18px;
            #             line-height: 1.6;
            #             color: #000;
            #             white-space: pre-wrap;
            #             word-wrap: break-word;
            #             text-align: left;
            #         '>{insight}</div>
            #     """, unsafe_allow_html=True)

            # except Exception as e:
            #     st.warning("⚠️ Could not fetch company-level insight. Please check your OpenAI API key.")
            #     st.exception(e)



            # st.markdown("---")

            st.markdown("<h3 style='text-align: center; text-transform: none;'>🌍 ESG Pillar Scores</h3>", unsafe_allow_html=True)
            # Bar chart visualization with custom ESG colors
            esg_chart_data = pd.DataFrame({
                "Category": ["Environmental", "Social", "Governance"],
                "Score": [esg_scores["Environmental Score"], esg_scores["Social Score"], esg_scores["Governance Score"]],
                "Color": ['#00be63', '#38b6ff', '#3300f3']  # Custom colors
            })

            fig = px.bar(
                esg_chart_data,
                x="Category",
                y="Score",
                color="Category",
                labels={"Score": "Score Value"},
                text_auto=True,
                color_discrete_map={
                    "Environmental": "#00be63",
                    "Social": "#38b6ff",
                    "Governance": "#3300f3"
                }
            )
            fig.update_layout(
                        margin=dict(t=20, b=20, l=10, r=10),
                        legend=dict(font=dict(size=12)),
                        showlegend=True
                    )
            with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

            st.plotly_chart(fig, use_container_width=True)

            #st.plotly_chart(fig)

            # Display ESG metrics dataset
        company_metrics = df_metrics[df_metrics['Company'] == selected_main_company]

        st.markdown("---")
        if not company_metrics.empty:
            st.markdown(f"<h3 style='text-align:center; text-transform: none;'>Environmental, Social, and Governance Profile - <u>{selected_main_company}</u></h3>", unsafe_allow_html=True)

            # Define column groups
            env_cols = [col for col in df_metrics.columns if "Environment" in col]
            soc_cols = [col for col in df_metrics.columns if "Social" in col]
            gov_cols = [col for col in df_metrics.columns if "Governance" in col]

            def get_pie_data(df, cols):
                """Extract non-NaN values for pie chart."""
                data = df[cols].iloc[0]
                return data.dropna().to_dict()  # Drop NaNs and convert to dict

            def plot_pie(data_dict):
                fig = px.pie(
                    names=list(data_dict.keys()),
                    values=list(data_dict.values()),
                    title=None,
                    hole=0  # keep it 0 for solid pie
                )
                fig.update_layout(
                    width=650,
                    height=500,
                    margin=dict(l=10, r=10, t=20, b=20),  # Reduce all margins
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05  # slightly push legend out
                    )
                )
                return fig
            # Environmental Pie
            if env_cols:
                env_data = get_pie_data(company_metrics, env_cols)
                if env_data:
                    if env_data:
                        st.markdown("<h5 style='text-align:center;text-transform: none;'>🌍 Environmental Metrics</h4>", unsafe_allow_html=True)
                        st.plotly_chart(plot_pie(env_data), use_container_width=True)
                        st.markdown(
                            "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                            "Environment metrics represent the company’s environmental footprint, including greenhouse gas emissions, energy consumption, waste generation, and other resource usage. "
                            "They help investors assess the company’s exposure to environmental risks and its commitment to sustainable practices."
                            "</p>",
                            unsafe_allow_html=True)

            # Social Pie
            if soc_cols:
                soc_data = get_pie_data(company_metrics, soc_cols)
                if soc_data:
                    st.markdown("<h5 style='text-align:center; text-transform: none;'>🤝 Social Metrics</h5>", unsafe_allow_html=True)
                    st.plotly_chart(plot_pie(soc_data), use_container_width=True)
                    st.markdown(
                        "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                        "Social metrics evaluate how the company manages relationships with employees, customers, suppliers, and the communities in which it operates. "
                        "Investors use these indicators to understand workforce well-being, diversity, human rights policies, and social license to operate."
                        "</p>",
                        unsafe_allow_html=True)

            # Governance Pie
            if gov_cols:
                gov_data = get_pie_data(company_metrics, gov_cols)
                if gov_data:
                    st.markdown("<h3 style='text-align:center; text-transform: none;'>🏛 Governance Metrics</h4>", unsafe_allow_html=True)
                    st.plotly_chart(plot_pie(gov_data), use_container_width=True)
                    st.markdown(
                        "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                        "Governance metrics reflect the company's leadership structure, business ethics, board diversity, and transparency in decision-making. "
                        "These indicators are crucial for investors to evaluate the effectiveness of corporate oversight and risk management frameworks."
                        "</p>",
                        unsafe_allow_html=True
                    )
        else:
            st.error("Dataset does not contain a 'Company' column or no data found for the selected company.")

        # Function to fetch yahoo ESG data from the database

    def fetch_esg_scores_from_db(selected_company, engine):
        """Fetch ESG scores (actual) for a selected company using SQLAlchemy engine."""
        try:
            query = """
                SELECT *
                FROM b_esg_actual_score
                WHERE company_name = %s AND data_type = 'actual'
                LIMIT 1
            """
            df = pd.read_sql(query, engine, params=(selected_company,))
            return df
        except Exception as e:
            st.error(f"Error fetching ESG scores: {e}")
            return pd.DataFrame()


    def fetch_esg_metrics_from_db(selected_company,engine):
        """Fetch detailed ESG metrics (Environment, Social, Governance) from the database."""
        try:
            query = """
                    SELECT *
                    FROM b_esg_metric_data_extracted
                    WHERE "Company_name" = %s
                    LIMIT 1
                """
            df = pd.read_sql_query(query, engine, params=(selected_company,))
            return df
        except Exception as e:
                st.error(f"Error fetching ESG metrics: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def get_esg_from_yahoo_db(selected_company,engine):
        """Fetch ESG data from Yahoo Financial database for comparison, extracting from JSON."""
        try:
            query = """
                    SELECT
                        json_content->>'totalEsg' AS "ESG Score",
                        json_content->>'environmentScore' AS "Environment Score",
                        json_content->>'socialScore' AS "Social Score",
                        json_content->>'governanceScore' AS "Governance Score"
                    FROM external_source
                    WHERE company_name = %s
                """
            df = pd.read_sql_query(query, engine, params=(selected_company,))


                # Convert string values to float or int
            if not df.empty:
                esg_data = df.iloc[0].to_dict()
                esg_data["ESG Score"] = float(esg_data["ESG Score"]) if esg_data["ESG Score"] else 0
                esg_data["Environment Score"] = float(esg_data["Environment Score"]) if esg_data["Environment Score"] else 0
                esg_data["Social Score"] = float(esg_data["Social Score"]) if esg_data["Social Score"] else 0
                esg_data["Governance Score"] = float(esg_data["Governance Score"]) if esg_data["Governance Score"] else 0
                return esg_data
        except Exception as e:
                st.error(f"Error fetching data from Yahoo Financial: {e}")
                return {}
        return {}

    # Function to generate a metric box with a tooltip
    def metric_box(label, value, tooltip):
        return f"""
        <div style="background:#fff;padding:10px;border-radius:8px;text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);font-family:'Poppins';">
            <div style="font-weight:500;font-size:16px;">
                {label}
                <span class="tooltip"> ℹ️
                    <span class="tooltiptext">{tooltip}</span>
                </span>
            </div>
            <div style="font-size:28px;font-weight:600;margin-top:6px;">{value}</div>
        </div>
        """
    # Function to plot pie chart
    def plot_pie_chart(data_dict):
        """Generate a pie chart using the given data."""
        fig = px.pie(
            names=list(data_dict.keys()),
            values=list(data_dict.values()),
            hole=0  # keep it solid
        )
        fig.update_layout(
            width=650,
            height=500,
            margin=dict(l=10, r=10, t=20, b=20),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        return fig

    with tabs[0]:
        #st.markdown("<h1 style='text-align: center;'>♻️ ESG Score Dashboard</h1>", unsafe_allow_html=True)

        selected_main_company = st.session_state.get("selected_main_company")

        if selected_main_company:
            try:
                # Fetch ESG scores for the selected company from the ESG Scores table
                esg_scores_df = fetch_esg_scores_from_db(selected_main_company,engine)

                if not esg_scores_df.empty:
                    row = esg_scores_df.iloc[0]
                    esg_scores = {
                        "Environmental Score": int(row["Environmental_Score"]),
                        "Social Score": int(row["Social_Score"]),
                        "Governance Score": int(row["Governance_Score"]),
                        "ESG Score": int(row["ESG_Score"]),
                        "ESG Rating": row["ESG_Rating"],
                        "ESG Rank": row["ESG_Rank"]
                    }

                    # Tooltips for each metric
                    tooltips = {
                        "Environmental Score": "Environmental impact like emissions, energy usage, waste.",
                        "Social Score": "Social practices including labor rights, community relations.",
                        "Governance Score": "Corporate governance like board structure and audits.",
                        "ESG Score": "Aggregate score across Environmental (40%), Social (30%), and Governance (30%).",
                        "ESG Rating": "Standard ESG letter rating based on total score (S&P, Moody Framework).",
                        "ESG Rank": "Relative ESG standing among peers."
                    }

                    # # Metric Display for ESG Scores
                    # col1, col2, col3 = st.columns(3)
                    # col1.markdown(metric_box("Environmental Score", esg_scores["Environmental Score"], tooltips["Environmental Score"]), unsafe_allow_html=True)
                    # col2.markdown(metric_box("Social Score", esg_scores["Social Score"], tooltips["Social Score"]), unsafe_allow_html=True)
                    # col3.markdown(metric_box("Governance Score", esg_scores["Governance Score"], tooltips["Governance Score"]), unsafe_allow_html=True)

                    # st.markdown("<br>", unsafe_allow_html=True)
                    # col4, col5, col6 = st.columns(3)
                    # col4.markdown(metric_box("ESG Score", esg_scores["ESG Score"], tooltips["ESG Score"]), unsafe_allow_html=True)
                    # col5.markdown(metric_box("ESG Rating", esg_scores["ESG Rating"], tooltips["ESG Rating"]), unsafe_allow_html=True)
                    # col6.markdown(metric_box("ESG Rank", esg_scores["ESG Rank"], tooltips["ESG Rank"]), unsafe_allow_html=True)

                    # st.markdown("---")

                    # --- Pie Charts for ESG Pillars ---
                    #st.markdown("<h3 style='text-align:center; text-transform: none;'>📊 ESG Pillar Breakdown</h3>", unsafe_allow_html=True)
                    score_df = pd.DataFrame({
                        "Category": ["Environmental", "Social", "Governance"],
                        "Score": [esg_scores["Environmental Score"], esg_scores["Social Score"], esg_scores["Governance Score"]]
                    })
                    fig = px.bar(score_df, x="Category", y="Score", color="Category",
                                color_discrete_map={"Environmental": "#00be63", "Social": "#38b6ff", "Governance": "#3300f3"})
                    #st.plotly_chart(fig, use_container_width=True)

                    # --- Fetch ESG Metrics for detailed breakdown ---
                    esg_metrics_df = fetch_esg_metrics_from_db(selected_main_company,engine)

                    if not esg_metrics_df.empty:
                        metrics_row = esg_metrics_df.iloc[0]
                        # Example for displaying specific metrics:
                        environment_metrics = {
                            "GHG ETT": metrics_row.get("E01_GHG_ETT"),
                            "GHG ITP": metrics_row.get("E02_GHG_ITP"),
                            "Land": metrics_row.get("E03_Land"),
                            "Bio": metrics_row.get("E04_Bio"),
                            "Water C": metrics_row.get("E05_Water_C"),
                            "Water W": metrics_row.get("E06_Water_W"),
                            "Electronic W": metrics_row.get("E07_Electronic_W"),
                            "Pkg M W": metrics_row.get("E08_Pkg_M_W"),
                            "Air P": metrics_row.get("E09_Air_P"),
                            "Toxic Waste": metrics_row.get("E10_Toxic_W"),
                            "Opp RE": metrics_row.get("E11_Opp_RE")
                        }
                        social_metrics = {
                            "HR": metrics_row.get("S01_HR"),
                            "PR": metrics_row.get("S02_PR"),
                            "HSI": metrics_row.get("S03_HSI"),
                            "HSF": metrics_row.get("S04_HSF"),
                            "TH": metrics_row.get("S05_TH"),
                            "CR": metrics_row.get("S06_CR")
                        }
                        governance_metrics = {
                            "Board Diversity": metrics_row.get("G01_BD"),
                            "BI": metrics_row.get("G02_BI"),
                            "P": metrics_row.get("G03_P"),
                            "Acct": metrics_row.get("G04_Acct"),
                            "BE": metrics_row.get("G05_BE"),
                            "Tax T": metrics_row.get("G06_Tax_T"),
                            "Vote R": metrics_row.get("G07_Vote_R")
                        }

                        # st.markdown("<h3 style='text-align:center; text-transform: none;'>📋 Detailed ESG Metrics</h3>", unsafe_allow_html=True)
                        # Environmental Section
                        st.markdown("<h3 style='text-align:center;text-transform: none;'>🌍 Environmental Metrics</h3>", unsafe_allow_html=True)
                        st.plotly_chart(plot_pie_chart(environment_metrics), use_container_width=True)
                        st.markdown(
                            "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                            "Environment metrics represent the company’s environmental footprint, including greenhouse gas emissions, energy consumption, waste generation, and other resource usage. "
                            "They help investors assess the company’s exposure to environmental risks and its commitment to sustainable practices."
                            "</p>",
                            unsafe_allow_html=True)
                        
                        

                        # Social Section
                        st.markdown("<h3 style='text-align:center; text-transform: none;'>🤝 Social Metrics</h3>", unsafe_allow_html=True)
                        st.plotly_chart(plot_pie(social_metrics), use_container_width=True)
                        st.markdown(
                            "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                            "Social metrics evaluate how the company manages relationships with employees, customers, suppliers, and the communities in which it operates. "
                            "Investors use these indicators to understand workforce well-being, diversity, human rights policies, and social license to operate."
                            "</p>",
                            unsafe_allow_html=True)
                        
                        # Governance Section
                        st.markdown("<h3 style='text-align:center; text-transform: none;'>🏛 Governance Metrics</h4>", unsafe_allow_html=True)
                        st.plotly_chart(plot_pie(governance_metrics), use_container_width=True)
                        st.markdown(
                            "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                            "Governance metrics reflect the company's leadership structure, business ethics, board diversity, and transparency in decision-making. "
                            "These indicators are crucial for investors to evaluate the effectiveness of corporate oversight and risk management frameworks."
                            "</p>",
                            unsafe_allow_html=True
                        )
                        

                    # --- Fetch ESG Data from Yahoo Finance for comparison ---
                    esg_scores_db = get_esg_from_yahoo_db(selected_main_company,engine)

                    st.markdown("---")
                    if esg_scores_db:
                        # Display ESG scores from Yahoo Financial
                        st.markdown("<h3 style='text-align:center; text-transform: none;'>💹 ESG Score by Yahoo Financial</h3>", unsafe_allow_html=True)
                        col1, col2, col3, col4 = st.columns(4)
                        col1.markdown(metric_box("ESG Score", esg_scores_db['ESG Score'], tooltips["ESG Score"]), unsafe_allow_html=True)
                        col2.markdown(metric_box("Environmental Score", esg_scores_db['Environment Score'], tooltips["Environmental Score"]), unsafe_allow_html=True)
                        col3.markdown(metric_box("Social Score", esg_scores_db['Social Score'], tooltips["Social Score"]), unsafe_allow_html=True)
                        col4.markdown(metric_box("Governance Score", esg_scores_db['Governance Score'], tooltips["Governance Score"]), unsafe_allow_html=True)

                        
                        
                        # col1.markdown(f"**ESG Score**: {esg_scores_db['ESG Score']}")
                        # col2.markdown(f"**Environment Score**: {esg_scores_db['Environment Score']}")
                        # col3.markdown(f"**Social Score**: {esg_scores_db['Social Score']}")
                        # col4.markdown(f"**Governance Score**: {esg_scores_db['Governance Score']}")

                        # Comparison Table between CTRL+Sustain and Yahoo Financial
                        st.markdown("<br>", unsafe_allow_html=True)  # One line spaces
                        st.markdown("<h4 style='text-align:center; text-transform: none;,'>⚖️ ESG Score Comparison (Calculated vs Yahoo Financial)</h4>", unsafe_allow_html=True)
                        comparison_data = {
                            "Category": ["ESG Score", "Social Score", "Governance Score", "Environment Score"],
                            "CTRL+Sustain Data": [
                                esg_scores["ESG Score"],
                                esg_scores["Social Score"],
                                esg_scores["Governance Score"],
                                esg_scores["Environmental Score"]
                            ],
                            "Yahoo Financial Data": [
                                esg_scores_db["ESG Score"],
                                esg_scores_db["Social Score"],
                                esg_scores_db["Governance Score"],
                                esg_scores_db["Environment Score"]
                            ]
                        }

                        df_comparison = pd.DataFrame(comparison_data)

                        # Apply styles based on comparison
                        def highlight_scores_text(row):
                            csv_val = row["CTRL+Sustain Data"]
                            yahoo_val = row["Yahoo Financial Data"]
                            csv_color = "color: green; font-weight:bold;" if csv_val > yahoo_val else "color: red; font-weight:bold;"
                            yahoo_color = "color: green; font-weight:bold;" if yahoo_val > csv_val else "color: red; font-weight:bold;"
                            return ["text-align: center;", csv_color + " text-align: center;", yahoo_color + " text-align: center;"]

                        # Apply styling to DataFrame
                        styled_df = (
                            df_comparison.style
                            .apply(highlight_scores_text, axis=1)
                            .set_table_styles([
                                {"selector": "thead th", "props": [("font-weight", "bold"), ("text-align", "center"), ("border", "none")]},
                                {"selector": "tbody td", "props": [("text-align", "center"), ("border", "none")]},
                                {"selector": "tbody th", "props": [("border", "none")]},
                                {"selector": "table", "props": [("border-collapse", "collapse"), ("width", "100%")]}
                            ])
                        )

                        # Display styled DataFrame without index
                        st.dataframe(styled_df.hide(axis="index"), use_container_width=True)

                        # Plot the comparison chart
                        st.markdown("<br>", unsafe_allow_html=True)  # One line space
                        st.markdown("<h4 style='text-align:center;,'>📊 ESG Score Comparison (Calculated vs Yahoo Financial)</h4>", unsafe_allow_html=True)
                        df_melted = df_comparison.melt(id_vars="Category", var_name="Source", value_name="Score")
                        fig = px.bar(df_melted, x="Category", y="Score", color="Source", barmode="group")
                        fig.update_layout(
                            margin=dict(t=20, b=20, l=10, r=10),
                            legend=dict(font=dict(size=12)),
                            showlegend=True
                        )
                        with st.container():
                            st.markdown(
                                """
                                <style>
                                .custom-container {
                                    max-width: 1200px;
                                    margin: auto;
                                }
                                </style>
                                <div class="custom-container">
                                """,
                                unsafe_allow_html=True
                            )

                        st.plotly_chart(fig, use_container_width=True)
                        # Description paragraph
                        st.markdown(
                            "<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>"
                            "This bar chart provides a side-by-side comparison of ESG scores derived from internal calculations against publicly available data from Yahoo Financial. "
                            "It highlights discrepancies or alignment between different data sources across Environmental, Social, and Governance categories."
                            "</p>",
                            unsafe_allow_html=True
                        )

                    else:
                        st.warning(f"No ESG data found in the database (Yahoo Financial) for {selected_main_company}")
                else:
                    st.warning(f"No ESG data found for {selected_main_company}.")
            except Exception as e:
                st.error(f"❌ Failed to load ESG scores: {e}")
        else:
            st.info("Please select a company from the sidebar.")

    # ---------- Tab 2: Financial Impact ----------
    with tabs[1]:
        st.markdown("<h1 style='text-align: center;'>📊 Financial Impact by Company</h1>", unsafe_allow_html=True)
        merged_df = pd.read_sql("SELECT * FROM b_esg_merged_financial_metrics ", engine)
        merged_df = merged_df.rename(columns={
            "company_name": "Company",
            "environmental_score": "Environmental Score",
            "social_score": "Social Score",
            "governance_score": "Governance Score",
            "roe": "ROE (%)",
            "roa": "ROA (%)",
            "1Y_Stock_Return": "1Y Stock Return (%)"
        })

        esg_components = ["Environmental Score", "Social Score", "Governance Score"]
        targets = ["ROE (%)", "ROA (%)", "1Y Stock Return (%)"]

        selected_company = st.session_state.get("selected_main_company")

        if not selected_company:
            st.warning("Please select a company from the sidebar to view financial impact.")
            st.stop()

        trained_models = {}
        feature_importances = {}
        
        for i, target in enumerate(targets):
            if i > 0:
                st.markdown("---")  # 🔹 Horizontal divider between sections

            st.markdown(f"<h3 style='text-align: center; text-transform: none;'>{target} Prediction</h3>", unsafe_allow_html=True)
            
            # Insert R² & RMSE explanation per metric
            if target == "ROE (%)":
                st.markdown("""
                <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                <b>R² Score</b> indicates how much of the variation in Return on Equity (ROE) can be explained by ESG scores, while 
                <b>RMSE</b> reflects the average prediction error of the model. A higher R² and lower RMSE suggest a stronger link between ESG practices and capital efficiency. 
                This analysis helps companies understand how well-governed, socially responsible, and environmentally conscious operations may contribute to maximizing shareholder value.
                </p>
                """, unsafe_allow_html=True)
            elif target == "ROA (%)":
                st.markdown("""
                <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                <b>R² Score</b> shows how much of the variability in Return on Assets (ROA) can be accounted for by ESG factors, while 
                <b>RMSE</b> quantifies the average prediction error. These metrics evaluate how effectively ESG performance translates into operational efficiency. 
                Companies can leverage this to identify which sustainability practices improve asset utilization and long-term profitability.
                </p>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                <b>R² Score</b> measures how well ESG scores explain the variance in 1-Year Stock Return, while 
                <b>RMSE</b> represents the average prediction error. These metrics indicate how market performance may be influenced by ESG profiles. 
                Companies can use these insights to align sustainability efforts with investor expectations and market sentiment, enhancing shareholder trust.
                </p>
                """, unsafe_allow_html=True)
            features = esg_components
            data = merged_df[features + [target]].dropna()
            X = data[features]
            y = data[target]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

            rf = RandomForestRegressor(random_state=1)
            rf.fit(X_train, y_train)
            y_pred_rf = rf.predict(X_test)

            r2 = r2_score(y_test, y_pred_rf)
            rmse = mean_squared_error(y_test, y_pred_rf) ** 0.5

            # Create the DataFrame
            score_table = pd.DataFrame({
                "Metric": ["R² Score", "RMSE"],
                "Value": [round(r2, 2), round(rmse, 2)]
            })

            # Custom CSS for dark borders and black text
            st.markdown("""
                <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 2px solid #333333 !important;  /* Dark borders */
                    padding: 8px;
                    text-align: center;
                    color: black !important;               /* Black text */
                }
                </style>
            """, unsafe_allow_html=True)

            # Render the table
            st.table(score_table)

            trained_models[target] = rf
            feature_importances[target] = rf.feature_importances_

            color_map = {
                "Environmental Score": "#00be63",
                "Social Score": "#38b6ff",
                "Governance Score": "#3300f3",
            }

            importance_df = pd.DataFrame({
                'Feature': esg_components,
                'Importance': rf.feature_importances_,
                'Color': [color_map[feat] for feat in esg_components]
            })

            st.markdown(f"<h4 style='text-align:center;'>🔍 Feature Importance for {target}</h4>", unsafe_allow_html=True)

            fig = px.bar(
                importance_df,
                x='Feature',
                y='Importance',
                color='Feature',
                color_discrete_map=color_map,
                labels={'Feature': 'ESG Component', 'Importance': 'Importance Score'}
            )
            fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), showlegend=False)
            with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

            st.plotly_chart(fig, use_container_width=True)

            # Feature importance explanation
            if target == "ROE (%)":
                feature_desc = (
                    "This chart identifies which ESG components most significantly influence Return on Equity (ROE). "
                    "Higher importance of governance-related factors may suggest that strong corporate oversight and ethical leadership are key drivers of capital efficiency and investor returns."
                )
            elif target == "ROA (%)":
                feature_desc = (
                    "This feature importance chart highlights the ESG elements that contribute most to Return on Assets (ROA). "
                    "A strong environmental score, for example, may indicate that responsible resource management and operational efficiency are pivotal in maximizing asset-driven returns."
                )
            else:
                feature_desc = (
                    "This chart shows how ESG dimensions contribute to predicting 1-Year Stock Return. "
                    "Greater weight on social or environmental scores may reflect the market’s responsiveness to corporate sustainability, stakeholder engagement, and long-term risk mitigation."
                )

            st.markdown(
                f"<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>{feature_desc}</p>",
                unsafe_allow_html=True
            )

            # Actual vs Predicted
            actual = merged_df[merged_df['Company'] == selected_company][target].values[0]
            predicted = rf.predict(merged_df[merged_df['Company'] == selected_company][esg_components])[0]

            comparison_df = pd.DataFrame({
                'Type': ['Actual', 'Predicted'],
                'Value': [actual, predicted]
            })
            st.markdown("<br>", unsafe_allow_html=True)  # One line space

            st.markdown(f"<h4 style='text-align:center;'>📊 Actual vs Predicted {target} for {selected_company}</h4>", unsafe_allow_html=True)

            fig2 = px.bar(
                comparison_df,
                x='Type',
                y='Value',
                color='Type',
                color_discrete_map={"Actual": "#e74c3c", "Predicted": "green"},
                labels={'Type': 'Data Type', 'Value': target}
            )
            fig2.update_layout(margin=dict(t=20, b=20, l=10, r=10), showlegend=False)
            with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

            st.plotly_chart(fig2, use_container_width=True)
            

            # Actual vs Predicted explanation
            if target == "ROE (%)":
                explanation = (
                    "Return on Equity (ROE) measures a company's ability to generate profits from shareholder investments. "
                    "This model estimates the impact of Environmental, Social, and Governance (ESG) factors on ROE, offering insights into how sustainable practices may enhance capital efficiency and shareholder value."
                )
            elif target == "ROA (%)":
                explanation = (
                    "Return on Assets (ROA) reflects how effectively a company utilizes its assets to drive earnings. "
                    "By linking ESG metrics to ROA, this forecast provides investors with a view of how operational sustainability and responsible resource management may translate into improved financial performance."
                )
            else:  # "1Y Stock Return (%)"
                explanation = (
                    "The 1-Year Stock Return represents the total return to shareholders over a one-year period. "
                    "This prediction explores how ESG scores influence market valuation, highlighting the potential for companies with strong sustainability profiles to outperform by attracting investor confidence and reducing long-term risks."
                )

            st.markdown(
                f"<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>{explanation}</p>",
                unsafe_allow_html=True
            )


    # ---------- Tab 3: Predictive Analysis ----------
    with tabs[2]:
        # 📌 Indicator Descriptions
        

        st.markdown("<h1 style='text-align: center;'>📈 Predictive Analysis</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; text-transform: none;'>Predictive Trend of <u>{selected_main_company}</u></h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>ESG performance from 2014 to 2024, capturing key Environmental, Social, and Governance indicators across a 10-year span. The 2024 values are model-generated predictions, calculated using a rolling 3-year window—for example, data from 2021 to 2023 is used to forecast 2024 outcomes. This approach enables accurate trend analysis and forward-looking insights for sustainability strategy and risk evaluation.</u></p>", unsafe_allow_html=True)

        df =pd.read_sql("SELECT * FROM conoco_predictions ", engine)
        df = df.rename(columns={"category": "Category"})
        df = df.rename(columns={"indicator": "Indicator"})
        # Remove commas in large numbers, if any
        for col in df.columns[2:]:
            df[col] = df[col].astype(str).str.replace(",", "")
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Melt for plotting
        df_melted = df.melt(id_vars=["Category", "Indicator"], var_name="Year", value_name="Value")
        df_melted["Year"] = df_melted["Year"].astype(str)  # Treat years as categorical

        # Sidebar filters
        st.sidebar.title("🔍 ESG Filters")
        selected_trend_category = st.sidebar.selectbox("Select Category", df_melted["Category"].unique(), key="trend_category_dropdown")

        filtered_indicators = df_melted[df_melted["Category"] == selected_trend_category]["Indicator"].unique()
        selected_indicators = st.sidebar.multiselect("Select Indicator(s)", filtered_indicators, default=list(filtered_indicators))

        # Subheader
        st.markdown(f"<h4 style='text-align: center; text-transform: none;'>Category: {selected_trend_category}</u></h4>", unsafe_allow_html=True)

        # Plotting
        for indicator in selected_indicators:
            data = df_melted[
                (df_melted["Category"] == selected_trend_category) &
                (df_melted["Indicator"] == indicator)
            ]

            # Title above chart
            st.markdown(f"<h5 style='text-align: center; text-transform: none'>{indicator}</h5>", unsafe_allow_html=True)
            #st.write("DEBUG:", selected_trend_category, indicator)

            # Description below title
            description_map = {
                "Environmental": {
                    "GHG emissions-total (tCO2e)": "Forecasted total greenhouse gas emissions, reflecting projected carbon footprint and regulatory risk exposure.",
                    "GHG intensity (tCO2e/production)": "Predicted emissions relative to output, indicating future operational efficiency and carbon productivity.",
                    "Biodiversity impacts (Barrels)": "Projected impact of operations on ecosystems, relevant for assessing future reputational and regulatory risks.",
                    "Water consumption (m3)": "Expected freshwater use, offering insight into sustainability of operations in water-stressed regions.",
                    "Air pollutant emission-Nox (Metric tonnes)": "Anticipated NOx emissions, helping investors assess exposure to evolving air quality regulations.",
                    "Toxic waste (Metric tonnes)": "Forecasted hazardous waste volumes, reflecting future environmental management efficiency and compliance risks."
                },
                "Social": {
                    "Health & safety-incident (%)": "Predicted incident rates, offering insight into workplace safety culture and future operational disruptions.",
                    "Health & safety-fatality (%)": "Forecasted fatality trends, critical for evaluating risk controls and employee well-being strategies.",
                    "Training (hour/pax)": "Projected investment in workforce development, indicating future talent readiness and ESG maturity."
                },
                "Governance": {
                    "Board diversity (%)": "Anticipated representation diversity at the board level, often linked to enhanced strategic foresight and risk governance.",
                    "Board independence (%)": "Forecasted board independence ratio, relevant for assessing governance strength and investor alignment."
                }
            }


            # Chart (without title inside)
            fig = px.line(
                data,
                x="Year",
                y="Value",
                markers=True,
                labels={"Value": "Value", "Year": "Year"},
                category_orders={"Year": sorted(df_melted["Year"].unique())}
            )
            fig.update_layout(margin=dict(t=25, b=20, l=10, r=10), height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            description = description_map.get(selected_trend_category, {}).get(indicator, "")
            if description:
                st.markdown(f"<p style='text-align: center; max-width: 1000px; font-size: 16px; margin: auto;'>{description}</p>", unsafe_allow_html=True)
                st.markdown("--")
    # ---------- Tab 4: Sentiment & Greenwashing ----------
    # 📥 Fetch sentiment + greenwashing data from NeonDB
    # Function to initialize the database connection with better error handling for sentiment and greenwashing
    def get_sentiment_connection():
        try:
            conn = psycopg2.connect(DB_URL)  # Using db URL directly or replace with your connection details
            return conn
        except psycopg2.OperationalError as e:
            st.error(f"Error connecting to the database: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred while connecting: {e}")
            return None

    # Query Function for Sentiment & Greenwashing Data
    def get_sentiment_data(company_name):
        try:
            conn = get_sentiment_connection()
            if conn:
                query = """
                    SELECT company, sentiment_label, sentiment_score, esg_category, greenwashing_risk
                    FROM esg_sentiment
                    WHERE LOWER(company) = %s
                """
                sentiment_df = pd.read_sql_query(query, conn, params=(company_name.lower(),))
                conn.close()  # Close the connection
                return sentiment_df
        except Exception as e:
            st.error(f"❌ Failed to load sentiment data: {e}")
            return pd.DataFrame()


    with tabs[3]:
        st.markdown("<h1 style='text-align: center;'>🔍Sentiment & Greenwashing Analysis</h1>", unsafe_allow_html=True)

        selected_main_company = st.session_state.get("selected_main_company")

        if selected_main_company:
            sentiment_df = get_sentiment_data(selected_main_company)

            if not sentiment_df.empty:
                    st.markdown("<h3 style='text-align: center; text-transform: none;'>📊 Distribution of Sentiment Intensity Buckets</h3>", unsafe_allow_html=True)

                    sentiment_counts = sentiment_df['sentiment_label'].value_counts().reset_index()
                    sentiment_counts.columns = ['sentiment_label', 'Count']

                    fig = px.bar(
                        sentiment_counts,
                        x="sentiment_label",
                        y="Count",
                        color="sentiment_label",
                        color_discrete_map={
                            "positive": "green",
                            "neutral": "#f1c40f",
                            "negative": "red"
                        }
                    )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=10, r=10),
                        
                    )
                    with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

                    st.plotly_chart(fig, use_container_width=True)

                    

                    st.markdown("""<p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                    This chart displays how stakeholder communications related to the company are distributed across positive, neutral, and negative sentiment categories. A higher share of positive sentiment generally reflects stronger public perception and reputational advantage.
                    </p>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

                    st.markdown("<h3 style='text-align: center;text-transform: none;'>🌡️ Sentiment Distribution by ESG Category</h3>", unsafe_allow_html=True)

                    sentiment_group = sentiment_df.groupby(['esg_category', 'sentiment_label']).size().reset_index(name='Count')
                    heatmap_data = sentiment_group.pivot(index='esg_category', columns='sentiment_label', values='Count')

                    fig = px.imshow(
                        heatmap_data,
                        labels=dict(x="Sentiment", y="ESG Category", color="Count"),
                        color_continuous_scale="YlGnBu"
                    )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=10, r=10),
                    )
                    with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

                    st.plotly_chart(fig, use_container_width=True)
                    

                    st.markdown("""
                    <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                    This heatmap illustrates how sentiment varies across ESG categories. It helps to identify which areas—Environmental, Social, or Governance—are generating more negative or positive discourse.
                    </p>
                    """, unsafe_allow_html=True)
                    st.markdown("---")

                    st.markdown("<h3 style='text-align: center; text-transform: none;'>📈 Average Sentiment Score by ESG Category</h3>", unsafe_allow_html=True)
                    avg_sentiment = sentiment_df.groupby("esg_category")["sentiment_score"].mean().reset_index()
                    fig = px.bar(
                        avg_sentiment,
                        x="esg_category",
                        y="sentiment_score",
                        color="esg_category",
                        labels={'Sentiment Score': 'Average Sentiment Score', 'ESG Category': 'ESG Category'},
                        color_discrete_map={
                            "Environment": "#00be63",
                            "Social": "#38b6ff",
                            "Governance": "#3300f3"
                        }
                        )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=10, r=10),
                    )
                    with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

                    st.plotly_chart(fig, use_container_width=True)

                    
                    st.markdown("""
                    <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                    This chart presents the average sentiment score across ESG pillars. Scores closer to 1 indicate more positive sentiment, guiding confidence in how the company is perceived in each ESG area.
                    </p>
                    """, unsafe_allow_html=True)
                    st.markdown("---")

                    st.markdown("<h3 style='text-align: center; text-transform: none;'>🚨 Potential Greenwashing Risk Distribution</h3>", unsafe_allow_html=True)
                    greenwashing_counts = sentiment_df['greenwashing_risk'].value_counts()
                    fig = px.pie(
                        names=greenwashing_counts.index,
                        values=greenwashing_counts.values,
                        width=800,
                        height=350
                    )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=10, r=10),
                        legend=dict(font=dict(size=12)),
                        showlegend=True
                    )
                    with st.container():
                        st.markdown(
                            """
                            <style>
                            .custom-container {
                                max-width: 1200px;
                                margin: auto;
                            }
                            </style>
                            <div class="custom-container">
                            """,
                            unsafe_allow_html=True
                        )

                    st.plotly_chart(fig, use_container_width=True)


                    st.markdown("""
                    <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                    This pie chart reflects the distribution of greenwashing risk labels across analyzed disclosures.
                    It provides an early indicator of potential ESG misrepresentation that may influence due diligence and risk assessments.
                    </p>
                    """, unsafe_allow_html=True)

                    st.markdown("---")

            else:
                st.warning("No sentiment/greenwashing data found for the selected company.")

# ---------- Tab 5: News ----------

    def get_recent_esg_news(company_name):
        try:
            conn = get_sentiment_connection()
            query = """
                SELECT DISTINCT ON (news_title) news_title, url, published_date
                FROM esg_news
                WHERE LOWER(company) = %s
                ORDER BY news_title, published_date DESC
                LIMIT 10
            """
            df = pd.read_sql_query(query, conn, params=(company_name.lower(),))
            conn.close()
            return df
        except Exception as e:
            st.error(f"❌ Failed to load ESG news: {e}")
            return pd.DataFrame()

    with tabs[4]:
        st.markdown("<h1 style='text-align: center;'>📰 Recent News Articles</h1>", unsafe_allow_html=True)
        st.markdown("""
                    <p style='text-align: center; max-width: 1200px; font-size: 18px; margin: auto;'>
                    Stay informed with the latest news articles related to ESG, sustainability, and corporate responsibility.
                    </p>
                    """, unsafe_allow_html=True)

        selected_main_company = st.session_state.get("selected_main_company")

        if selected_main_company:
            news_df = get_recent_esg_news(selected_main_company)

            if not news_df.empty:
                for _, row in news_df.iterrows():
                    st.markdown(f"🔗 **[{row['news_title']}]({row['url']})**  \n🗓️ {row['published_date']}")
            else:
                st.info(f"No news articles found for {selected_main_company}.")
        else:
            st.info("Please select a company from the sidebar.")

# ------------------------ CHATBOT SECTION ------------------------ #
st.markdown("""
    <style>
    .chat-popup {
        position: fixed;
        bottom: 100px;
        right: 40px;
        border: 2px solid #ccc;
        background-color: white;
        z-index: 9;
        width: 350px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border-radius: 10px;
    }
    .chat-button {
        position: fixed;
        bottom: 30px;
        right: 40px;
        z-index: 10;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize message state
if "messages" not in st.session_state:
    st.session_state.messages = []

def respond_to_query_with_gpt(query):
    # Sample top 5 rows from ESG scores
    company_col = "Company" if "Company" in df_scores.columns else "company_name"
    df_summary_scores = df_scores[[
        company_col, "Environmental_Score", "Social_Score", "Governance_Score", "ESG_Score", "ESG_Rating"
    ]].head(5)

    df_summary_metrics = df_metrics.head(3)  # First 3 rows for brevity

    # Convert to string (markdown-style table preview)
    score_text = df_summary_scores.to_markdown(index=False)
    metric_text = df_summary_metrics.to_markdown(index=False)

    # # Construct prompt
    # prompt = (
    #     "You are an ESG data analyst. Use the ESG performance data below to respond factually to user queries.\n\n"
    #     "### ESG Score Snapshot (Top 5 companies):\n"
    #     f"{score_text}\n\n"
    #     "### ESG Metrics Snapshot (Top 3 rows):\n"
    #     f"{metric_text}\n\n"
    #     f"User Query: {query}"
    # )

    # # Query GPT
    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": "Answer using only the ESG data provided. Be concise and analytical."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.4,
    #     max_tokens=200
    # )
    # return response.choices[0].message.content.strip()

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box at the bottom
if user_input := st.chat_input("Ask something about ESG scores, performance, or trends..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = respond_to_query_with_gpt(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

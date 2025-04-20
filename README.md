# 🧠 Automating ESG Insights: Data Extraction and Performance Analysis  
**DSS5105 — Data Science Projects in Practice**  
*Semester 2, AY2024/25*

---

## 📘 Project Overview

This project focuses on automating the extraction of ESG (Environmental, Social, and Governance) insights from unstructured corporate reports using advanced NLP techniques. It supports ESG analysts, investors, and regulators by enhancing the speed, accuracy, and usability of ESG data, offering industry-aligned benchmarking and interactive dashboards for performance insights.
Video: https://www.youtube.com/watch?v=yNcdobaMEGo

---

## ⚙️ Backend Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/xuanntm/5105_development.git
   cd 5105_development
   ```

2. **Set Up a Python Virtual Environment**
   ```bash
   python -m venv .venv
   ```

   - **Activate on macOS/Linux:**  
     `source .venv/bin/activate`
   - **Activate on Windows:**  
     `.venv\Scripts\activate`

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**  
   Create a `.env` file in the root directory with the following entries:
   ```
   SQLALCHEMY_DATABASE_URI=postgresql://admin:admin@127.0.0.1:54320/postgres
   NEWSAPI_KEY={{YOUR_NEWS_API_KEY}}
   BING_API_KEY={{YOUR_BING_API_KEY}}
   ```

5. **Download Pre-trained Models**
   ```bash
   python src/config/model_config.py
   ```

6. **Launch Backend Server**
   ```bash
   python backend_app.py
   ```
   - Backend Endpoint: [http://localhost:5000/](http://localhost:5000/)

---

### 🛠 Database Setup

**Dictionary Tables**
- `esg_index_metric`
- `esg_benchmark`
- `company_profile`
- `b_esg_cluster_analyis_actual_demo`
- `b_esg_financial_metrics`
- `b_esg_merged_financial_metrics`
- `b_esg_metric_data_extracted`
- `b_esg_with_trend_features`

**Output Tables**
- `report_history`
- `external_source`
- `esg_sentiment`
- `esg_news`
- `b_esg_actual_score`

**Switching Between LocalDB and NeonDB**
1. Stop any running backend service:
   ```bash
   Ctrl + C
   ```
2. Update `.env` with the new `SQLALCHEMY_DATABASE_URI`
3. Clear environment variable cache:
   ```bash
   unset SQLALCHEMY_DATABASE_URI
   ```
4. Restart backend:
   ```bash
   python backend_app.py
   ```

---

## 🖥️ Frontend UI Setup

1. **Create `.env` in the root directory**
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
   ```

2. **Run Streamlit Frontend**
   ```bash
   cd UI
   streamlit run login.py
   ```

> ✅ Ensure `.env` is added to `.gitignore` to avoid exposing sensitive credentials.

---

## 🧩 Project Highlights

- Modular architecture integrating data ingestion, processing, and analysis
- ESG metric extraction tailored to the energy sector
- External trend and news integration for profile enhancement
- Microservices implementation for backend modularity
# Integrated dashboard with:
  - ESG performance insights
  - Chatbot assistance
  - User authentication
  - NeonDB database service

---

## ⚠️ Disclaimer

> For testing purposes, the **backend** currently uses **LocalDB**, while the **frontend** connects to **NeonDB**. A complete migration to NeonDB is recommended for end-to-end integration and consistent testing.

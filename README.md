🧠 Automating ESG Insights: Data Extraction and Performance Analysis

DSS5105 — Data Science Projects in Practice

Semester 2, AY2024/25

⸻

📘 Project Overview

This project aims to automate the extraction of ESG (Environmental, Social, Governance) insights from unstructured company reports using advanced NLP techniques, and provide performance analysis based on industry benchmarks. The system supports ESG analysts, investors, and regulators by making ESG data extraction faster, more reliable, and more actionable.



## 1.Install environment
move to the folder where you want to work
> 1. Clone code from github  
> $ git clone https://github.com/xuanntm/5105_development.git
> 2. Move to Git project  
> $ cd 5105_development
> 3. Create environment  
> $ python -m venv .venv  
> $ source .venv/bin/activate  
> $ pip install -r requirements.txt  
> 4. Create .env file with the some config
> SQLALCHEMY_DATABASE_URI=postgresql://admin:admin@127.0.0.1:54320/postgres  
> NEWSAPI_KEY={{YOUR_NEWS_API_KEY}}  
> BING_API_KEY={{YOUR_BING_API_KEY}}  
> 5. Download model  
> $ python src/config/model_config.py
> 6. Start environment  
> $ python backend_app.py  
> Backend endpoint : http://localhost:5000/
> 7. 
## 2.Install DB or create DB from script.
> 1. Dictionary table  
> esg_index_metric  
> esg_benchmark  
> company_profile  
> b_esg_cluster_analyis_actual_demo  
> b_esg_financial_metrics  
> b_esg_merged_financial_metrics  
> b_esg_metric_data_extracted  
> b_esg_with_trend_features  

## 3.Run Streamlit UI app
> $ streamlit run frontend_app.py  
> Frontend endpoint : http://localhost:8501/


## 4. switch db local <--> neondb

step to update DB endpoint:
- Stop current service (if it's running) : Ctrl+C
- update .env with new value for SQLALCHEMY_DATABASE_URI
- clean up cache $ unset SQLALCHEMY_DATABASE_URI
- start backend app $ python backend_app.py

## FrontEnd UI
![image](https://github.com/user-attachments/assets/320bc6f8-20f4-4049-b806-a705aca0b777)


Project Structure

![image](https://github.com/user-attachments/assets/925c267a-9759-48bd-a957-2a6f10e04d27)




>1. Clone the Repository

>2.  Create and Activate a Virtual Environment
      >Create
      python -m venv .venv

       Activate (macOS/Linux)
    source .venv/bin/activate

    >Activate (Windows)
    .venv\Scripts\activate

>3. Install Required Packages
>4. In the root directory, create a .env file:
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
   ✅ Ensure .env is listed in .gitignore to prevent accidental commits.

>5. Run the Streamlit App
  cd UI
  streamlit run login.py


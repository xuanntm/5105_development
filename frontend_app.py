import streamlit as st
import requests, os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:5000")

# Function to fetch company names from API with caching
@st.cache_data
def get_companies():
    response = requests.get(f'{BACKEND_API_URL}/api/v1/esg/company')  # Replace with your API URL
    if response.status_code == 200:
        return response.json()  # Adjust based on your API response structure
    else:
        return []  # Return an empty list on failure

# Function to make the submission API call
def submit_data(company_name, report_year, report_url):
    payload = {
        "company_name": company_name,
        "report_year": report_year,
        "report_url": report_url
    }
    response = requests.post(f'{BACKEND_API_URL}/api/v1/esg/input', json=payload)  # Replace with your Submission API URL
    return response.json()  # Adjust as needed


# Function to fetch table data from the new API
def fetch_table_data():
    response = requests.get(f'{BACKEND_API_URL}/api/v1/esg/report-history')  # Replace with your Table Data API URL
    if response.status_code == 200:
        return response.json()  # Adjust based on your API response structure
    else:
        return []


# Streamlit App
st.title("Company Report Submission")

# Dropdown for companies
companies = get_companies()
selected_company = st.selectbox("Select Company", options=companies)

# Dropdown for years
years = [2020, 2021, 2022, 2023, 2024]
selected_year = st.selectbox("Select Year", options=years)

# Input text for report URL
report_url = st.text_input("Enter Report URL (up to 500 characters)", max_chars=500)

# Submit button
if st.button("Submit"):
    if report_url and selected_company and selected_year:
        with st.spinner("Submitting data..."):
            submission_result = submit_data(selected_company, selected_year, report_url)
            st.success("Data submitted successfully: {}".format(submission_result))  # Show success message
            
            # Fetch and display the table data
            table_data = fetch_table_data()
            if table_data:
                df = pd.DataFrame(table_data)  # Convert to DataFrame for easy manipulation
                
                # Display table with filtering and sorting
                st.dataframe(df, use_container_width=True)  # Enables interactive features
            else:
                st.error("Failed to fetch table data.")
    else:
        st.error("Please fill in all fields before submitting.")
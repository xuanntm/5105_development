import yfinance as yf
import pandas as pd
import requests, json
from bs4 import BeautifulSoup
from IPython.display import display
from src.model.esg_models import db, ExternalSource


def get_ticker_symbol(company_name):
    """
    Search Yahoo Finance for the ticker symbol using web scraping.
    """
    search_url = f"https://finance.yahoo.com/lookup?s={company_name.replace(' ', '+')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # Raise an error if request fails
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first table row with a ticker symbol
        table_rows = soup.find_all("tr")
        for row in table_rows:
            columns = row.find_all("td")
            if len(columns) > 1:
                return columns[0].text.strip()  # Extract first ticker symbol

        return None  # Return None if no ticker found

    except Exception as e:
        print(f"Error retrieving ticker: {e}")
        return None


def get_esg_score(company_name):
    """
    Retrieve ESG scores from Yahoo Finance based on a company name.
    Returns 'NA' values if no ESG data is available.
    """
    ticker_symbol = get_ticker_symbol(company_name)
    # print(f'ticker_symbol{ticker_symbol}')

    if not ticker_symbol:
        print(f"No ticker found for '{company_name}'.")
        return pd.DataFrame(columns=["totalEsg", "socialScore", "governanceScore",
                                     "environmentScore", "esgPerformance", "percentile",
                                     "peerGroup", "highestControversy"], index=[company_name]).fillna("NA")

    ticker = yf.Ticker(ticker_symbol)

    try:
        esg_data = pd.DataFrame(ticker.sustainability)
        # print(f'esg_data{esg_data}')
        if esg_data.empty:
            print(f"No ESG data found for '{company_name}' ({ticker_symbol}).")
            return pd.DataFrame(columns=["totalEsg", "socialScore", "governanceScore",
                                         "environmentScore", "esgPerformance", "percentile",
                                         "peerGroup", "highestControversy"], index=[ticker_symbol]).fillna("NA")

        esg_data.columns = [ticker_symbol]
        esg_data_filtered = esg_data.loc[['totalEsg', 'socialScore', 'governanceScore',
                                          'environmentScore', 'esgPerformance',
                                          'percentile', 'peerGroup', 'highestControversy'], :]
        return esg_data_filtered

    except Exception as e:
        print(f"Error fetching ESG data for '{company_name}' ({ticker_symbol}): {e}")
        return pd.DataFrame(columns=["totalEsg", "socialScore", "governanceScore",
                                     "environmentScore", "esgPerformance", "percentile",
                                     "peerGroup", "highestControversy"], index=[ticker_symbol]).fillna("NA")


def fetch_and_plot_esg_scores(company_name):
    try:
        esg_scores = get_esg_score(company_name)
        if esg_scores is not None:
            display(esg_scores)
            # plot_esg_horizontal_chart(company_name, esg_scores)
            new_item = ExternalSource(esg_source="yahoo",
                                company_code="TestCode",
                                company_name=company_name, 
                                description="from Yahoo Fiancial", 
                                json_content=json.loads(esg_scores.to_json())['COP'])
            db.session.add(new_item)
            db.session.commit()
        return esg_scores
    except Exception as e:
        print(str(e))
        print(f'fetch_and_plot_esg_scores fail for {company_name}')
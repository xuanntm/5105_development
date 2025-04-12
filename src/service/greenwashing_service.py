# import pandas as pd

# from src.config.app_config import DATA_FOLDER_SENTIMENT, DATA_FOLDER_GREENWASHING
# from src.service.benchmark_service import detect_greenwashing_advanced
# from IPython.display import display


# def process_sentiment_data(company, report_year):
#     sentiment_file_name = f"{DATA_FOLDER_SENTIMENT}esg_sentiment_climatebert_" + company + str(report_year) + ".csv"
#     df = pd.read_csv(sentiment_file_name)

#     df[["Greenwashing Risk", "Matched Benchmark"]] = df.apply(
#         # lambda row: pd.Series(detect_greenwashing_advanced(row, benchmark_topics)), axis=1
#         lambda row: pd.Series(detect_greenwashing_advanced(row)), axis=1
#     )

#     # See which topics are most often flagged
#     df[df["Greenwashing Risk"] == "Potential"]["Matched Benchmark"].value_counts().head()
#     print('print Greenwashing Risk')
#     display(df)
#     # Export
#     file_name = f"{DATA_FOLDER_GREENWASHING}esg_greenwashing_risk_" + company + str(report_year) + ".csv"
#     print(f'save Greenwashing as {file_name}')
#     df.to_csv(file_name, index=False)
#     return True
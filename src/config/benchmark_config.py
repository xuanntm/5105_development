import pandas as pd
# from .app_config import DATA_FOLDER_BENCHMARK
from src.model.esg_models import db, EsgBenchmark

# benchmark_df = pd.read_csv(f"{DATA_FOLDER_BENCHMARK}Combined_ESG_Benchmark_Topics.csv")
# benchmark_topics = benchmark_df["Disclosure Topic"].dropna().str.lower().unique().tolist()
# print(benchmark_topics)
benchmark_topics = []
def db_load():
    benchmark_topics = db.session.query(EsgBenchmark.disclosure_topic).distinct().all() # .order_by(EsgBenchmark.id.asc())
    # print(benchmark_topics)

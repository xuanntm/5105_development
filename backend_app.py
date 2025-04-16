from flask import Flask, request, jsonify
from src.model.esg_models import db, EsgBenchmark
from src.service.text_extraction_service import esg_download_extract_save
from src.service.yfinance_service import fetch_and_plot_esg_scores
from src.service.realtime_news_service import run_esg_news_monitoring
from src.service.sentiment_analysis_service import process_esg_reports
from src.service.confidence_service import calculate_confidence_scores
from src.service.training_service import load_esg_model
from src.config.app_config import SQLALCHEMY_DATABASE_URI
from src.service.esg_score_service import load_all_data
from src.service.cluster_service import run_clustering
from src.service.util_service import get_company_list, get_esg_financial_metric, get_esg_report_histopry

# API connection
app = Flask(__name__)
# define database connection
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
print(f'SQLALCHEMY_DATABASE_URI:{SQLALCHEMY_DATABASE_URI}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# # Inside your app context
with app.app_context():
    benchmark_topics = db.session.query(EsgBenchmark.disclosure_topic).distinct().all()
    benchmark_topics = [topic[0] for topic in benchmark_topics]  # Convert to a flat list
#     db_load()
#     db.create_all()  # This will create the Item table


# ESG Input endpoint
@app.route('/api/v1/esg/input', methods=['POST'])
def esg_input():
    data = request.json
    required_fields = ['company_name', 'report_url', 'report_year']
    
    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    print(data)
    company_name = data['company_name']
    report_year = data['report_year']
    report_url = data['report_url']

    # Step 1: Download report from internet and extract to text
    print(f"📥 Processing ESG report: {company_name} {report_year}")
    message = esg_download_extract_save(report_url=report_url, company_name=company_name, report_year=report_year)
    # print(f'esg_dowload_extract_save:{message}')

    # Step 2: fetch yahoo finance data
    esg_scores = fetch_and_plot_esg_scores(company_name)
    # print(esg_scores)

    # Step 3: fetch ESG news
    df = run_esg_news_monitoring(company_name)
    # display(df.head())

    # Step 4: process ESG report with output from Step 1
    df = process_esg_reports(company_name, report_year, benchmark_topics)

    # Step 5: check confidence score
    calculate_confidence_scores(company_name, report_year)    

    # Step 6: ??? Training
    load_esg_model(company_name, report_year)

    return jsonify({'message': 'successful'}), 200



@app.route('/api/v1/esg/score', methods=['POST'])
def esg_score():
    print('esg_score start')
    data = request.json
    required_fields = ['report_year']
    
    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    report_year = data['report_year']
    print(f'report_year {report_year}')
    [df, output] = load_all_data(year=report_year)
    run_clustering(df)
    return jsonify(output), 200


@app.route('/api/v1/esg/company', methods=['GET'])
def retrieve_company_list():
    return get_company_list(), 200


@app.route('/api/v1/esg/financial-metric', methods=['GET'])
def retrieve_esg_financial_metric():
    return get_esg_financial_metric(), 200


@app.route('/api/v1/esg/report-history', methods=['GET'])
def retrieve_esg_report_histopry():
    return get_esg_report_histopry(), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
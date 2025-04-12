from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from src.service.text_extraction_service import extract_pdf_from_url, extract_sentences
from src.service.yfinance_service import fetch_and_plot_esg_scores
from src.service.realtime_news_service import run_esg_news_monitoring
from src.service.sentiment_analysis_service import process_esg_reports
# from src.service.greenwashing_service import process_sentiment_data
from src.service.confidence_service import calculate_confidence_scores
from src.service.training_service import load_esg_model
from src.config.app_config import SQLALCHEMY_DATABASE_URI
from src.config.benchmark_config import db_load
from src.model.esg_models import db, ReportHistory
import os, json
from IPython.display import display
# API connection
app = Flask(__name__)
# define database connection
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
# 'postgresql://admin:admin@127.0.0.1:54320/postgres'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@host.docker.internal:54320/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Sample data structures
# companies = []
# esg_metrics = []
# esg_inputs = []  # To store the ESG input data



# class Items(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)

# # Inside your app context
with app.app_context():
    db_load()
#     db.create_all()  # This will create the Item table

# @app.route('/items', methods=['GET'])
# def get_items():
#     items = Items.query.all()
#     return jsonify([{'id': item.id, 'name': item.name} for item in items])

# @app.route('/items', methods=['POST'])
# def create_item():
#     data = request.get_json()
#     new_item = Items(name=data['name'])
#     db.session.add(new_item)
#     db.session.commit()
#     return jsonify({'id': new_item.id, 'name': new_item.name}), 201

# You can implement other CRUD operations (GET by ID, PUT, DELETE) similarly.

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
    company_name = data['company_name']

    # Step 1.1: Download report from internet and extract to text
    print(f"📥 Processing ESG report: {company_name} {report_year}")
    # raw_text = extract_pdf_from_url(report_url)
    # report_pages, report_sentences = extract_sentences(raw_text)
    # print(raw_text)
    # Step 1.2: save extract to json file in structure
    # json_extract_path = os.path.join(DATA_FOLDER_JSON, f"{company_name}{report_year}.json")
    # report_data = {
    #     "company": company_name,
    #     "year": report_year,
    #     "url": report_url,
    #     "content": raw_text,
    #     "pages": report_pages,
    #     "sentences": report_sentences
    # }
    # new_item = ReportHistory(history_id="Test",
    #                          company_code="TestCode", 
    #                          year=report_year,
    #                          company_name=company_name, 
    #                          url=report_url, 
    #                          file_report_location=json_extract_path, 
    #                          esg_content= raw_text,
    #                          report_pages=report_pages,
    #                          report_sentences=report_sentences)  # Ensure 'name' corresponds to your model
    # db.session.add(new_item)
    # db.session.commit()
    # with open(json_extract_path, "w") as f:
    #     json.dump(report_data, f, indent=2)

    # # Step 2: fetch yahoo finance data
    # esg_scores = fetch_and_plot_esg_scores(company_name)

    # # Step 3: fetch ESG news
    # df = run_esg_news_monitoring(company_name)
    # display(df.head())

    # # Step 4: process ESG report with output from Step 1.2
    # extracted_files = [json_extract_path]
    df = process_esg_reports(company_name, report_year)
    # Step 5: process Sentiment data with output from Step 4
    # process_sentiment_data(company_name, report_year)

    # Step 6: check confidence score
    # calculate_confidence_scores(company_name, report_year)    
    # load_esg_model(company_name, report_year)

    return jsonify(data), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
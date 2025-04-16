from src.model.esg_models import db, CompanyProfile, BEsgFinancialMetrics, ReportHistory


def get_company_list():
    companies = db.session.query(CompanyProfile.company_name).distinct().all()
    return [topic[0] for topic in companies]


def get_esg_financial_metric():
    data = db.session.query(BEsgFinancialMetrics).with_entities(
            BEsgFinancialMetrics.year,
            BEsgFinancialMetrics.company_name,
            BEsgFinancialMetrics.Ticker,
            BEsgFinancialMetrics.ROA,
            BEsgFinancialMetrics.ROE,
            BEsgFinancialMetrics._1Y_Stock_Return,
        ).all()
    metrics = [{
            'company': row.company_name, 
            'year': row.year, 
            'ticker': row.Ticker,
            'roa': row.ROA,
            'roe': row.ROE,
            'stockReturn': row._1Y_Stock_Return
        }for row in data]
    return metrics

def get_esg_report_histopry():
    data = db.session.query(ReportHistory).with_entities(
            ReportHistory.year,
            ReportHistory.company_name,
            ReportHistory.url,
            ReportHistory.confidence_score,
            ReportHistory.history_id,
            ReportHistory.created_date,
        ).order_by(ReportHistory.created_date.desc()).all()
    history = [{
            # 'history_id': row.history_id, 
            'created_date': row.created_date, 
            'company_name': row.company_name,
            'year': row.year,
            'confidence_score': row.confidence_score,
            'url': row.url
        }for row in data]
    return history
from src.model.esg_models import db, CompanyProfile


def get_company_list():
    companies = db.session.query(CompanyProfile.company_name).distinct().all()
    return [topic[0] for topic in companies]

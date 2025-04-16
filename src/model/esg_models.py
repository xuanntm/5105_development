from typing import Optional

from sqlalchemy import Column, DateTime, Integer, JSON, Numeric, PrimaryKeyConstraint, REAL, Sequence, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime
import decimal
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Base(DeclarativeBase):
    pass


class BEsgActualScore(db.Model):
    __tablename__ = 'b_esg_actual_score'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_actual_score_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Year: Mapped[Optional[int]] = mapped_column(Integer)
    company_name: Mapped[Optional[str]] = mapped_column(String(50))
    Environmental_Score: Mapped[Optional[float]] = mapped_column(REAL)
    Social_Score: Mapped[Optional[float]] = mapped_column(REAL)
    Governance_Score: Mapped[Optional[float]] = mapped_column(REAL)
    ESG_Score: Mapped[Optional[float]] = mapped_column(REAL)
    ESG_Rating: Mapped[Optional[str]] = mapped_column(String(50))
    ESG_Rank: Mapped[Optional[int]] = mapped_column(Integer)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    data_type: Mapped[Optional[str]] = mapped_column(String(10))


class BEsgClusterAnalyisActual(db.Model):
    __tablename__ = 'b_esg_cluster_analyis_actual'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_cluster_analyis_actual_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Year: Mapped[Optional[int]] = mapped_column(Integer)
    company_name: Mapped[Optional[str]] = mapped_column(String(50))
    Environmental_Score: Mapped[Optional[float]] = mapped_column(REAL)
    Social_Score: Mapped[Optional[float]] = mapped_column(REAL)
    Governance_Score: Mapped[Optional[float]] = mapped_column(REAL)
    ESG_Score: Mapped[Optional[float]] = mapped_column(REAL)
    PCA1: Mapped[Optional[float]] = mapped_column(REAL)
    PCA2: Mapped[Optional[float]] = mapped_column(REAL)
    Cluster: Mapped[Optional[int]] = mapped_column(Integer)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    data_type: Mapped[Optional[str]] = mapped_column(String(10))


class BEsgClusterAnalyisActualDemo(db.Model):
    __tablename__ = 'b_esg_cluster_analyis_actual_demo'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_cluster_analyis_actual_demo_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Year: Mapped[Optional[int]] = mapped_column(Integer)
    Company: Mapped[Optional[str]] = mapped_column(String(50))
    Environmental_Score: Mapped[Optional[float]] = mapped_column('Environmental Score', REAL)
    Social_Score: Mapped[Optional[float]] = mapped_column('Social Score', REAL)
    Governance_Score: Mapped[Optional[float]] = mapped_column('Governance Score', REAL)
    ESG_Score: Mapped[Optional[float]] = mapped_column('ESG Score', REAL)
    PCA1: Mapped[Optional[float]] = mapped_column(REAL)
    PCA2: Mapped[Optional[float]] = mapped_column(REAL)
    Cluster: Mapped[Optional[int]] = mapped_column(Integer)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class BEsgFinancialMetrics(db.Model):
    __tablename__ = 'b_esg_financial_metrics'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_financial_metrics_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    company_name: Mapped[Optional[str]] = mapped_column(String(50))
    Ticker: Mapped[Optional[str]] = mapped_column(String(50))
    ROA: Mapped[Optional[float]] = mapped_column(REAL)
    ROE: Mapped[Optional[float]] = mapped_column(REAL)
    _1Y_Stock_Return: Mapped[Optional[float]] = mapped_column('1Y_Stock Return', REAL)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class BEsgMergedFinancialMetrics(db.Model):
    __tablename__ = 'b_esg_merged_financial_metrics'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_merged_financial_metrics_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(50))
    Year: Mapped[Optional[int]] = mapped_column(Integer)
    roa: Mapped[Optional[float]] = mapped_column(REAL)
    roe: Mapped[Optional[float]] = mapped_column(REAL)
    _1Y_Stock_Return: Mapped[Optional[float]] = mapped_column('1Y_Stock_Return', REAL)
    environmental_score: Mapped[Optional[float]] = mapped_column(REAL)
    social_score: Mapped[Optional[int]] = mapped_column(Integer)
    governance_score: Mapped[Optional[int]] = mapped_column(Integer)
    esg_score: Mapped[Optional[float]] = mapped_column(REAL)
    esg_rating: Mapped[Optional[str]] = mapped_column(String(50))
    esg_rank: Mapped[Optional[int]] = mapped_column(Integer)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class BEsgMetricDataExtracted(db.Model):
    __tablename__ = 'b_esg_metric_data_extracted'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_metric_data_extracted_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Data_type: Mapped[Optional[str]] = mapped_column(String(50))
    Company_name: Mapped[Optional[str]] = mapped_column(String(50))
    Year: Mapped[Optional[int]] = mapped_column(Integer)
    E01_GHG_ETT: Mapped[Optional[str]] = mapped_column(String(50))
    E02_GHG_ITP: Mapped[Optional[str]] = mapped_column(String(50))
    E03_Land: Mapped[Optional[str]] = mapped_column(String(50))
    E04_Bio: Mapped[Optional[int]] = mapped_column(Integer)
    E05_Water_C: Mapped[Optional[str]] = mapped_column(String(50))
    E06_Water_W: Mapped[Optional[str]] = mapped_column(String(50))
    E07_Electronic_W: Mapped[Optional[float]] = mapped_column(REAL)
    E08_Pkg_M_W: Mapped[Optional[float]] = mapped_column(REAL)
    E09_Air_P: Mapped[Optional[str]] = mapped_column(String(50))
    E10_Toxic_W: Mapped[Optional[str]] = mapped_column(String(50))
    E11_Opp_RE: Mapped[Optional[str]] = mapped_column(String(50))
    S01_HR: Mapped[Optional[str]] = mapped_column(String(128))
    S02_PR: Mapped[Optional[str]] = mapped_column(String(50))
    S03_HSI: Mapped[Optional[float]] = mapped_column(REAL)
    S04_HSF: Mapped[Optional[str]] = mapped_column(String(50))
    S05_TH: Mapped[Optional[str]] = mapped_column(String(50))
    S06_CR: Mapped[Optional[str]] = mapped_column(String(50))
    G01_BD: Mapped[Optional[float]] = mapped_column(REAL)
    G02_BI: Mapped[Optional[int]] = mapped_column(Integer)
    G03_P: Mapped[Optional[str]] = mapped_column(String(50))
    G04_Acct: Mapped[Optional[str]] = mapped_column(String(50))
    G05_BE: Mapped[Optional[str]] = mapped_column(String(50))
    G06_Tax_T: Mapped[Optional[str]] = mapped_column(String(50))
    G07_Vote_R: Mapped[Optional[str]] = mapped_column(String(50))
    F01_R: Mapped[Optional[float]] = mapped_column(REAL)
    F02_NP: Mapped[Optional[float]] = mapped_column(REAL)
    F03_ROE: Mapped[Optional[float]] = mapped_column(REAL)
    F04_R_GR: Mapped[Optional[float]] = mapped_column(REAL)
    F05_CF: Mapped[Optional[float]] = mapped_column(REAL)
    F06_EBITDA: Mapped[Optional[float]] = mapped_column(REAL)
    F07_BV: Mapped[Optional[float]] = mapped_column(REAL)
    F08_CR: Mapped[Optional[str]] = mapped_column(String(50))
    F09_ESG_CS: Mapped[Optional[int]] = mapped_column(Integer)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class BEsgWithTrendFeatures(db.Model):
    __tablename__ = 'b_esg_with_trend_features'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='b_esg_with_trend_features_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Year: Mapped[Optional[int]] = mapped_column(Integer)
    company_name: Mapped[Optional[str]] = mapped_column(String(50))
    Environmental_Score: Mapped[Optional[float]] = mapped_column(REAL)
    Social_Score: Mapped[Optional[float]] = mapped_column(REAL)
    Governance_Score: Mapped[Optional[float]] = mapped_column(REAL)
    ESG_Score: Mapped[Optional[float]] = mapped_column(REAL)
    ESG_Rating: Mapped[Optional[str]] = mapped_column(String(50))
    ESG_Rank: Mapped[Optional[int]] = mapped_column(Integer)
    ESG_News_Count: Mapped[Optional[int]] = mapped_column(Integer)
    esg_trend: Mapped[Optional[float]] = mapped_column(REAL)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    data_type: Mapped[Optional[str]] = mapped_column(String(10))


class CompanyEsgScores(db.Model):
    __tablename__ = 'company_esg_scores'
    __table_args__ = (
        PrimaryKeyConstraint('company_name', 'year', name='company_esg_scores_pkey'),
        {}
    )

    company_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    environment_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    social_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    governance_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    esg_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    esg_rating: Mapped[Optional[str]] = mapped_column(String(10))
    esg_rank: Mapped[Optional[int]] = mapped_column(Integer)
    data_flag: Mapped[Optional[str]] = mapped_column(String(10))


class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='company_profile_pkey'),
        UniqueConstraint('companycode', name='unique_company_code'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, Sequence('company_profile_company_id_seq', schema='esg'), primary_key=True)
    companycode: Mapped[Optional[str]] = mapped_column(String(10))
    company_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class EsgBenchmark(db.Model):
    __tablename__ = 'esg_benchmark'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_benchmark_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sector: Mapped[Optional[str]] = mapped_column(String(30))
    disclosure_topic: Mapped[Optional[str]] = mapped_column(String(100))
    esg_category: Mapped[Optional[str]] = mapped_column(String(100))
    esg_source: Mapped[Optional[str]] = mapped_column(String(10))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class EsgExtractedMetricData(Base):
    __tablename__ = 'esg_extracted_metric_data'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_extracted_metric_data_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(100))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    history_id: Mapped[Optional[str]] = mapped_column(String(50))
    pillar: Mapped[Optional[str]] = mapped_column(String(50))
    metric: Mapped[Optional[str]] = mapped_column(String(128))
    extracted_metric: Mapped[Optional[str]] = mapped_column(String(512))
    extracted_value: Mapped[Optional[str]] = mapped_column(String(50))
    esg_id: Mapped[Optional[str]] = mapped_column(String(20))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))



class EsgIndexMetric(db.Model):
    __tablename__ = 'esg_index_metric'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_index_metric_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    esg_id: Mapped[str] = mapped_column(String(20))
    esg_index_metric: Mapped[Optional[str]] = mapped_column(String(255))
    type: Mapped[Optional[str]] = mapped_column(String(20))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class EsgNews(db.Model):
    __tablename__ = 'esg_news'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_news_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[Optional[str]] = mapped_column(String(50))
    news_source: Mapped[Optional[str]] = mapped_column(String(10))
    news_title: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(50))
    sentiment_score: Mapped[Optional[float]] = mapped_column(REAL)
    esg_category: Mapped[Optional[str]] = mapped_column(String(50))
    published_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    remark: Mapped[Optional[str]] = mapped_column(String(200))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class EsgSentiment(db.Model):
    __tablename__ = 'esg_sentiment'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_sentiment_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[Optional[str]] = mapped_column(String(50))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    esg_category: Mapped[Optional[str]] = mapped_column(String(50))
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(50))
    sentiment_score: Mapped[Optional[float]] = mapped_column(REAL)
    greenwashing_risk: Mapped[Optional[str]] = mapped_column(String(50))
    matched_benchmark_topic: Mapped[Optional[str]] = mapped_column(String(100))
    text_snippet: Mapped[Optional[str]] = mapped_column(String(500))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class ExternalSource(db.Model):
    __tablename__ = 'external_source'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='external_source_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    esg_source: Mapped[str] = mapped_column(String(20))
    company_code: Mapped[Optional[str]] = mapped_column(String(10))
    company_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    text_content: Mapped[Optional[str]] = mapped_column(Text)
    json_content: Mapped[Optional[dict]] = mapped_column(JSON)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class ReportHistory(db.Model):
    __tablename__ = 'report_history'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='report_history_pkey'),
        {}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    company_code: Mapped[Optional[str]] = mapped_column(String(10))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    company_name: Mapped[Optional[str]] = mapped_column(String(100))
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    file_report_location: Mapped[Optional[str]] = mapped_column(String(200))
    esg_content: Mapped[Optional[str]] = mapped_column(Text)
    report_pages: Mapped[Optional[dict]] = mapped_column(JSON)
    report_sentences: Mapped[Optional[dict]] = mapped_column(JSON)
    confidence_score: Mapped[Optional[float]] = mapped_column(REAL)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

from typing import Optional

from sqlalchemy import Column, DateTime, Integer, JSON, PrimaryKeyConstraint, REAL, Sequence, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Base(DeclarativeBase):
    pass


class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='company_profile_pkey'),
        UniqueConstraint('companycode', name='unique_company_code'),
        {'schema': 'esg'}
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
        {'schema': 'esg'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sector: Mapped[Optional[str]] = mapped_column(String(30))
    disclosure_topic: Mapped[Optional[str]] = mapped_column(String(100))
    esg_category: Mapped[Optional[str]] = mapped_column(String(100))
    esg_source: Mapped[Optional[str]] = mapped_column(String(10))
    description: Mapped[Optional[str]] = mapped_column(String(200))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


t_esg_extracted_metric_data = Table(
    'esg_extracted_metric_data', Base.metadata,
    Column('history_id', String(20)),
    Column('esg_id', String(20)),
    Column('esg_value', String(100)),
    Column('created_date', DateTime, server_default=text('CURRENT_TIMESTAMP')),
    schema='esg'
)


class EsgIndexMetric(db.Model):
    __tablename__ = 'esg_index_metric'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_index_metric_pkey'),
        {'schema': 'esg'}
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
        {'schema': 'esg'}
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
    url: Mapped[Optional[str]] = mapped_column(String(200))
    remark: Mapped[Optional[str]] = mapped_column(String(200))
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class EsgSentiment(db.Model):
    __tablename__ = 'esg_sentiment'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='esg_sentiment_pkey'),
        {'schema': 'esg'}
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
        {'schema': 'esg'}
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
        {'schema': 'esg'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    history_id: Mapped[str] = mapped_column(String(20))
    company_code: Mapped[Optional[str]] = mapped_column(String(10))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    company_name: Mapped[Optional[str]] = mapped_column(String(100))
    url: Mapped[Optional[str]] = mapped_column(String(200))
    file_report_location: Mapped[Optional[str]] = mapped_column(String(200))
    esg_content: Mapped[Optional[str]] = mapped_column(Text)
    report_pages: Mapped[Optional[dict]] = mapped_column(JSON)
    report_sentences: Mapped[Optional[dict]] = mapped_column(JSON)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


t_test_number = Table(
    'test_number', Base.metadata,
    Column('Company', String(50)),
    Column('Year', Integer),
    Column('ESG Category', String(50)),
    Column('Sentiment Label', String(50)),
    Column('Sentiment Score', REAL),
    Column('Text Snippet', String(64)),
    schema='esg'
)

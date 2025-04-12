from typing import List, Optional

from sqlalchemy import Column, ForeignKeyConstraint, Integer, LargeBinary, PrimaryKeyConstraint, String, Table, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class CompanyProfile(Base):
    __tablename__ = 'company_profile'
    __table_args__ = (
        PrimaryKeyConstraint('company_id', name='company_profile_pkey'),
        UniqueConstraint('companycode', name='unique_company_code'),
        {'schema': 'my_sample'}
    )

    company_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    companycode: Mapped[Optional[str]] = mapped_column(String(10))
    company_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))

    report_history: Mapped[List['ReportHistory']] = relationship('ReportHistory', back_populates='company_profile')


class EsgIndexMetric(Base):
    __tablename__ = 'esg_index_metric'
    __table_args__ = (
        PrimaryKeyConstraint('esg_id', name='esg_index_metric_pkey'),
        {'schema': 'my_sample'}
    )

    esg_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    esg_index_metric: Mapped[Optional[str]] = mapped_column(String(255))
    type: Mapped[Optional[str]] = mapped_column(String(20))


class ReportHistory(Base):
    __tablename__ = 'report_history'
    __table_args__ = (
        ForeignKeyConstraint(['companycode'], ['my_sample.company_profile.companycode'], name='report_history_companycode_fkey'),
        PrimaryKeyConstraint('history_id', name='pk_history_id'),
        UniqueConstraint('companycode', 'year', name='report_history_companycode_year_key'),
        {'schema': 'my_sample'}
    )

    history_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    companycode: Mapped[Optional[str]] = mapped_column(String(10))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    filereportlocation: Mapped[Optional[str]] = mapped_column(String(200))
    rawextractedtext: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    company_profile: Mapped[Optional['CompanyProfile']] = relationship('CompanyProfile', back_populates='report_history')


t_esg_extracted_metric_data = Table(
    'esg_extracted_metric_data', Base.metadata,
    Column('history_id', String(20)),
    Column('esg_id', String(20)),
    Column('esg_value', String(100)),
    ForeignKeyConstraint(['esg_id'], ['my_sample.esg_index_metric.esg_id'], name='esg_extracted_metric_data_esg_id_fkey'),
    ForeignKeyConstraint(['history_id'], ['my_sample.report_history.history_id'], name='esg_extracted_metric_data_history_id_fkey'),
    schema='my_sample'
)

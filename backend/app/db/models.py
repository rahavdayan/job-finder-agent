from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class JobPageRaw(Base):
    __tablename__ = "job_pages_raw"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_html = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship to parsed data (one-to-one)
    parsed_data = relationship("JobPageParsed", back_populates="job_page_raw", uselist=False)


class JobPageParsed(Base):
    __tablename__ = "job_pages_parsed"
    
    id = Column(Integer, primary_key=True, index=True)
    job_page_raw_id = Column(Integer, ForeignKey("job_pages_raw.id"), nullable=False, unique=True)
    job_title = Column(String, nullable=True)
    employer = Column(String, nullable=True)
    location = Column(String, nullable=True)
    date_posted = Column(String, nullable=True)  # ISO 8601 timestamp or date
    primary_salary_min = Column(Float, nullable=True)  # From salary div during scraping
    primary_salary_max = Column(Float, nullable=True)  # From salary div during scraping
    primary_salary_rate = Column(Enum('hourly', 'weekly', 'monthly', 'yearly', 'other', name='salary_rate_enum'), nullable=True)  # From salary div during scraping
    secondary_salary_min = Column(Float, nullable=True)  # From description using LLM
    secondary_salary_max = Column(Float, nullable=True)  # From description using LLM
    secondary_salary_rate = Column(Enum('hourly', 'weekly', 'monthly', 'yearly', 'other', name='salary_rate_enum'), nullable=True)  # From description using LLM
    normalized_salary_min = Column(Float, nullable=True)  # Always in yearly USD
    normalized_salary_max = Column(Float, nullable=True)  # Always in yearly USD
    job_type = Column(String, nullable=True)  # Full-time, Part-time, Contract, etc.
    skills = Column(String, nullable=True)  # Stored as comma-separated string for SQLite compatibility
    description = Column(String, nullable=True)
    seniority = Column(String, nullable=True)  # Junior, Mid-level, Senior, Lead, Manager
    education_level = Column(String, nullable=True)  # High School, BSc, MSc, PhD
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship back to raw data
    job_page_raw = relationship("JobPageRaw", back_populates="parsed_data")

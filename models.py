from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class JobPageRaw(Base):
    __tablename__ = "job_pages_raw"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_html = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

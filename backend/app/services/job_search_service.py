from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from app.schemas.jobs import JobSearchRequest
from app.db.models import JobPageParsed

def search_jobs(db: Session, search_params: JobSearchRequest) -> List[JobPageParsed]:
    """
    Placeholder function that returns all jobs without filtering.
    Returns all JobPageParsed objects from the database.
    """
    return db.query(JobPageParsed).all()

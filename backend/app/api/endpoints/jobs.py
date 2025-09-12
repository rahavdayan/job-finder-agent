from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.jobs import JobSearchRequest, JobResponse
from app.services.job_search_service import search_jobs

router = APIRouter()

@router.post("/users/find_jobs", response_model=List[JobResponse])
def find_jobs(
    search_params: JobSearchRequest,
    db: Session = Depends(get_db)
) -> List[JobResponse]:
    """
    Search for jobs based on user preferences and requirements.
    Returns a list of matching job postings.
    """
    try:
        jobs = search_jobs(db, search_params)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

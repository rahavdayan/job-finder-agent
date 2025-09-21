from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.api.schemas.job_search import JobSearchRequest, JobSearchResponse, JobMatch
from app.services.job_matcher import JobMatcher
from app.db.models import JobPageParsed, JobPageRaw

router = APIRouter()

@router.post("/users/find_jobs", response_model=JobSearchResponse)
def find_jobs(
    request: JobSearchRequest,
    db: Session = Depends(get_db)
) -> JobSearchResponse:
    """
    Find jobs that match user criteria with scoring.
    
    Filters jobs based on:
    - Salary range
    - Seniority level (job requirement <= user level)
    - Education level (job requirement <= user level)
    
    Scores jobs based on:
    - Job type match (20%)
    - Title similarity (30%) 
    - Skills overlap (40%)
    - Salary position in range (10%)
    
    Returns jobs ordered by score (highest first).
    """
    try:
        job_matcher = JobMatcher(db)
        matching_jobs = job_matcher.find_matching_jobs(request)
        
        return JobSearchResponse(
            jobs=matching_jobs,
            total_count=len(matching_jobs)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding matching jobs: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobMatch)
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db)
) -> JobMatch:
    """
    Get a single job by its ID.
    
    Returns the job with all details including the URL from the raw table.
    Note: This endpoint returns the job without scoring since no user criteria are provided.
    """
    try:
        # Query job with URL from raw table
        job_query = db.query(JobPageParsed, JobPageRaw.url).join(
            JobPageRaw, JobPageParsed.job_page_raw_id == JobPageRaw.id
        ).filter(JobPageParsed.id == job_id).first()
        
        if not job_query:
            raise HTTPException(
                status_code=404,
                detail=f"Job with ID {job_id} not found"
            )
        
        job_parsed, job_url = job_query
        
        # Create JobMatch object without scoring (since no user criteria provided)
        job_match = JobMatch(
            # Job data
            id=job_parsed.id,
            job_title=job_parsed.job_title,
            employer=job_parsed.employer,
            location=job_parsed.location,
            date_posted=job_parsed.date_posted,
            primary_salary_min=job_parsed.primary_salary_min,
            primary_salary_max=job_parsed.primary_salary_max,
            primary_salary_rate=job_parsed.primary_salary_rate,
            secondary_salary_min=job_parsed.secondary_salary_min,
            secondary_salary_max=job_parsed.secondary_salary_max,
            secondary_salary_rate=job_parsed.secondary_salary_rate,
            job_type=job_parsed.job_type,
            skills=job_parsed.skills,
            description=job_parsed.description,
            seniority=job_parsed.seniority,
            education_level=job_parsed.education_level,
            normalized_salary_min=job_parsed.normalized_salary_min,
            normalized_salary_max=job_parsed.normalized_salary_max,
            
            # URL from raw table
            url=job_url,
            
            # Default scores (no user criteria to calculate against)
            score=0.0,
            job_type_score=0.0,
            title_score=0.0,
            skills_score=0.0,
            salary_score=0.0
        )
        
        return job_match
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching job: {str(e)}"
        )

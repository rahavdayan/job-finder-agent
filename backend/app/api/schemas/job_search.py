from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class SeniorityLevel(str, Enum):
    JUNIOR = "Junior"
    MID_LEVEL = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high school"
    BSC = "BSc"
    MSC = "MSc"
    PHD = "PhD"

class JobSearchRequest(BaseModel):
    salary_min: int = Field(..., description="Minimum salary requirement")
    salary_max: int = Field(..., description="Maximum salary requirement")
    seniority: SeniorityLevel = Field(..., description="User's seniority level")
    job_type: List[str] = Field(..., description="Preferred job types (e.g., Full-time, Part-time, Contract)")
    job_titles: List[str] = Field(..., description="User's job titles/roles")
    skills: List[str] = Field(..., description="User's skills")
    education_level: EducationLevel = Field(..., description="User's education level")

class JobMatch(BaseModel):
    # Job data from JOB_PAGES_PARSED
    id: int
    job_title: Optional[str]
    employer: Optional[str]
    location: Optional[str]
    date_posted: Optional[str]
    primary_salary_min: Optional[float]
    primary_salary_max: Optional[float]
    primary_salary_rate: Optional[str]
    secondary_salary_min: Optional[float]
    secondary_salary_max: Optional[float]
    secondary_salary_rate: Optional[str]
    job_type: Optional[str]
    skills: Optional[str]
    description: Optional[str]
    seniority: Optional[str]
    education_level: Optional[str]
    normalized_salary_min: Optional[float]
    normalized_salary_max: Optional[float]
    
    # URL from JOB_PAGES_RAW
    url: str
    
    # Calculated score
    score: float
    
    # Score breakdown for transparency
    job_type_score: float
    title_score: float
    skills_score: float
    salary_score: float

class JobSearchResponse(BaseModel):
    jobs: List[JobMatch]
    total_count: int

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class SeniorityLevel(str, Enum):
    JUNIOR = "Junior"
    MID_LEVEL = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"

class JobType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "High School"
    BSC = "BSc"
    MSC = "MSc"
    PHD = "PhD"

class JobSearchRequest(BaseModel):
    salaryMin: Optional[float] = Field(None, description="Minimum desired salary in dollars")
    salaryMax: Optional[float] = Field(None, description="Maximum desired salary in dollars")
    seniority: Optional[SeniorityLevel] = Field(None, description="Target seniority level")
    jobType: Optional[List[JobType]] = Field(None, description="Desired job types")
    jobTitles: Optional[List[str]] = Field(None, description="Target job titles")
    skills: Optional[List[str]] = Field(None, description="Required skills")
    educationLevel: Optional[EducationLevel] = Field(None, description="Required education level")

    @validator('salaryMax')
    def validate_salary_range(cls, v, values):
        if v is not None and values.get('salaryMin') is not None:
            if v < values['salaryMin']:
                raise ValueError('Maximum salary must be greater than or equal to minimum salary')
        return v

class JobResponse(BaseModel):
    id: int
    job_title: Optional[str]
    employer: Optional[str]
    location: Optional[str]
    date_posted: Optional[str]
    primary_salary_min: Optional[float]
    primary_salary_max: Optional[float]
    primary_salary_rate: Optional[str]
    job_type: Optional[str]
    skills: Optional[str]
    seniority: Optional[str]
    education_level: Optional[str]

    class Config:
        from_attributes = True

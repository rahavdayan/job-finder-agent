from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

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

class ResumeParseResponse(BaseModel):
    seniority: Optional[SeniorityLevel] = None
    job_titles: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    education_level: Optional[EducationLevel] = None

import re
from typing import List, Optional, Tuple
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import JobPageParsed, JobPageRaw
from app.api.schemas.job_search import JobSearchRequest, JobMatch, SeniorityLevel, EducationLevel


class JobMatcher:
    """Service for matching jobs to user preferences with scoring."""
    
    # Seniority hierarchy for filtering
    SENIORITY_HIERARCHY = {
        "Junior": 1,
        "Mid-level": 2,
        "Senior": 3,
        "Lead": 4,
        "Manager": 5
    }
    
    # Education hierarchy for filtering
    EDUCATION_HIERARCHY = {
        "high school": 1,
        "BSc": 2,
        "MSc": 3,
        "PhD": 4
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_matching_jobs(self, request: JobSearchRequest) -> List[JobMatch]:
        """Find and score jobs based on user criteria."""
        
        # Get all jobs with their URLs
        jobs_query = self.db.query(JobPageParsed, JobPageRaw.url).join(
            JobPageRaw, JobPageParsed.job_page_raw_id == JobPageRaw.id
        )
        
        all_jobs = jobs_query.all()
        
        # Filter jobs based on requirements
        filtered_jobs = []
        for job_parsed, job_url in all_jobs:
            if self._passes_filters(job_parsed, request):
                filtered_jobs.append((job_parsed, job_url))
        
        # Calculate scores for filtered jobs
        scored_jobs = []
        for job_parsed, job_url in filtered_jobs:
            score_data = self._calculate_score(job_parsed, request)
            
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
                
                # Scores
                score=score_data["total_score"],
                job_type_score=score_data["job_type_score"],
                title_score=score_data["title_score"],
                skills_score=score_data["skills_score"],
                salary_score=score_data["salary_score"]
            )
            
            scored_jobs.append(job_match)
        
        # Sort by score (highest first)
        scored_jobs.sort(key=lambda x: x.score, reverse=True)
        
        return scored_jobs
    
    def _passes_filters(self, job: JobPageParsed, request: JobSearchRequest) -> bool:
        """Check if job passes basic filtering criteria."""

        if job.normalized_salary_max and job.normalized_salary_max < request.salary_min:
            return False
        if job.normalized_salary_min and job.normalized_salary_min > request.salary_max:
            return False
        
        # Filter by seniority (job requirement should not exceed user level)
        if job.seniority and request.seniority:
            job_seniority_level = self.SENIORITY_HIERARCHY.get(job.seniority, 0)
            user_seniority_level = self.SENIORITY_HIERARCHY.get(request.seniority.value, 0)
            
            if job_seniority_level > user_seniority_level:
                return False
        
        # Filter by education (job requirement should not exceed user level)
        if job.education_level and request.education_level:
            job_education_level = self.EDUCATION_HIERARCHY.get(job.education_level, 0)
            user_education_level = self.EDUCATION_HIERARCHY.get(request.education_level.value, 0)
            
            if job_education_level > user_education_level:
                return False
        
        return True
    
    def _calculate_score(self, job: JobPageParsed, request: JobSearchRequest) -> dict:
        """Calculate comprehensive score for a job."""
        
        # Job Type Score (0.2 weight)
        job_type_score = self._calculate_job_type_score(job, request)
        
        # Title Score (0.3 weight)
        title_score = self._calculate_title_score(job, request)
        
        # Skills Score (0.4 weight)
        skills_score = self._calculate_skills_score(job, request)
        
        # Salary Score (0.1 weight)
        salary_score = self._calculate_salary_score(job, request)
        
        # Final weighted score
        total_score = (
            0.2 * job_type_score +
            0.3 * title_score +
            0.4 * skills_score +
            0.1 * salary_score
        )
        
        return {
            "total_score": total_score,
            "job_type_score": job_type_score,
            "title_score": title_score,
            "skills_score": skills_score,
            "salary_score": salary_score
        }
    
    def _calculate_job_type_score(self, job: JobPageParsed, request: JobSearchRequest) -> float:
        """Calculate job type score (1 if match, 0 if no match)."""
        if not job.job_type:
            return 1.0
        
        job_type_normalized = self._normalize_text(job.job_type)
        
        for user_job_type in request.job_type:
            user_job_type_normalized = self._normalize_text(user_job_type)
            if user_job_type_normalized in job_type_normalized or job_type_normalized in user_job_type_normalized:
                return 1.0
        
        return 0.0
    
    def _calculate_title_score(self, job: JobPageParsed, request: JobSearchRequest) -> float:
        """Calculate title similarity score using fuzzy matching."""
        if not job.job_title or not request.job_titles:
            return 0.0
        
        job_title_normalized = self._normalize_text(job.job_title)
        max_similarity = 0.0
        
        for user_title in request.job_titles:
            user_title_normalized = self._normalize_text(user_title)
            similarity = self._fuzzy_similarity(job_title_normalized, user_title_normalized)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_skills_score(self, job: JobPageParsed, request: JobSearchRequest) -> float:
        """Calculate skills overlap ratio."""
        if not job.skills or not request.skills:
            return 0.0
        
        # Parse job skills (comma-separated string)
        job_skills = [self._normalize_text(skill.strip()) for skill in job.skills.split(',') if skill.strip()]
        user_skills = [self._normalize_text(skill) for skill in request.skills]
        
        if not user_skills:
            return 0.0
        
        # Count overlapping skills
        overlapping_skills = 0
        for user_skill in user_skills:
            for job_skill in job_skills:
                # Use fuzzy matching for skills as well
                if self._fuzzy_similarity(user_skill, job_skill) > 0.8:
                    overlapping_skills += 1
                    break
        
        # Return overlap ratio
        return overlapping_skills / len(user_skills)
    
    def _calculate_salary_score(self, job: JobPageParsed, request: JobSearchRequest) -> float:
        """Calculate salary score based on position within user's range."""
        
        if not job.normalized_salary_min:
            return 0.5  # Neutral score if no salary info
        
        if request.salary_max <= request.salary_min:
            return 0.5  # Avoid division by zero
        
        # Calculate score: (job.salary - user.salaryMin) / (user.salaryMax - user.salaryMin)
        score = (job.normalized_salary_min - request.salary_min) / (request.salary_max - request.salary_min)
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text by lowercasing and removing punctuation."""
        if not text:
            return ""
        
        # Convert to lowercase and remove punctuation
        normalized = re.sub(r'[^\w\s]', ' ', text.lower())
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _fuzzy_similarity(self, text1: str, text2: str) -> float:
        """Calculate fuzzy similarity between two strings."""
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1, text2).ratio()

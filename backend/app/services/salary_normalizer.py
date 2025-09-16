from typing import Optional, Tuple
from app.db.models import JobPageParsed


class SalaryNormalizer:
    """Utility class for normalizing salaries to yearly USD."""
    
    @staticmethod
    def normalize_salary(min_salary: Optional[float], max_salary: Optional[float], rate: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        """
        Convert salary to yearly USD when possible.
        
        Args:
            min_salary: Minimum salary amount
            max_salary: Maximum salary amount  
            rate: Salary rate type ('hourly', 'weekly', 'monthly', 'yearly', 'other')
            
        Returns:
            Tuple of (normalized_min, normalized_max)
        """
        if not rate or not (min_salary or max_salary):
            return None, None
            
        multipliers = {
            'hourly': 2080,    # 40 hours/week * 52 weeks
            'weekly': 52,      # 52 weeks/year
            'monthly': 12,     # 12 months/year
            'yearly': 1        # Already yearly
        }
        
        multiplier = multipliers.get(rate)
        if not multiplier:  # 'other' and any unknown rates are non-normalizable
            return None, None
            
        return (
            min_salary * multiplier if min_salary else None,
            max_salary * multiplier if max_salary else None
        )
    
    @staticmethod
    def get_best_salary_data(job: JobPageParsed) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Get the best available salary data, preferring primary over secondary.
        
        Args:
            job: JobPageParsed instance
            
        Returns:
            Tuple of (min_salary, max_salary, rate)
        """
        # Try primary salary first (from scraping)
        if job.primary_salary_min or job.primary_salary_max:
            return (
                job.primary_salary_min,
                job.primary_salary_max,
                job.primary_salary_rate
            )
        
        # Fall back to secondary salary (from LLM extraction)
        return (
            job.secondary_salary_min,
            job.secondary_salary_max,
            job.secondary_salary_rate
        )
    
    @classmethod
    def normalize_job_salary(cls, job: JobPageParsed) -> None:
        """
        Normalize salary for a job and update the job instance.
        
        Args:
            job: JobPageParsed instance to update
        """
        min_salary, max_salary, rate = cls.get_best_salary_data(job)
        
        normalized_min, normalized_max = cls.normalize_salary(
            min_salary, max_salary, rate
        )
        
        job.normalized_salary_min = normalized_min
        job.normalized_salary_max = normalized_max

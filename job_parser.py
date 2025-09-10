import os
import json
import logging
import argparse
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv

from database import get_db, SessionLocal
from models import JobPageParsed

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobFieldExtractor:
    """
    Extracts missing job fields using OpenAI API
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def has_missing_fields(self, job: JobPageParsed) -> bool:
        """
        Check if job entry has any NULL fields that need extraction
        
        Args:
            job: JobPageParsed instance
            
        Returns:
            bool: True if any target fields are NULL
        """
        target_fields = ['skills', 'seniority', 'education_level', 'secondary_salary_rate', 'secondary_salary_min', 'secondary_salary_max']
        return any(getattr(job, field) is None for field in target_fields)
    
    def get_missing_fields(self, job: JobPageParsed) -> List[str]:
        """
        Get list of NULL fields for a job entry
        
        Args:
            job: JobPageParsed instance
            
        Returns:
            List[str]: List of field names that are NULL
        """
        target_fields = ['skills', 'seniority', 'education_level', 'secondary_salary_rate', 'secondary_salary_min', 'secondary_salary_max']
        return [field for field in target_fields if getattr(job, field) is None]
    
    def prepare_job_text(self, job: JobPageParsed) -> str:
        """
        Concatenate job title and description
        
        Args:
            job: JobPageParsed instance
            
        Returns:
            str: Concatenated title and description
        """
        title = job.job_title or ""
        description = job.description or ""
        return f"{title}\n\n{description}".strip()
    
    def create_openai_prompt(self, job_text: str) -> str:
        """
        Create the OpenAI prompt for field extraction
        
        Args:
            job_text: Concatenated job title and description
            
        Returns:
            str: Formatted prompt for OpenAI
        """
        prompt = """Extract salary information and other fields from the job description text below. Return the output as JSON with these keys:
        secondary_salary_min (float, JSON null if not mentioned or non-numeric)
        secondary_salary_max (float, JSON null if not mentioned or non-numeric)
        secondary_salary_rate (hourly, weekly, monthly, yearly, other based on salary context, JSON null if unclear)
        skills (list of concise strings, JSON null if not mentioned)
        seniority (junior, mid, senior, lead, executive, JSON null if unclear)
        education_level (high school, associate, bachelor, master, PhD, JSON null if not mentioned or equivalent practical experience)

        Salary extraction rules:
        1. REQUIRE compensation context words:
           "offer|compensation|salary|pay|wage|benefits"
           
        2. REQUIRE time period:
           "hour|week|month|year|annual"
           
        3. IGNORE if near business words:
           "manage|oversee|grow|drive|revenue|budget|portfolio|quota"

        Examples:
        VALID 
        - "salary: $50k/year"
        - "compensation range: $20-25/hour"
        - "we offer $60k annually"
        
        INVALID 
        - "manage $1M budget"
        - "$2M revenue business"
        - "$500k sales quota"

        Other rules:
        - For skills, provide concise keywords without descriptors.
        - For education, prefer null if degree is optional or equivalent experience is mentioned.
        - For all fields, ensure 'null' is a JSON null, not a string.

        Job information: {job_text}"""
        
        return prompt.format(job_text=job_text)
    
    def extract_fields_with_openai(self, job_text: str) -> Optional[Dict[str, Any]]:
        """
        Call OpenAI API to extract job fields
        
        Args:
            job_text: Concatenated job title and description
            
        Returns:
            Optional[Dict[str, Any]]: Extracted fields or None if failed
        """
        try:
            prompt = self.create_openai_prompt(job_text)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            parsed_response = response.choices[0].message.content
            try:
                data = json.loads(parsed_response)
                # Convert top-level string 'null' to None
                for key, value in data.items():
                    if isinstance(value, str) and value.lower() == 'null':
                        data[key] = None
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return None
    
    def update_job_fields(self, db: Session, job: JobPageParsed, extracted_data: Dict[str, Any]) -> bool:
        """
        Update job entry with extracted fields (only NULL fields)
        
        Args:
            db: Database session
            job: JobPageParsed instance
            extracted_data: Dictionary with extracted field values
            
        Returns:
            bool: True if any updates were made
        """
        updated = False
        
        try:
            # Only update NULL fields
            if job.secondary_salary_rate is None and extracted_data.get('secondary_salary_rate'):
                job.secondary_salary_rate = extracted_data['secondary_salary_rate']
                updated = True
                logger.info(f"Updated secondary_salary_rate for job {job.id}: {job.secondary_salary_rate}")
            
            if job.secondary_salary_min is None and extracted_data.get('secondary_salary_min'):
                job.secondary_salary_min = extracted_data['secondary_salary_min']
                updated = True
                logger.info(f"Updated secondary_salary_min for job {job.id}: {job.secondary_salary_min}")
            
            if job.secondary_salary_max is None and extracted_data.get('secondary_salary_max'):
                job.secondary_salary_max = extracted_data['secondary_salary_max']
                updated = True
                logger.info(f"Updated secondary_salary_max for job {job.id}: {job.secondary_salary_max}")
            
            if job.skills is None and extracted_data.get('skills'):
                # Convert list to comma-separated string for SQLite compatibility
                if isinstance(extracted_data['skills'], list):
                    job.skills = ','.join(extracted_data['skills'])
                else:
                    job.skills = str(extracted_data['skills'])
                updated = True
                logger.info(f"Updated skills for job {job.id}: {job.skills}")
            
            if job.seniority is None and extracted_data.get('seniority'):
                job.seniority = extracted_data['seniority']
                updated = True
                logger.info(f"Updated seniority for job {job.id}: {job.seniority}")
            
            if job.education_level is None and extracted_data.get('education_level'):
                job.education_level = extracted_data['education_level']
                updated = True
                logger.info(f"Updated education_level for job {job.id}: {job.education_level}")
            
            if updated:
                db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update job {job.id}: {e}")
            db.rollback()
            return False
            
        return updated
    
    def process_all_jobs(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Process job entries and extract missing fields
        
        Args:
            limit: Maximum number of jobs to process (None for no limit)
            
        Returns:
            Dict[str, int]: Statistics about processing
        """
        stats = {
            'total_jobs': 0,
            'jobs_processed': 0,
            'jobs_with_missing_fields': 0,
            'jobs_updated': 0,
            'api_failures': 0,
            'limit_reached': False
        }
        
        db = SessionLocal()
        try:
            # Fetch job entries with missing fields
            query = db.query(JobPageParsed)
            
            # Apply limit if specified
            if limit is not None and limit > 0:
                query = query.limit(limit)
                
            jobs = query.all()
            stats['total_jobs'] = len(jobs)
            
            logger.info(f"Found {stats['total_jobs']} job entries" + 
                       (f" (limited to {limit})" if limit else ""))
            
            for job in jobs:
                if not self.has_missing_fields(job):
                    logger.debug(f"Job {job.id} has no missing fields, skipping")
                    continue
                
                stats['jobs_with_missing_fields'] += 1
                missing_fields = self.get_missing_fields(job)
                logger.info(f"Processing job {job.id}, missing fields: {missing_fields}")
                
                # Prepare job text
                job_text = self.prepare_job_text(job)
                if not job_text.strip():
                    logger.warning(f"Job {job.id} has no title or description, skipping")
                    continue
                
                # Extract fields using OpenAI
                extracted_data = self.extract_fields_with_openai(job_text)
                stats['jobs_processed'] += 1
                
                if extracted_data is None:
                    stats['api_failures'] += 1
                    logger.error(f"Failed to extract fields for job {job.id}")
                    continue
                
                # Update database
                if self.update_job_fields(db, job, extracted_data):
                    stats['jobs_updated'] += 1
                
                # Check if we've reached the limit of jobs to process
                if limit is not None and stats['jobs_processed'] >= limit:
                    stats['limit_reached'] = True
                    logger.info(f"Reached processing limit of {limit} jobs")
                    break
                
        except Exception as e:
            logger.error(f"Error processing jobs: {e}")
            db.rollback()
        finally:
            db.close()
        
        return stats

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Extract missing job fields using OpenAI')
    parser.add_argument('--limit', type=int, default=None,
                      help='Maximum number of jobs to process (default: no limit)')
    return parser.parse_args()

def main():
    """
    Main function to run the job field extraction process
    """
    args = parse_arguments()
    logger.info(f"Starting job field extraction process{'' if args.limit is None else f' (limit: {args.limit} jobs)'}")
    
    try:
        extractor = JobFieldExtractor()
        stats = extractor.process_all_jobs(limit=args.limit)
        
        logger.info("Job field extraction completed")
        logger.info(f"Statistics: {stats}")
        
        print("\n=== Job Field Extraction Results ===")
        print(f"Total jobs in database: {stats['total_jobs']}")
        print(f"Jobs with missing fields: {stats['jobs_with_missing_fields']}")
        print(f"Jobs processed with OpenAI: {stats['jobs_processed']}")
        print(f"Jobs successfully updated: {stats['jobs_updated']}")
        print(f"API failures: {stats['api_failures']}")
        if args.limit and stats['limit_reached']:
            print(f"\nNote: Processing stopped after reaching the limit of {args.limit} jobs")
        
    except Exception as e:
        logger.error(f"Job field extraction failed: {e}")
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

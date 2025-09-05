import os
import json
import logging
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
        target_fields = ['salary', 'skills', 'seniority', 'education_level']
        return any(getattr(job, field) is None for field in target_fields)
    
    def get_missing_fields(self, job: JobPageParsed) -> List[str]:
        """
        Get list of NULL fields for a job entry
        
        Args:
            job: JobPageParsed instance
            
        Returns:
            List[str]: List of field names that are NULL
        """
        target_fields = ['salary', 'skills', 'seniority', 'education_level']
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
        prompt = """Extract the following fields from the job description below. Return the output as JSON with these keys:
salary (string, null if not mentioned)
skills (list of strings, null if not mentioned)
seniority (junior, mid, senior, lead, executive, null if unclear)
education_level (high school, associate, bachelor, master, PhD, null if not mentioned)

Rules: Only use information present in the description. Do not guess or invent values. If a field is missing or unclear, return null.

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
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON from the response
            try:
                # Remove any markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                extracted_data = json.loads(content)
                return extracted_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response content: {content}")
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
            if job.salary is None and extracted_data.get('salary'):
                job.salary = extracted_data['salary']
                updated = True
                logger.info(f"Updated salary for job {job.id}: {job.salary}")
            
            if job.skills is None and extracted_data.get('skills'):
                # Convert list to comma-separated string for SQLite compatibility
                if isinstance(extracted_data['skills'], list):
                    job.skills = ', '.join(extracted_data['skills'])
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
    
    def process_all_jobs(self) -> Dict[str, int]:
        """
        Process all job entries and extract missing fields
        
        Returns:
            Dict[str, int]: Statistics about processing
        """
        stats = {
            'total_jobs': 0,
            'jobs_with_missing_fields': 0,
            'jobs_processed': 0,
            'jobs_updated': 0,
            'api_failures': 0
        }
        
        db = SessionLocal()
        try:
            # Fetch all job entries
            jobs = db.query(JobPageParsed).all()
            stats['total_jobs'] = len(jobs)
            
            logger.info(f"Found {stats['total_jobs']} job entries")
            
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
                
        except Exception as e:
            logger.error(f"Error processing jobs: {e}")
            db.rollback()
        finally:
            db.close()
        
        return stats


def main():
    """
    Main function to run the job field extraction process
    """
    logger.info("Starting job field extraction process")
    
    try:
        extractor = JobFieldExtractor()
        stats = extractor.process_all_jobs()
        
        logger.info("Job field extraction completed")
        logger.info(f"Statistics: {stats}")
        
        print("\n=== Job Field Extraction Results ===")
        print(f"Total jobs in database: {stats['total_jobs']}")
        print(f"Jobs with missing fields: {stats['jobs_with_missing_fields']}")
        print(f"Jobs processed with OpenAI: {stats['jobs_processed']}")
        print(f"Jobs successfully updated: {stats['jobs_updated']}")
        print(f"API failures: {stats['api_failures']}")
        
    except Exception as e:
        logger.error(f"Job field extraction failed: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

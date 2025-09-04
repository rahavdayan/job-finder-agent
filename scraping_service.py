#!/usr/bin/env python3
"""
Scraping Service Script for We Work Remotely

This script scrapes job listings from We Work Remotely's landing page,
extracts individual job URLs, fetches the raw HTML content of each job page,
and stores them in the JOB_PAGES_RAW database table.
"""

from bs4 import BeautifulSoup
from typing import Optional
import re
from sqlalchemy.orm import Session
from urllib.parse import urljoin, urlparse
import time
import logging
from datetime import datetime, timedelta
from typing import List, Set, Optional
import sys
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import Base, JobPageRaw, JobPageParsed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrape.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeWorkRemotelyScraper:
    """Scraper for We Work Remotely job listings"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://weworkremotely.com"
        self.landing_page_url = "https://weworkremotely.com/remote-jobs"
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless, slow_mo=100)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            bypass_csp=True
        )
        self.page = self.context.new_page()
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0

    def close(self):
        """Deterministically clean up Playwright resources to avoid EPIPE on shutdown."""
        try:
            if hasattr(self, 'page') and self.page:
                try:
                    self.page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
                finally:
                    self.page = None
            if hasattr(self, 'context') and self.context:
                try:
                    self.context.close()
                except Exception as e:
                    logger.warning(f"Error closing browser context: {e}")
                finally:
                    self.context = None
            if hasattr(self, 'browser') and self.browser:
                try:
                    self.browser.close()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
                finally:
                    self.browser = None
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    self.playwright.stop()
                except Exception as e:
                    logger.warning(f"Error stopping Playwright: {e}")
                finally:
                    self.playwright = None
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Clean up Playwright resources"""
        try:
            self.close()
        except Exception:
            # Prevent any exceptions from being raised during cleanup
            pass
        
    def _respect_delay(self):
        """Ensure we're not making requests too quickly"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def fetch_landing_page(self, save_to_file: Optional[str] = None) -> str:
        """Fetch the HTML content of the We Work Remotely landing page using Playwright"""
        try:
            self._respect_delay()
            logger.info(f"Fetching landing page: {self.landing_page_url}")
            
            # Navigate to the page and wait for it to fully load
            try:
                self.page.goto(self.landing_page_url, timeout=60000)  # 60 second timeout
                # Wait for the main content to be visible
                self.page.wait_for_selector('body', timeout=30000)
            except PlaywrightTimeoutError as e:
                logger.warning(f"Timeout while loading page: {e}")
                # Try to get the content anyway
            
            # Get the page content
            html_content = self.page.content()
            
            # Save HTML snapshot locally for debugging
            if save_to_file:
                with open(save_to_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Saved landing page HTML to {save_to_file}")

            return html_content
            
        except Exception as e:
            logger.error(f"Error fetching landing page: {e}")
            # Take a screenshot for debugging
            if hasattr(self, 'page'):
                self.page.screenshot(path='error_screenshot.png')
                logger.info("Saved error screenshot to error_screenshot.png")
            raise
    
    def extract_landing_page_info(self, html_content: str) -> tuple[list[str], list[str]]:
        """
        Extract job information from the landing page HTML.
        
        Returns:
            tuple[list[str], list[str]]: A tuple containing two lists:
                - First list contains job URLs
                - Second list contains corresponding company locations
        """
        try:
            soup = BeautifulSoup(html_content, 'html5lib')
            job_urls = []
            locations = []
            seen_urls = set()
            
            # Find all job listing containers
            job_containers = soup.select('[id^="category-"] > article > ul > li')
            
            for container in job_containers:
                try:
                    # Extract job link
                    link_elem = container.find('a', href=lambda x: x and x.startswith('/remote-jobs/'))
                    if not link_elem or not link_elem.get('href'):
                        continue
                        
                    # Create absolute URL
                    job_url = f"{self.base_url}{link_elem['href']}"
                    
                    # Skip if we've already seen this URL
                    if job_url in seen_urls:
                        continue
                        
                    # Extract location from the company headquarters element
                    location_elem = link_elem.select_one('p.new-listing__company-headquarters')
                    location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                    
                    job_urls.append(job_url)
                    locations.append(location)
                    seen_urls.add(job_url)
                    
                except Exception as e:
                    logger.warning(f"Error processing job container: {e}")
                    continue
            
            return job_urls, locations
            
        except Exception as e:
            logger.error(f"Error extracting job information: {e}")
            return [], []
    
    def fetch_job_page(self, job_url: str) -> str:
        """Fetch the raw HTML content of a single job page using Playwright"""
        try:
            self._respect_delay()
            logger.info(f"Fetching job page: {job_url}")
            
            # Navigate to the job page
            try:
                self.page.goto(job_url, timeout=60000)  # 60 second timeout
                # Wait for the main content to be visible
                self.page.wait_for_selector('body', timeout=30000)
            except PlaywrightTimeoutError as e:
                logger.warning(f"Timeout while loading job page: {e}")
                # Try to get the content anyway
            
            # Get the page content
            html_content = self.page.content()
            
            # Verify we got HTML back
            if not html_content.strip() or '<html' not in html_content.lower():
                logger.warning("No valid HTML content received from job page")
                
            return html_content
            
        except Exception as e:
            logger.error(f"Error fetching job page {job_url}: {e}")
            # Take a screenshot for debugging
            if hasattr(self, 'page'):
                self.page.screenshot(path=f'error_job_{job_url.split("/")[-1]}.png')
                logger.info(f"Saved error screenshot to error_job_{job_url.split('/')[-1]}.png")
            raise
    
    def clear_existing_data(self, db: Session):
        """Clear all existing data from both JOB_PAGES_PARSED and JOB_PAGES_RAW tables.
        Delete parsed records first due to foreign key constraints.
        """
        try:
            # Delete from parsed first to satisfy FK to raw
            parsed_deleted = db.query(JobPageParsed).delete()
            raw_deleted = db.query(JobPageRaw).delete()
            db.commit()
            logger.info(
                f"Cleared existing records: JOB_PAGES_PARSED={parsed_deleted}, JOB_PAGES_RAW={raw_deleted}"
            )
        except Exception as e:
            logger.error(f"Error clearing existing data: {e}")
            db.rollback()
            raise
    
    def save_job_page(self, db: Session, url: str, raw_html: str):
        """
        Save a job page's raw HTML to the database
        
        Args:
            db: Database session
            url: Job posting URL
            raw_html: Raw HTML content of the job page
        """
        try:
            job_page = JobPageRaw(
                url=url,
                raw_html=raw_html,
                timestamp=datetime.utcnow()
            )
            db.add(job_page)
            db.commit()
            logger.info(f"Saved job page: {url}")
            return job_page.id
        except Exception as e:
            logger.error(f"Error saving job page {url}: {e}")
            db.rollback()
            raise
            
    def parse_job_page(self, db: Session, raw_html: str, job_page_raw_id: int, location: str):
        """
        Parse job details from raw HTML and save to JobPageParsed table
        
        Args:
            db: Database session
            raw_html: Raw HTML content of the job page
            job_page_raw_id: ID of the corresponding raw job page
            location: Company location from the job listing
        """
        def parse_relative_date(relative_date_str):
            """Convert relative date string to actual date"""
            try:
                today = datetime.utcnow().date()
                if 'hour' in relative_date_str or 'minute' in relative_date_str:
                    return today
                
                num = int(''.join(filter(str.isdigit, relative_date_str)))
                
                if 'day' in relative_date_str:
                    return today - timedelta(days=num)
                elif 'week' in relative_date_str:
                    return today - timedelta(weeks=num)
                elif 'month' in relative_date_str:
                    # Approximate month as 30 days
                    return today - timedelta(days=num*30)
                return today
            except Exception as e:
                logger.warning(f"Error parsing date '{relative_date_str}': {e}")
                return None

        try:
            soup = BeautifulSoup(raw_html, 'html5lib')
            
            # Extract job title
            title_elem = soup.select_one('h2.lis-container__header__hero__company-info__title')
            job_title = title_elem.get_text(strip=True) if title_elem else None
            
            # Extract employer
            employer_elem = soup.select_one('.lis-container__job__sidebar__companyDetails__info__title h3')
            employer = employer_elem.get_text(strip=True) if employer_elem else None
            
            # Extract date posted
            date_posted = None
            date_elem = next(
                (li for li in soup.find_all('li', class_='lis-container__job__sidebar__job-about__list__item')
                 if 'Posted on' in li.get_text()),
                None
            )
            if date_elem:
                date_span = date_elem.find('span')
                if date_span:
                    date_posted = parse_relative_date(date_span.get_text(strip=True))
            
            # Extract salary
            salary_min = None
            salary_max = None
            salary_elem = next(
                (li for li in soup.find_all('li', class_='lis-container__job__sidebar__job-about__list__item')
                 if 'Salary' in li.get_text()),
                None
            )
            if salary_elem:
                salary_span = salary_elem.find('span', class_='box box--blue')
                if salary_span:
                    salary_text = salary_span.get_text(strip=True)
                    # Normalize text and extract numeric parts
                    # Examples:
                    # "$75,000 - $99,999 USD" -> min=75000, max=99999
                    # "$100,000 or more USD" -> min=100000, max=None
                    numbers = [int(n.replace(',', '')) for n in re.findall(r"\$?([0-9][0-9,]*)", salary_text)]
                    if 'or more' in salary_text.lower():
                        if numbers:
                            salary_min = numbers[0]
                            salary_max = None
                    elif len(numbers) >= 2:
                        salary_min, salary_max = numbers[0], numbers[1]
                    elif len(numbers) == 1:
                        # Single number without explicit range; treat as min
                        salary_min = numbers[0]
            
            # Extract job type
            job_type = None
            job_type_elem = next(
                (li for li in soup.find_all('li', class_='lis-container__job__sidebar__job-about__list__item')
                 if 'Job type' in li.get_text()),
                None
            )
            if job_type_elem:
                job_type_span = job_type_elem.find('span', class_='box--jobType')
                if job_type_span:
                    job_type = job_type_span.get_text(strip=True)
            
            # Extract skills
            skills = None
            skills_list = []
            skills_elem = next(
                (li for li in soup.find_all('li', class_='lis-container__job__sidebar__job-about__list__item')
                 if 'Skills' in li.get_text()),
                None
            )
            if skills_elem:
                skill_boxes = skills_elem.find_all('span', class_='box--multi')
                skills_list = [box.get_text(strip=True) for box in skill_boxes]
                skills = ','.join(skills_list)  # Convert list to comma-separated string
            
            # Extract job description
            description = None
            description_elem = soup.select_one('div.lis-container__job__content__description')
            if description_elem:
                # Save inner HTML only (remove outer div wrapper)
                description = description_elem.decode_contents()
            
            # Create parsed job entry
            parsed_job = JobPageParsed(
                job_page_raw_id=job_page_raw_id,
                job_title=job_title,
                employer=employer,
                location=location,
                date_posted=date_posted,
                salary_min=salary_min,
                salary_max=salary_max,
                job_type=job_type,
                skills=skills,
                description=description,
                seniority=None,  # Not explicitly available
                education_level=None,  # Not explicitly available
                timestamp=datetime.utcnow()
            )
            
            db.add(parsed_job)
            db.commit()
            logger.info(f"Parsed and saved job details for raw ID {job_page_raw_id}")
            
        except Exception as e:
            logger.error(f"Error parsing job page {job_page_raw_id}: {e}")
            db.rollback()
            raise
    
    def run_scraping(self, max_jobs: Optional[int] = None):
        """
        Main method to run the complete scraping process
        
        Args:
            max_jobs: Maximum number of jobs to process (None for no limit)
        """
        logger.info(f"Starting We Work Remotely scraping process{'' if max_jobs is None else f' (max {max_jobs} jobs)'}")
        
        # Create database tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Step 1: Clear existing data
            self.clear_existing_data(db)
            
            # Step 2: Fetch landing page
            landing_html = self.fetch_landing_page()
            
            # Step 3: Extract job URLs and locations
            job_urls, locations = self.extract_landing_page_info(landing_html)
            
            if not job_urls or not locations or len(job_urls) != len(locations):
                logger.warning("No valid job information found on the landing page")
                return
            
            # Step 4: Fetch and save each job page
            successful_saves = 0
            failed_saves = 0
            saved_jobs = []  # Store (job_id, location) for parsing step
            
            # Apply max_jobs limit if specified
            if max_jobs is not None:
                job_urls = job_urls[:max_jobs]
                locations = locations[:max_jobs]
                
            for i, (job_url, location) in enumerate(zip(job_urls, locations), 1):
                try:
                    logger.info(f"Processing job {i}/{len(job_urls)}: {job_url}")
                    
                    # Fetch job page HTML
                    job_html = self.fetch_job_page(job_url)
                    
                    # Save to database and store the ID for parsing
                    job_id = self.save_job_page(db, job_url, job_html)
                    saved_jobs.append((job_id, location))
                    successful_saves += 1
                    
                    # Add a small delay to be respectful to the server
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to process job {job_url}: {e}")
                    failed_saves += 1
                    continue
            
            logger.info(f"Scraping completed. Successfully saved: {successful_saves}, Failed: {failed_saves}")
            
            # Step 5: Parse saved job pages
            if saved_jobs:
                logger.info("Starting to parse saved job pages...")
                successful_parses = 0
                failed_parses = 0
                
                for job_id, location in saved_jobs:
                    try:
                        # Get the raw job page from database
                        job_page = db.query(JobPageRaw).filter(JobPageRaw.id == job_id).first()
                        if job_page:
                            self.parse_job_page(db, job_page.raw_html, job_id, location)
                            successful_parses += 1
                        else:
                            logger.warning(f"Job page with ID {job_id} not found for parsing")
                            failed_parses += 1
                            
                    except Exception as e:
                        logger.error(f"Failed to parse job {job_id}: {e}")
                        failed_parses += 1
                        continue
                
                logger.info(f"Parsing completed. Successfully parsed: {successful_parses}, Failed: {failed_parses}")
            
        except Exception as e:
            logger.error(f"Critical error during scraping process: {e}")
            raise
        finally:
            db.close()

def main():
    """Main entry point for the scraping script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape job listings from We Work Remotely')
    parser.add_argument('--max-jobs', type=int, default=None,
                      help='Maximum number of jobs to process (default: None)')
    args = parser.parse_args()
    
    scraper = None
    try:
        scraper = WeWorkRemotelyScraper()
        scraper.run_scraping(max_jobs=args.max_jobs)
        logger.info("Scraping process completed successfully")
    except Exception as e:
        logger.error(f"Scraping process failed: {e}")
        sys.exit(1)
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()

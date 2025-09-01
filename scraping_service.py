#!/usr/bin/env python3
"""
Scraping Service Script for We Work Remotely

This script scrapes job listings from We Work Remotely's landing page,
extracts individual job URLs, fetches the raw HTML content of each job page,
and stores them in the JOB_PAGES_RAW database table.
"""

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from urllib.parse import urljoin, urlparse
import time
import logging
from datetime import datetime
from typing import List, Set, Optional
import sys
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import Base, JobPageRaw

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
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
    
    def __del__(self):
        """Clean up Playwright resources"""
        try:
            if hasattr(self, 'page') and self.page:
                try:
                    self.page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
            
            if hasattr(self, 'context') and self.context:
                try:
                    self.context.close()
                except Exception as e:
                    logger.warning(f"Error closing browser context: {e}")
            
            if hasattr(self, 'browser') and self.browser:
                try:
                    self.browser.close()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
            
            if hasattr(self, 'playwright') and self.playwright:
                try:
                    self.playwright.stop()
                except Exception as e:
                    logger.warning(f"Error stopping Playwright: {e}")
        except Exception as e:
            # Prevent any exceptions from being raised during cleanup
            logger.warning(f"Error during cleanup: {e}")
        
    def _respect_delay(self):
        """Ensure we're not making requests too quickly"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def fetch_landing_page(self, save_to_file: str = "landing_page.html") -> str:
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
    
    def extract_job_urls(self, html_content: str) -> List[str]:
        """Extract individual job URLs from the landing page HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html5lib')
            
            # Find all job listing containers and extract hrefs
            job_links = [a['href'] for a in soup.select('[id^="category-"] > article > ul > li > a[href^="/remote-jobs/"]') 
                        if a.get('href') and not any(skip in a['href'].lower() for skip in ['#', 'javascript:', 'mailto:'])]
            
            # Convert to absolute URLs and remove duplicates
            seen = set()
            return [f"{self.base_url}{url}" for url in job_links if url not in seen and not seen.add(url)]
            
        except Exception as e:
            logger.error(f"Error extracting job URLs: {e}")
            return []
    
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
        """Clear all existing data from JOB_PAGES_RAW table"""
        try:
            deleted_count = db.query(JobPageRaw).delete()
            db.commit()
            logger.info(f"Cleared {deleted_count} existing records from JOB_PAGES_RAW table")
        except Exception as e:
            logger.error(f"Error clearing existing data: {e}")
            db.rollback()
            raise
    
    def save_job_page(self, db: Session, url: str, raw_html: str):
        """Save a job page's raw HTML to the database"""
        try:
            job_page = JobPageRaw(
                url=url,
                raw_html=raw_html,
                timestamp=datetime.utcnow()
            )
            db.add(job_page)
            db.commit()
            logger.info(f"Saved job page: {url}")
        except Exception as e:
            logger.error(f"Error saving job page {url}: {e}")
            db.rollback()
            raise
    
    def run_scraping(self):
        """Main method to run the complete scraping process"""
        logger.info("Starting We Work Remotely scraping process")
        
        # Create database tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Step 1: Clear existing data
            self.clear_existing_data(db)
            
            # Step 2: Fetch landing page
            landing_html = self.fetch_landing_page()
            
            # Step 3: Extract job URLs
            job_urls = self.extract_job_urls(landing_html)
            
            if not job_urls:
                logger.warning("No job URLs found on the landing page")
                return
            
            # Step 4: Fetch and save each job page
            successful_saves = 0
            failed_saves = 0
            
            for i, job_url in enumerate(job_urls, 1):
                try:
                    logger.info(f"Processing job {i}/{len(job_urls)}: {job_url}")
                    
                    # Fetch job page HTML
                    job_html = self.fetch_job_page(job_url)
                    
                    # Save to database
                    self.save_job_page(db, job_url, job_html)
                    successful_saves += 1
                    
                    # Add a small delay to be respectful to the server
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to process job {job_url}: {e}")
                    failed_saves += 1
                    continue
            
            logger.info(f"Scraping completed. Successfully saved: {successful_saves}, Failed: {failed_saves}")
            
        except Exception as e:
            logger.error(f"Critical error during scraping process: {e}")
            raise
        finally:
            db.close()

def main():
    """Main entry point for the scraping script"""
    try:
        scraper = WeWorkRemotelyScraper()
        scraper.run_scraping()
        logger.info("Scraping process completed successfully")
    except Exception as e:
        logger.error(f"Scraping process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

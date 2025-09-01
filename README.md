# Job Finder Agent

A FastAPI-based job finder application that uses AI to help match resumes with appropriate job listings from We Work Remotely.

## Project Structure

```
job-finder-agent/
├── alembic/                 # Database migration files
├── venv/                   # Python virtual environment
├── alembic.ini            # Alembic configuration
├── database.py            # Database connection and session management
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── scraping_service.py    # Main scraping service for We Work Remotely
├── run_scraper.py         # Simple runner script for the scraper
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Setup

1. **Create virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env with your database configuration
   ```

3. **Initialize database:**
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

## Backend Scripts

### 1. Scraping Service Script

**File:** `scraping_service.py`

**Purpose:** Scrapes job listings from We Work Remotely and stores raw HTML in the database.

**Features:**
- Fetches We Work Remotely landing page
- Extracts individual job listing URLs
- Fetches raw HTML content of each job page
- Stores data in `JOB_PAGES_RAW` table
- Clears existing data before each run
- Comprehensive logging and error handling
- Respectful scraping with delays between requests

**Usage:**
```bash
python scraping_service.py
# or
python run_scraper.py
```

**Database Schema:**
```sql
CREATE TABLE job_pages_raw (
    id INTEGER PRIMARY KEY,
    raw_html TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Database Models

### JobPageRaw
- **id**: Primary key (integer)
- **raw_html**: Raw HTML content of the job page (string)
- **url**: Job listing URL (string, unique)
- **timestamp**: When the data was fetched (datetime with timezone)

## Dependencies

- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **Requests**: HTTP library for web scraping
- **BeautifulSoup4**: HTML parsing library
- **python-dotenv**: Environment variable management
- **psycopg2-binary**: PostgreSQL adapter (optional, defaults to SQLite)

## Configuration

The application uses SQLite by default but can be configured to use PostgreSQL by setting the `DATABASE_URL` environment variable:

```
DATABASE_URL=postgresql://username:password@localhost:5432/job_finder_db
```

## Logging

The scraping service logs to both console and `scraping.log` file with detailed information about:
- Fetching progress
- Successful/failed operations
- Error messages and stack traces
- Summary statistics

## Next Steps

This backend foundation is ready for:
1. Job parsing and extraction service
2. AI-powered job matching algorithms
3. Resume analysis and matching
4. FastAPI endpoints for frontend integration
5. User management and preferences

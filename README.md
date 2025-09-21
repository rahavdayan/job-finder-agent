# 🤖 AI-Powered Job Finder Agent

> **An intelligent job matching platform that leverages AI to revolutionize the job search experience**

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai)](https://openai.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org/)

## 🌟 Overview

The **AI-Powered Job Finder Agent** is a sophisticated full-stack application that transforms how job seekers discover opportunities. By combining advanced AI technologies with intelligent matching algorithms, it provides personalized job recommendations with detailed compatibility scoring.

### 🎯 Key AI Features

- **🧠 AI Resume Parser**: Automatically extracts skills, experience, and qualifications using OpenAI GPT-4o-mini
- **🎯 Intelligent Job Matching**: Advanced scoring algorithm that evaluates job compatibility across multiple dimensions
- **📊 Smart Scoring System**: Multi-factor analysis including skills overlap, title similarity, and salary positioning
- **🔍 Semantic Search**: Context-aware job discovery that understands intent beyond keywords

## 🤖 AI-Powered Components

### 1. **Intelligent Resume Parser**
- **Technology**: OpenAI GPT-4o-mini model
- **Capabilities**: 
  - Extracts structured data from PDF/DOCX resumes
  - Identifies seniority levels (Junior → Manager)
  - Parses technical and soft skills
  - Determines education levels
  - Handles missing data gracefully

### 2. **Advanced Job Matching Algorithm**
- **Multi-dimensional Scoring**:
  - **Skills Match (40%)**: Semantic analysis of skill overlap
  - **Title Similarity (30%)**: NLP-based job title matching
  - **Job Type Compatibility (20%)**: Employment type preferences
  - **Salary Optimization (10%)**: Position within desired range

### 3. **Smart User Experience**
- **Adaptive Forms**: Pre-fills data from AI-parsed resumes
- **Real-time Scoring**: Live compatibility percentages
- **Intelligent Filtering**: Context-aware job filtering
- **Persistent Preferences**: Maintains user criteria across sessions

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks + localStorage
- **UI Components**: Custom responsive components

### Backend
- **Framework**: FastAPI (Python)
- **AI Integration**: OpenAI API (GPT-4o-mini)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Processing**: PyPDF2, python-docx
- **API Documentation**: Auto-generated OpenAPI/Swagger

### AI & Data Processing
- **Resume Parsing**: OpenAI GPT-4o-mini
- **Text Processing**: Custom NLP algorithms
- **Scoring Engine**: Multi-factor compatibility analysis
- **Data Validation**: Comprehensive error handling

## 📁 Project Structure

```
job-finder-agent/
├── frontend/                 # Next.js 14 application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── services/        # API integration layer
│   │   └── types/           # TypeScript definitions
│   └── package.json
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── db/             # Database models & config
│   │   └── main.py         # Application entry point
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL
- OpenAI API key

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/job-finder-agent.git
cd job-finder-agent
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Add your OpenAI API key and database URL
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Configure API URL
```

### 4. Database Setup
```bash
# Create PostgreSQL database
# Run migrations (if applicable)
```

### 5. Launch Application
```bash
# Terminal 1 - Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

Visit `http://localhost:3000` to see the application in action!

## 🎯 Key Features Showcase

### 🤖 AI Resume Processing
```python
# Intelligent resume parsing with OpenAI
async def parse_resume(file: UploadFile):
    content = extract_text(file)
    
    prompt = """
    Extract structured data from this resume:
    - Seniority level (Junior/Mid/Senior/Manager)
    - Job titles from experience
    - Technical and soft skills
    - Education level
    """
    
    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"{prompt}\n\n{content}"}]
    )
    
    return parse_structured_response(response)
```

### 🎯 Intelligent Job Matching
```python
def calculate_match_score(job, user_criteria):
    # Multi-dimensional scoring algorithm
    scores = {
        'skills': calculate_skills_overlap(job.skills, user_criteria.skills),
        'title': calculate_title_similarity(job.title, user_criteria.titles),
        'job_type': calculate_job_type_match(job.type, user_criteria.types),
        'salary': calculate_salary_score(job.salary, user_criteria.salary_range)
    }
    
    # Weighted final score
    return (
        scores['skills'] * 0.4 +
        scores['title'] * 0.3 +
        scores['job_type'] * 0.2 +
        scores['salary'] * 0.1
    )
```

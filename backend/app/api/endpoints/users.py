from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

from app.services.resume_parser import ResumeParser
from app.api.schemas.resume import ResumeParseResponse

router = APIRouter()
resume_parser = ResumeParser()

@router.post("/resume", response_model=ResumeParseResponse)
async def upload_resume(file: UploadFile = File(...)) -> ResumeParseResponse:
    """
    Upload and parse a resume file (PDF or DOCX).
    Returns structured data extracted from the resume.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = Path(file.filename).suffix
    if file_extension.lower() not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Only PDF and DOCX files are supported"
        )
    
    file_content = await file.read()
    return await resume_parser.parse_resume(file_content, file_extension)

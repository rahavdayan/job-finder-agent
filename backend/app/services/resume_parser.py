import json
from typing import Optional
import PyPDF2
import docx
from openai import OpenAI
from fastapi import HTTPException

from app.api.schemas.resume import ResumeParseResponse

class ResumeParser:
    def __init__(self):
        self.client = OpenAI()

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(file_content)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    def _extract_text_from_docx(self, file_content: bytes) -> str:
        try:
            doc = docx.Document(file_content)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

    def extract_text(self, file_content: bytes, file_extension: str) -> str:
        if file_extension.lower() == ".pdf":
            return self._extract_text_from_pdf(file_content)
        elif file_extension.lower() in [".docx", ".doc"]:
            return self._extract_text_from_docx(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

    async def parse_resume(self, file_content: bytes, file_extension: str) -> ResumeParseResponse:
        try:
            resume_text = self.extract_text(file_content, file_extension)
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a resume parser. Extract the following information from the resume:
                    - Seniority level (Junior, Mid-level, Senior, Lead, or Manager)
                    - List of job titles from previous positions
                    - List of skills (both technical and soft skills)
                    - Education level (high school, BSc, MSc, or PhD)
                    
                    Return the information in JSON format. If any information is not found or unclear, leave that field empty."""},
                    {"role": "user", "content": resume_text}
                ],
                response_format={"type": "json_object"}
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            return ResumeParseResponse(**parsed_data)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

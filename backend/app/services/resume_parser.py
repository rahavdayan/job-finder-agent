import json
import io
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
            # Convert bytes to BytesIO for PyPDF2
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    def _extract_text_from_docx(self, file_content: bytes) -> str:
        try:
            # Convert bytes to BytesIO for python-docx
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
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
            
            if not resume_text.strip():
                raise HTTPException(status_code=400, detail="No text could be extracted from the file")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a resume parser. Extract the following information from the resume:
                    - seniority: Seniority level (Junior, Mid-level, Senior, Lead, or Manager)
                    - job_titles: List of job titles from previous positions
                    - skills: List of skills (both technical and soft skills)
                    - education_level: Education level (high school, BSc, MSc, or PhD)
                    
                    Return the information in JSON format with these exact field names. If any information is not found or unclear, use null for that field.
                    
                    Example response:
                    {
                        "seniority": "Senior",
                        "job_titles": ["Software Engineer", "Senior Developer"],
                        "skills": ["Python", "JavaScript", "Leadership"],
                        "education_level": "BSc"
                    }"""},
                    {"role": "user", "content": f"Please parse this resume:\n\n{resume_text}"}
                ],
                response_format={"type": "json_object"}
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            
            # Ensure the response matches our schema
            return ResumeParseResponse(
                seniority=parsed_data.get("seniority"),
                job_titles=parsed_data.get("job_titles"),
                skills=parsed_data.get("skills"),
                education_level=parsed_data.get("education_level")
            )
            
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error parsing OpenAI response: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

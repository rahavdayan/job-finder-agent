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

    async def validate_resume(self, text: str) -> bool:
        """
        Validate if the extracted text is actually from a resume document.
        Returns True if it's a resume, False otherwise.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a document classifier. Your task is to determine if the provided text is from a resume/CV document or not.

A resume/CV typically contains:
- Personal information (name, contact details)
- Work experience with job titles and descriptions
- Education information
- Skills section
- Professional summary or objective

Return a JSON response with:
- "is_resume": boolean (true if it's a resume, false otherwise)
- "confidence": number between 0-1 (confidence level)
- "reason": string (brief explanation of your decision)

Examples of what IS a resume:
- Documents with work history, education, and skills
- Professional profiles with career experience
- CVs with academic or professional background

Examples of what IS NOT a resume:
- Random text documents
- Academic papers or articles
- Legal documents
- Marketing materials
- Personal letters
- Technical manuals
- Fiction or creative writing"""},
                    {"role": "user", "content": f"Please analyze this document and determine if it's a resume:\n\n{text[:2000]}"}  # Limit to first 2000 chars for efficiency
                ],
                response_format={"type": "json_object"}
            )
            
            validation_result = json.loads(response.choices[0].message.content)
            is_resume = validation_result.get("is_resume", False)
            confidence = validation_result.get("confidence", 0)
            reason = validation_result.get("reason", "Unknown")
            
            # Require high confidence for validation
            if not is_resume or confidence < 0.7:
                raise HTTPException(
                    status_code=400, 
                    detail=f"The uploaded document does not appear to be a resume. Reason: {reason} (Confidence: {confidence:.2f})"
                )
            
            return True
            
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error validating document: {str(e)}")
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during document validation: {str(e)}")

    async def parse_resume(self, file_content: bytes, file_extension: str) -> ResumeParseResponse:
        try:
            resume_text = self.extract_text(file_content, file_extension)
            
            if not resume_text.strip():
                raise HTTPException(status_code=400, detail="No text could be extracted from the file")
            
            # Validate that the document is actually a resume
            await self.validate_resume(resume_text)
            
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
        except HTTPException:
            raise  # Re-raise HTTP exceptions (including validation errors) without wrapping
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

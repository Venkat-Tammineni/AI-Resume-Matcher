from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pdfplumber, io
import logging
import os
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud, models
from app.gemini_interface import get_resume_feedback, extract_skills_with_gemini  # Added import

# Add this debug print
print(f"Gemini API Key present: {'GEMINI_API_KEY' in os.environ}")

router = APIRouter(prefix="/resume", tags=["Resume"])

# Configure logging to exclude debug messages from PDF processing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence any low-level PDF processing logs
logging.getLogger('pdfplumber').setLevel(logging.WARNING)
logging.getLogger('pdfminer').setLevel(logging.WARNING)

@router.post("/upload", response_model=schemas.ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    try:
        contents = await file.read()
        pdf_stream = io.BytesIO(contents)

        with pdfplumber.open(pdf_stream) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

        if not text.strip():
            raise HTTPException(status_code=422, detail="Could not extract any text from the PDF.")

        # Save resume without feedback
        try:
            resume_data = schemas.ResumeCreate(filename=file.filename, content=text)
            saved_resume = crud.create_resume(db=db, resume=resume_data)
            return saved_resume
        except Exception as db_error:
            logger.error(f"Database error while saving resume: {str(db_error)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to save resume to database. Please try again."
            )

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing resume file. Please ensure the file is valid."
        )

@router.get("/feedback/{resume_id}", response_model=schemas.ResumeOut)
async def get_resume_ai_feedback(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        feedback = get_resume_feedback(resume.content)
        if not feedback:
            logger.warning("Gemini API returned empty feedback")
            feedback = "Unable to generate feedback at this time."
        updated_resume = crud.update_resume_feedback(db, resume.id, feedback)
        return updated_resume
    except Exception as gemini_error:
        logger.error(f"Gemini API error: {str(gemini_error)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI feedback. Please try again later."
        )

@router.get("/match/{resume_id}")
async def match_resume_to_jobs(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        # Extract skills specifically for job matching
        skill_prompt = "Extract only the technical skills from this resume as a comma-separated list. Include only the skill names and do not add any feedback:"
        resume_skills_text = get_resume_feedback(skill_prompt + "\n" + resume.content)
        resume_skills = [skill.lower().strip() for skill in resume_skills_text.split(',') if skill.strip()]

        job_list = crud.get_all_jobs(db)
        matches = []

        for job in job_list:
            # Clean and normalize job skills
            job_skills = [skill.lower().strip() for skill in job.skills_required.split(',') if skill.strip()]
            
            # Find matching skills
            matching_skills = set(resume_skills) & set(job_skills)
            
            # Calculate match score
            match_score = 0
            if job_skills:  # Prevent division by zero
                match_score = (len(matching_skills) / len(job_skills)) * 100

            if match_score > 0:  # Only include jobs with some match
                matches.append({
                    "job_id": job.id,
                    "title": job.title,
                    "location": job.location,
                    "match_score": round(match_score, 2),
                    "matching_skills": list(matching_skills),
                    "required_skills": job_skills,
                    "missing_skills": list(set(job_skills) - set(resume_skills))
                })

        # Sort matches by score in descending order and get top 5
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        top_matches = matches[:5]

        return {
            "resume_id": resume_id,
            "candidate_skills": resume_skills,
            "job_matches": top_matches,
            "total_matches_found": len(matches),  # Added for context
            "showing_top": min(5, len(matches))   # Shows actual number of matches returned
        }
    except Exception as e:
        logger.error(f"Error matching resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error matching resume to jobs. Please try again later."
        )

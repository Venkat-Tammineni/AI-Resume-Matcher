from sqlalchemy.orm import Session
from app import models, schemas

def create_resume(db: Session, resume: schemas.ResumeCreate):
    db_resume = models.Resume(**resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def update_resume_feedback(db: Session, resume_id: int, feedback: str):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if resume:
        resume.ai_feedback = feedback
        db.commit()
        db.refresh(resume)
    return resume


def get_all_jobs(db: Session):
    return db.query(models.Job).all()

def match_resume_to_jobs(resume_skills: list[str], job_list: list[models.Job]) -> list[dict]:
    matches = []

    for job in job_list:
        job_skills = [skill.strip().lower() for skill in job.skills_required.split(",")]
        overlap = set(resume_skills).intersection(set(job_skills))
        score = len(overlap) / len(job_skills)  # Simple match % based on skill overlap

        matches.append({
            "job_id": job.id,
            "title": job.title,
            "location": job.location,
            "match_score": round(score * 100, 2)
        })

    # Sort by highest match
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:5]


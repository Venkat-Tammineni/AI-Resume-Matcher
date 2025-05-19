from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ResumeCreate(BaseModel):
    filename: str
    content: str

class ResumeOut(BaseModel):
    id: int
    filename: str
    content: str
    uploaded_at: datetime
    ai_feedback: Optional[str]
    

    class Config:
       from_attributes = True
        
class JobOut(BaseModel):
    id: int
    title: str
    description: str
    location: str
    skills_required: str

    class Config:
        from_attributes = True


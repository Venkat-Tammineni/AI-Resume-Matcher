from fastapi import FastAPI
from app.routers import resume
from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Resume Matcher",
    description="Upload a PDF resume and extract its content using pdfplumber.",
    version="1.0.0"
)

# Include the resume upload router
app.include_router(resume.router)

# Optional: Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Matcher API"}

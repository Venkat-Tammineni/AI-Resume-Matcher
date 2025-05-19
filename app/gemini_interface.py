import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_resume_feedback(resume_text: str) -> str:
    if not GEMINI_API_KEY:
        return "Gemini API key not found."

    # Updated API endpoint URL to use v1beta
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Analyze this resume text and give specific feedback:\
                    \n1. Missing skills\n2. Tone improvement\n3. Clarity\n4. ATS tips\n\nResume:\n{resume_text}"}
                ]
            }
        ]
    }

    try:
        response = requests.post(
            f"{url}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        
        logger.info(f"API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = f"Gemini API error: {response.text}"
            logger.error(error_msg)
            return error_msg

    except Exception as e:
        error_msg = f"Error calling Gemini API: {str(e)}"
        logger.error(error_msg)
        return error_msg

def extract_skills_with_gemini(resume_text: str) -> list[str]:
    prompt = f"From the following resume text, extract a comma-separated list of technical and soft skills:\n\n{resume_text}"
    
    # Use get_resume_feedback instead of call_gemini
    response_text = get_resume_feedback(prompt)
    
    # Post-process (split and clean)
    if isinstance(response_text, str):
        return [skill.strip() for skill in response_text.split(",") if skill.strip()]
    return []


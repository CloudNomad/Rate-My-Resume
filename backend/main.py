from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz
import spacy
from typing import Dict, List
import json
from functools import lru_cache
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class ResumeAnalysisError(Exception):
    pass

def validate_pdf(file: UploadFile) -> None:
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    if file.size > int(os.getenv('MAX_FILE_SIZE', 5 * 1024 * 1024)):  # Default 5MB limit
        raise HTTPException(status_code=400, detail="File too large")

def extract_text_from_pdf(file: UploadFile) -> str:
    content = file.file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@lru_cache(maxsize=int(os.getenv('CACHE_SIZE', 100)))
def analyze_resume(text: str) -> Dict:
    doc = nlp(text)
    
    # Basic metrics
    word_count = len([token.text for token in doc if not token.is_punct])
    sentence_count = len(list(doc.sents))
    
    # Action verbs detection
    action_verbs = ["developed", "created", "implemented", "managed", "led", "increased", "improved", "achieved"]
    found_verbs = [token.text.lower() for token in doc if token.text.lower() in action_verbs]
    
    # Technical skills detection
    tech_skills = ["python", "javascript", "react", "node", "sql", "aws", "docker", "kubernetes"]
    found_skills = [skill for skill in tech_skills if skill in text.lower()]
    missing_skills = [skill for skill in tech_skills if skill not in text.lower()]
    
    # Passive voice detection
    passive_voice = []
    for sent in doc.sents:
        if any(token.dep_ == "auxpass" for token in sent):
            passive_voice.append(sent.text)
    
    # Calculate score
    score = min(100, (
        len(found_verbs) * 10 +  # Action verbs
        len(found_skills) * 5 +  # Technical skills
        (word_count // 10) -     # Content length
        len(passive_voice) * 5   # Penalty for passive voice
    ))
    
    # Generate suggestions
    suggestions = []
    if len(found_verbs) < 3:
        suggestions.append("Add more action verbs to describe your achievements")
    if word_count < 200:
        suggestions.append("Consider adding more details to your experience")
    if missing_skills:
        suggestions.append(f"Add these missing technical skills: {', '.join(missing_skills)}")
    if passive_voice:
        suggestions.append("Consider rewriting passive voice sentences")
    
    return {
        "score": score,
        "metrics": {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "action_verbs_found": len(found_verbs),
            "technical_skills_found": len(found_skills),
            "passive_voice_sentences": len(passive_voice)
        },
        "suggestions": suggestions,
        "strengths": [
            "Good structure" if sentence_count > 5 else "Needs more content",
            f"Strong technical skills: {', '.join(found_skills)}" if found_skills else None
        ],
        "weaknesses": [
            "Limited action verbs" if len(found_verbs) < 3 else "Good use of action verbs",
            f"Missing key technical skills: {', '.join(missing_skills)}" if missing_skills else None,
            "Contains passive voice" if passive_voice else None
        ]
    }

@app.post("/analyze")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    try:
        validate_pdf(file)
        text = await asyncio.to_thread(extract_text_from_pdf, file)
        if not text.strip():
            raise ResumeAnalysisError("Could not extract text from PDF")
        return await asyncio.to_thread(analyze_resume, text)
    except ResumeAnalysisError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
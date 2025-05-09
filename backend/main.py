from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz
import spacy
from typing import Dict, List, Optional
import json
from functools import lru_cache
import asyncio
import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel

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

class ResumeSection(BaseModel):
    title: str
    content: str
    score: float
    suggestions: List[str]

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

def detect_sections(text: str) -> Dict[str, str]:
    # Common section headers
    section_patterns = {
        'education': r'(?i)(education|academic|qualification)',
        'experience': r'(?i)(experience|work|employment|professional)',
        'skills': r'(?i)(skills|technical|competencies)',
        'projects': r'(?i)(projects|portfolio)',
        'contact': r'(?i)(contact|email|phone|address)'
    }
    
    sections = {}
    lines = text.split('\n')
    current_section = 'summary'
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line matches any section header
        found_section = False
        for section, pattern in section_patterns.items():
            if re.search(pattern, line):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section
                current_content = []
                found_section = True
                break
                
        if not found_section:
            current_content.append(line)
    
    # Add the last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def analyze_section(section_name: str, content: str) -> ResumeSection:
    doc = nlp(content)
    
    # Section-specific analysis
    if section_name == 'skills':
        return analyze_skills_section(content)
    elif section_name == 'experience':
        return analyze_experience_section(content)
    elif section_name == 'education':
        return analyze_education_section(content)
    elif section_name == 'contact':
        return analyze_contact_section(content)
    
    # Default analysis
    return ResumeSection(
        title=section_name,
        content=content,
        score=0.0,
        suggestions=[]
    )

def analyze_skills_section(content: str) -> ResumeSection:
    # Technical skills database
    tech_skills = {
        'programming': ['python', 'javascript', 'java', 'c++', 'ruby', 'go', 'rust'],
        'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express'],
        'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis'],
        'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
        'tools': ['git', 'jenkins', 'jira', 'confluence']
    }
    
    found_skills = []
    missing_skills = []
    
    for category, skills in tech_skills.items():
        for skill in skills:
            if skill in content.lower():
                found_skills.append(skill)
            else:
                missing_skills.append(skill)
    
    score = min(100, len(found_skills) * 10)
    suggestions = []
    
    if len(found_skills) < 5:
        suggestions.append("Add more technical skills to strengthen your profile")
    if missing_skills:
        suggestions.append(f"Consider adding these in-demand skills: {', '.join(missing_skills[:3])}")
    
    return ResumeSection(
        title="Skills",
        content=content,
        score=score,
        suggestions=suggestions
    )

def analyze_experience_section(content: str) -> ResumeSection:
    doc = nlp(content)
    
    # Action verbs analysis
    action_verbs = ["developed", "created", "implemented", "managed", "led", "increased", 
                   "improved", "achieved", "delivered", "optimized", "designed", "architected"]
    found_verbs = [token.text.lower() for token in doc if token.text.lower() in action_verbs]
    
    # Metrics and achievements
    metrics_pattern = r'\d+%|\$\d+|\d+x|\d+% increase|\d+% reduction'
    metrics = re.findall(metrics_pattern, content)
    
    # Passive voice detection
    passive_voice = [sent.text for sent in doc.sents if any(token.dep_ == "auxpass" for token in sent)]
    
    score = min(100, (
        len(found_verbs) * 5 +    # Action verbs
        len(metrics) * 10 +       # Quantifiable achievements
        -len(passive_voice) * 5   # Penalty for passive voice
    ))
    
    suggestions = []
    if len(found_verbs) < 3:
        suggestions.append("Add more action verbs to describe your achievements")
    if len(metrics) < 2:
        suggestions.append("Include more quantifiable achievements and metrics")
    if passive_voice:
        suggestions.append("Consider rewriting passive voice sentences to be more impactful")
    
    return ResumeSection(
        title="Experience",
        content=content,
        score=score,
        suggestions=suggestions
    )

def analyze_education_section(content: str) -> ResumeSection:
    # Education keywords
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'gpa']
    found_keywords = [keyword for keyword in education_keywords if keyword in content.lower()]
    
    # Date detection
    date_pattern = r'\d{4}'
    dates = re.findall(date_pattern, content)
    
    score = min(100, (
        len(found_keywords) * 10 +  # Education keywords
        len(dates) * 5             # Dates found
    ))
    
    suggestions = []
    if len(found_keywords) < 3:
        suggestions.append("Add more details about your educational background")
    if len(dates) < 2:
        suggestions.append("Include graduation dates for your degrees")
    
    return ResumeSection(
        title="Education",
        content=content,
        score=score,
        suggestions=suggestions
    )

def analyze_contact_section(content: str) -> ResumeSection:
    # Contact information patterns
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    
    email = re.search(email_pattern, content)
    phone = re.search(phone_pattern, content)
    linkedin = re.search(linkedin_pattern, content)
    
    score = min(100, (
        bool(email) * 30 +
        bool(phone) * 30 +
        bool(linkedin) * 40
    ))
    
    suggestions = []
    if not email:
        suggestions.append("Add your email address")
    if not phone:
        suggestions.append("Include your phone number")
    if not linkedin:
        suggestions.append("Add your LinkedIn profile URL")
    
    return ResumeSection(
        title="Contact",
        content=content,
        score=score,
        suggestions=suggestions
    )

@lru_cache(maxsize=int(os.getenv('CACHE_SIZE', 100)))
def analyze_resume(text: str) -> Dict:
    # Detect and analyze sections
    sections = detect_sections(text)
    section_analyses = {name: analyze_section(name, content) for name, content in sections.items()}
    
    # Calculate overall score
    overall_score = sum(section.score for section in section_analyses.values()) / len(section_analyses)
    
    # Combine all suggestions
    all_suggestions = []
    for section in section_analyses.values():
        all_suggestions.extend(section.suggestions)
    
    # Identify strengths and weaknesses
    strengths = []
    weaknesses = []
    
    for name, section in section_analyses.items():
        if section.score >= 70:
            strengths.append(f"Strong {name} section")
        elif section.score < 50:
            weaknesses.append(f"{name.title()} section needs improvement")
    
    return {
        "score": round(overall_score, 1),
        "sections": {
            name: {
                "score": section.score,
                "suggestions": section.suggestions
            }
            for name, section in section_analyses.items()
        },
        "suggestions": all_suggestions,
        "strengths": strengths,
        "weaknesses": weaknesses
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
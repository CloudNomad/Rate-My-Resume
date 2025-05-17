from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import fitz
import spacy
from typing import Dict, List, Optional, Set
import json
from functools import lru_cache
import asyncio
import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import random

from database import get_db
from models import User, ResumeVersion

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

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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
    details: Dict[str, any] = {}

class ResumeVersion(BaseModel):
    id: str
    user_id: str
    content: str
    score: float
    created_at: datetime
    version_name: str
    file_path: str

# Industry-specific keywords and skills
INDUSTRY_KEYWORDS = {
    'software_engineering': {
        'keywords': ['software', 'development', 'engineering', 'programming', 'coding'],
        'skills': {
            'programming': ['python', 'javascript', 'java', 'c++', 'ruby', 'go', 'rust', 'typescript', 'swift', 'kotlin'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node.js', 'laravel', 'asp.net'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'github', 'gitlab', 'bitbucket']
        }
    },
    'data_science': {
        'keywords': ['data', 'analytics', 'machine learning', 'ai', 'statistics'],
        'skills': {
            'programming': ['python', 'r', 'sql', 'scala', 'julia'],
            'libraries': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras'],
            'tools': ['jupyter', 'tableau', 'power bi', 'spark', 'hadoop'],
            'techniques': ['regression', 'classification', 'clustering', 'nlp', 'computer vision']
        }
    },
    'product_management': {
        'keywords': ['product', 'management', 'strategy', 'roadmap', 'agile'],
        'skills': {
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall'],
            'tools': ['jira', 'confluence', 'figma', 'productboard', 'amplitude'],
            'concepts': ['user stories', 'mvp', 'product lifecycle', 'market research']
        }
    }
}

# Achievement metrics patterns
ACHIEVEMENT_PATTERNS = {
    'percentage': r'\d+%',
    'monetary': r'\$\d+(?:\.\d+)?(?:K|M|B)?',
    'time': r'\d+(?:x|times)',
    'reduction': r'\d+% reduction|\d+% decrease',
    'increase': r'\d+% increase|\d+% growth',
    'scale': r'\d+(?:K|M|B) users|\d+(?:K|M|B) customers',
    'efficiency': r'\d+% efficiency|\d+% improvement',
    'cost': r'\$\d+(?:K|M|B)? savings|\$\d+(?:K|M|B)? reduction'
}

# In-memory storage for demo (replace with database in production)
resume_versions = {}

# Developer mode flag
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

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
        'contact': r'(?i)(contact|email|phone|address)',
        'summary': r'(?i)(summary|profile|objective)',
        'certifications': r'(?i)(certifications|certificates|accreditations)',
        'languages': r'(?i)(languages|language proficiency)'
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

def detect_industry(text: str) -> str:
    max_matches = 0
    detected_industry = 'general'
    
    for industry, data in INDUSTRY_KEYWORDS.items():
        matches = sum(1 for keyword in data['keywords'] if keyword.lower() in text.lower())
        if matches > max_matches:
            max_matches = matches
            detected_industry = industry
    
    return detected_industry

def analyze_achievements(content: str) -> Dict[str, List[str]]:
    achievements = defaultdict(list)
    
    for metric_type, pattern in ACHIEVEMENT_PATTERNS.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            context = content[max(0, match.start() - 50):min(len(content), match.end() + 50)]
            achievements[metric_type].append({
                'value': match.group(),
                'context': context.strip()
            })
    
    return dict(achievements)

def analyze_skills_section(content: str, industry: str = 'software_engineering') -> ResumeSection:
    industry_data = INDUSTRY_KEYWORDS.get(industry, INDUSTRY_KEYWORDS['software_engineering'])
    skills_data = industry_data['skills']
    
    found_skills = defaultdict(list)
    missing_skills = defaultdict(list)
    
    for category, skills in skills_data.items():
        for skill in skills:
            if skill in content.lower():
                found_skills[category].append(skill)
            else:
                missing_skills[category].append(skill)
    
    # Calculate category scores
    category_scores = {}
    for category in skills_data.keys():
        if category in found_skills:
            category_scores[category] = min(100, len(found_skills[category]) * 20)
        else:
            category_scores[category] = 0
    
    # Calculate overall score
    score = min(100, sum(category_scores.values()) / len(category_scores))
    
    suggestions = []
    if len(found_skills) < 3:
        suggestions.append("Add more technical skills to strengthen your profile")
    
    # Category-specific suggestions
    for category, skills in missing_skills.items():
        if len(found_skills.get(category, [])) < 2:
            suggestions.append(f"Consider adding more {category} skills: {', '.join(skills[:3])}")
    
    return ResumeSection(
        title="Skills",
        content=content,
        score=score,
        suggestions=suggestions,
        details={
            'found_skills': dict(found_skills),
            'missing_skills': dict(missing_skills),
            'category_scores': category_scores
        }
    )

def analyze_experience_section(content: str) -> ResumeSection:
    doc = nlp(content)
    
    # Action verbs analysis
    action_verbs = ["developed", "created", "implemented", "managed", "led", "increased", 
                   "improved", "achieved", "delivered", "optimized", "designed", "architected",
                   "launched", "initiated", "coordinated", "facilitated", "established",
                   "enhanced", "streamlined", "revolutionized", "pioneered", "spearheaded"]
    
    found_verbs = [token.text.lower() for token in doc if token.text.lower() in action_verbs]
    
    # Analyze achievements
    achievements = analyze_achievements(content)
    
    # Passive voice detection
    passive_voice = [sent.text for sent in doc.sents if any(token.dep_ == "auxpass" for token in sent)]
    
    # Calculate scores for different aspects
    verb_score = min(100, len(found_verbs) * 5)
    achievement_score = min(100, sum(len(achievements[metric]) for metric in achievements) * 10)
    passive_penalty = len(passive_voice) * 5
    
    # Overall score
    score = min(100, (verb_score + achievement_score - passive_penalty))
    
    suggestions = []
    if len(found_verbs) < 3:
        suggestions.append("Add more action verbs to describe your achievements")
    if not any(len(achievements[metric]) > 0 for metric in achievements):
        suggestions.append("Include more quantifiable achievements and metrics")
    if passive_voice:
        suggestions.append("Consider rewriting passive voice sentences to be more impactful")
    
    return ResumeSection(
        title="Experience",
        content=content,
        score=score,
        suggestions=suggestions,
        details={
            'action_verbs': found_verbs,
            'achievements': achievements,
            'passive_voice': passive_voice,
            'aspect_scores': {
                'action_verbs': verb_score,
                'achievements': achievement_score,
                'passive_voice_penalty': passive_penalty
            }
        }
    )

def analyze_education_section(content: str) -> ResumeSection:
    # Education keywords
    education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'gpa']
    found_keywords = [keyword for keyword in education_keywords if keyword in content.lower()]
    
    # Date detection
    date_pattern = r'\d{4}'
    dates = re.findall(date_pattern, content)
    
    # GPA detection
    gpa_pattern = r'(?:GPA|gpa)[:\s]*(\d+\.\d+)'
    gpa_match = re.search(gpa_pattern, content)
    gpa = float(gpa_match.group(1)) if gpa_match else None
    
    # Degree detection
    degree_pattern = r'(?:Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.)[\w\s]*'
    degrees = re.findall(degree_pattern, content)
    
    score = min(100, (
        len(found_keywords) * 10 +  # Education keywords
        len(dates) * 5 +           # Dates found
        (20 if gpa else 0) +       # GPA bonus
        len(degrees) * 15          # Degree bonus
    ))
    
    suggestions = []
    if len(found_keywords) < 3:
        suggestions.append("Add more details about your educational background")
    if len(dates) < 2:
        suggestions.append("Include graduation dates for your degrees")
    if not gpa and 'gpa' not in content.lower():
        suggestions.append("Consider adding your GPA if it's above 3.0")
    if not degrees:
        suggestions.append("Specify your degree(s) clearly")
    
    return ResumeSection(
        title="Education",
        content=content,
        score=score,
        suggestions=suggestions,
        details={
            'degrees': degrees,
            'dates': dates,
            'gpa': gpa,
            'found_keywords': found_keywords
        }
    )

def analyze_contact_section(content: str) -> ResumeSection:
    # Contact information patterns
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    github_pattern = r'github\.com/[\w-]+'
    portfolio_pattern = r'(?:https?://)?(?:www\.)?[\w-]+\.(?:com|io|dev|app)'
    
    email = re.search(email_pattern, content)
    phone = re.search(phone_pattern, content)
    linkedin = re.search(linkedin_pattern, content)
    github = re.search(github_pattern, content)
    portfolio = re.search(portfolio_pattern, content)
    
    score = min(100, (
        bool(email) * 25 +
        bool(phone) * 25 +
        bool(linkedin) * 20 +
        bool(github) * 15 +
        bool(portfolio) * 15
    ))
    
    suggestions = []
    if not email:
        suggestions.append("Add your email address")
    if not phone:
        suggestions.append("Include your phone number")
    if not linkedin:
        suggestions.append("Add your LinkedIn profile URL")
    if not github:
        suggestions.append("Consider adding your GitHub profile")
    if not portfolio:
        suggestions.append("Add your portfolio website if available")
    
    return ResumeSection(
        title="Contact",
        content=content,
        score=score,
        suggestions=suggestions,
        details={
            'email': email.group() if email else None,
            'phone': phone.group() if phone else None,
            'linkedin': linkedin.group() if linkedin else None,
            'github': github.group() if github else None,
            'portfolio': portfolio.group() if portfolio else None
        }
    )

@lru_cache(maxsize=int(os.getenv('CACHE_SIZE', 100)))
def analyze_resume(text: str) -> Dict:
    # Detect industry
    industry = detect_industry(text)
    
    # Detect and analyze sections
    sections = detect_sections(text)
    section_analyses = {name: analyze_section(name, content, industry) for name, content in sections.items()}
    
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
        "industry": industry,
        "sections": {
            name: {
                "score": section.score,
                "suggestions": section.suggestions,
                "details": section.details
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

@app.post("/save-version")
async def save_resume_version(
    file: UploadFile = File(...),
    user_id: str = None,
    version_name: str = None,
    db: Session = Depends(get_db)
):
    try:
        validate_pdf(file)
        
        # Save file to disk
        file_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract and analyze text
        text = await asyncio.to_thread(extract_text_from_pdf, file)
        if not text.strip():
            raise ResumeAnalysisError("Could not extract text from PDF")
        
        analysis = await asyncio.to_thread(analyze_resume, text)
        
        # Get or create user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, email=f"{user_id}@example.com")
            db.add(user)
            db.commit()
        
        # Create version
        version = ResumeVersion(
            user_id=user.id,
            content=text,
            score=analysis["score"],
            version_name=version_name or f"Version {len(user.versions) + 1}",
            file_path=str(file_path)
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return {"version_id": version.id, "score": version.score}
    except Exception as e:
        if 'file_path' in locals():
            file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/versions/{user_id}")
async def get_resume_versions(user_id: str, db: Session = Depends(get_db)):
    versions = db.query(ResumeVersion).filter(ResumeVersion.user_id == user_id).all()
    return sorted(versions, key=lambda x: x.created_at, reverse=True)

@app.get("/compare/{version_id_1}/{version_id_2}")
async def compare_versions(version_id_1: str, version_id_2: str, db: Session = Depends(get_db)):
    v1 = db.query(ResumeVersion).filter(ResumeVersion.id == version_id_1).first()
    v2 = db.query(ResumeVersion).filter(ResumeVersion.id == version_id_2).first()
    
    if not v1 or not v2:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Compare scores
    score_diff = v2.score - v1.score
    
    # Compare sections
    sections_1 = detect_sections(v1.content)
    sections_2 = detect_sections(v2.content)
    
    changes = {
        "score_difference": score_diff,
        "created_at_difference": (v2.created_at - v1.created_at).total_seconds(),
        "section_changes": {}
    }
    
    # Compare each section
    for section in set(sections_1.keys()) | set(sections_2.keys()):
        if section not in sections_1:
            changes["section_changes"][section] = "Added in new version"
        elif section not in sections_2:
            changes["section_changes"][section] = "Removed in new version"
        elif sections_1[section] != sections_2[section]:
            changes["section_changes"][section] = "Modified"
    
    return changes

@app.delete("/versions/{version_id}")
async def delete_version(version_id: str, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Delete file if it exists
    if version.file_path:
        try:
            Path(version.file_path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    db.delete(version)
    db.commit()
    return {"message": "Version deleted successfully"}

# Test data generation
def generate_test_resume() -> str:
    sections = {
        "summary": "Experienced software engineer with a passion for building scalable applications.",
        "experience": """Senior Software Engineer at Tech Corp (2020-2023)
- Developed and maintained microservices using Python and FastAPI
- Improved system performance by 40% through optimization
- Led a team of 5 developers in implementing CI/CD pipelines

Software Engineer at Startup Inc (2018-2020)
- Built RESTful APIs using Node.js and Express
- Reduced API response time by 30%
- Implemented automated testing with 90% coverage""",
        "education": """Bachelor of Science in Computer Science
University of Technology, 2014-2018
GPA: 3.8/4.0""",
        "skills": """Programming: Python, JavaScript, Java, C++
Frameworks: React, Django, Spring Boot
Databases: PostgreSQL, MongoDB
Tools: Git, Docker, Kubernetes""",
        "projects": """E-commerce Platform
- Built a full-stack e-commerce platform using React and Node.js
- Implemented real-time inventory management
- Achieved 99.9% uptime

AI Chatbot
- Developed an NLP-based chatbot using Python
- Integrated with multiple messaging platforms
- Handled 10,000+ daily conversations"""
    }
    
    return "\n\n".join(f"{section.upper()}\n{content}" for section, content in sections.items())

def generate_test_versions(user_id: str, count: int = 5, db: Session = None) -> List[ResumeVersion]:
    versions = []
    base_score = 75
    base_date = datetime.utcnow() - timedelta(days=30)
    
    for i in range(count):
        # Generate slightly different content for each version
        content = generate_test_resume()
        if i > 0:
            # Add some random improvements
            improvements = [
                "Improved system performance by 50%",
                "Reduced API response time by 40%",
                "Implemented automated testing with 95% coverage",
                "Led a team of 8 developers",
                "Achieved 99.99% uptime"
            ]
            content += f"\n\nAdditional Achievement:\n{random.choice(improvements)}"
        
        # Calculate score with some randomness
        score = min(100, base_score + (i * 5) + random.randint(-2, 2))
        
        version = ResumeVersion(
            user_id=user_id,
            content=content,
            score=score,
            created_at=base_date + timedelta(days=i * 7),
            version_name=f"Test Version {i + 1}",
            file_path=None  # No file for test versions
        )
        
        if db:
            db.add(version)
            db.commit()
            db.refresh(version)
        
        versions.append(version)
    
    return versions

# Developer mode endpoints
if DEV_MODE:
    @app.post("/dev/generate-test-data")
    async def generate_test_data(user_id: str = None, count: int = 5, db: Session = Depends(get_db)):
        if not user_id:
            user_id = f"test_user_{uuid.uuid4()}"
        
        # Create test user
        user = User(id=user_id, email=f"{user_id}@example.com")
        db.add(user)
        db.commit()
        
        # Generate test versions
        versions = generate_test_versions(user_id, count, db)
        
        return {
            "user_id": user_id,
            "versions": versions
        }
    
    @app.get("/dev/test-resume")
    async def get_test_resume():
        return {
            "content": generate_test_resume(),
            "score": random.randint(70, 90)
        }
    
    @app.delete("/dev/clear-test-data")
    async def clear_test_data(db: Session = Depends(get_db)):
        # Delete all test users and their versions
        test_users = db.query(User).filter(User.email.like("test_user_%")).all()
        for user in test_users:
            db.delete(user)
        db.commit()
        return {"message": "Test data cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
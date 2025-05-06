from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz
import spacy
from typing import Dict, List
import json

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

def extract_text_from_pdf(file: UploadFile) -> str:
    content = file.file.read()
    doc = fitz.open(stream=content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_resume(text: str) -> Dict:
    doc = nlp(text)
    
    # Basic metrics
    word_count = len([token.text for token in doc if not token.is_punct])
    sentence_count = len(list(doc.sents))
    
    # Action verbs detection
    action_verbs = ["developed", "created", "implemented", "managed", "led", "increased", "improved", "achieved"]
    found_verbs = [token.text.lower() for token in doc if token.text.lower() in action_verbs]
    
    # Calculate score (simple version)
    score = min(100, (len(found_verbs) * 10) + (word_count // 10))
    
    # Generate suggestions
    suggestions = []
    if len(found_verbs) < 3:
        suggestions.append("Add more action verbs to describe your achievements")
    if word_count < 200:
        suggestions.append("Consider adding more details to your experience")
    
    return {
        "score": score,
        "metrics": {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "action_verbs_found": len(found_verbs)
        },
        "suggestions": suggestions,
        "strengths": ["Good structure" if sentence_count > 5 else "Needs more content"],
        "weaknesses": ["Limited action verbs" if len(found_verbs) < 3 else "Good use of action verbs"]
    }

@app.post("/analyze")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"error": "Please upload a PDF file"}
    
    text = extract_text_from_pdf(file)
    analysis = analyze_resume(text)
    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
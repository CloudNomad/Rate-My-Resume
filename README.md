# Rate My Resume

An AI-powered web application that analyzes, rates, and provides suggestions for improving resumes.

## Features

- PDF resume upload and analysis
- Resume scoring (0-100)
- Action verb detection
- Content metrics (word count, sentence count)
- Personalized improvement suggestions
- Modern, responsive UI

## Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python main.py
```

The backend will run on http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Click "Select Resume" to choose a PDF file
3. Click "Analyze Resume" to get your resume analysis
4. View your score, metrics, strengths, weaknesses, and suggestions

## Technology Stack

- Frontend: React, Material-UI
- Backend: FastAPI
- NLP: spaCy
- PDF Processing: PyMuPDF 
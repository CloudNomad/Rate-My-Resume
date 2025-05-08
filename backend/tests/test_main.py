import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_endpoint_invalid_file():
    response = client.post("/analyze", files={"file": ("test.txt", b"test content")})
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]

def test_analyze_endpoint_no_file():
    response = client.post("/analyze")
    assert response.status_code == 422

def test_analyze_endpoint_success():
    # Create a simple PDF file for testing
    with open("tests/sample_resume.pdf", "rb") as f:
        response = client.post("/analyze", files={"file": f})
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "metrics" in data
    assert "suggestions" in data
    assert "strengths" in data
    assert "weaknesses" in data 
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "job-matcher"}

def test_perfect_match():
    payload = {
        "candidate": {
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_years": 1,
            "preferred_locations": ["Bangalore"],
            "preferred_roles": ["Backend Developer"],
            "expected_salary": 600000,
            "education": {"degree": "B.Tech", "field": "CS", "cgpa": 8.5}
        },
        "jobs": [
            {
                "job_id": "J001",
                "title": "Backend Developer",
                "required_skills": ["Python", "FastAPI"],
                "experience_required": "0-2 years",
                "location": "Bangalore",
                "salary_range": [600000, 1000000],
                "company": "TechCorp"
            }
        ]
    }
    response = client.post("/match", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["matches"][0]["match_score"] >= 80 #for a good match
    #Test data with a expected score or threshold

def test_partial_match():
    # Candidate missing one skill
    payload = {
        "candidate": {
            "skills": ["Python"],
            "experience_years": 1,
            "preferred_locations": ["Bangalore"],
            "preferred_roles": ["Backend Developer"],
            "expected_salary": 600000,
            "education": {"degree": "B.Tech", "field": "CS", "cgpa": 8.5}
        },
        "jobs": [
            {
                "job_id": "J001",
                "title": "Backend Developer",
                "required_skills": ["Python", "FastAPI"], # 50% skill match
                "experience_required": "0-2 years",
                "location": "Bangalore",
                "salary_range": [600000, 1000000],
                "company": "TechCorp"
            }
        ]
    }
    response = client.post("/match", json=payload)
    data = response.json()
    # Skill weight is 40. Skill match is 50%. So we lose 20 points. Total 80.
    assert data["matches"][0]["match_score"] >= 80.0 #for a descent match
    assert "FastAPI" in data["matches"][0]["missing_skills"]
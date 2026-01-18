# Wevolve Job Matching Engine

## Problem Statement
The Wevolve Job Matching Engine is designed to address the challenge of efficiently matching job candidates to job postings based on multiple factors such as skills, experience, location, and salary expectations. The goal is to provide a ranked list of job matches with detailed scoring breakdowns to help candidates and recruiters make informed decisions.

---

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Sunistha-Agarwal/wevolve-ps1-sunista.git
   cd wevolve-ps1-sunista/backend
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Run Tests**:
   ```bash
   pytest tests/
   ```

---

## How to Run

- Start the server using the `uvicorn` command mentioned above.
- Access the API documentation at `http://127.0.0.1:8000/docs`.

---

## Tech Stack

- **Backend Framework**: FastAPI
- **Machine Learning**: Sentence Transformers (BAAI/bge-base-en-v1.5)
- **Testing**: Pytest
- **Other Libraries**: scikit-learn, NumPy, Pydantic

---

## API Documentation

### Endpoints

1. **Health Check**
   - **URL**: `/`
   - **Method**: `GET`
   - **Response**:
     ```json
     {
       "status": "healthy",
       "service": "job-matcher"
     }
     ```

2. **Match Jobs**
   - **URL**: `/match`
   - **Method**: `POST`
   - **Request Body**:
     ```json
     {
       "candidate": {
         "skills": ["Python", "FastAPI"],
         "experience_years": 2,
         "preferred_locations": ["Bangalore"],
         "preferred_roles": ["Backend Developer"],
         "expected_salary": 600000,
         "education": {
           "degree": "B.Tech",
           "field": "CS",
           "cgpa": 8.5
         }
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
     ```
   - **Response**:
     ```json
     {
       "matches": [
         {
           "job_id": "J001",
           "match_score": 85.0,
           "breakdown": {
             "skill_match": 90.0,
             "location_match": 100.0,
             "salary_match": 80.0,
             "experience_match": 100.0,
             "role_match": 90.0
           },
           "missing_skills": [],
           "recommendation_reason": "Strong skill alignment with 2/2 required skills. Profile closely matches job role."
         }
       ]
     }
     ```

---

## Design Decisions and Approach

1. **Multi-Factor Scoring**: The scoring algorithm considers multiple factors such as skills, location, salary, experience, and role alignment.
2. **Sentence Transformers**: Used for semantic similarity in skill and role matching.
3. **Haversine Formula**: Calculates distance between cities for location matching.
4. **Threshold Filtering**: Only jobs with a match score above 75 are returned.

---

## Challenges Faced and Solutions

1. **Semantic Matching**:
   - **Challenge**: Accurately matching skills and roles.
   - **Solution**: Leveraged pre-trained Sentence Transformers for semantic similarity.

2. **Location Scoring**:
   - **Challenge**: Quantifying location preferences.
   - **Solution**: Implemented the Haversine formula to calculate distances between cities.

3. **Data Validation**:
   - **Challenge**: Ensuring robust input validation.
   - **Solution**: Used Pydantic models for strict schema validation.

---

## Known Limitations

1. **Limited Dataset**: The scoring algorithm relies on the quality of input data.
2. **Static City Coordinates**: Location matching is limited to predefined cities.
3. **No Real-Time Updates**: Job postings and candidate profiles are static in the current implementation.

---

## Future Improvements

1. **Dynamic Data Integration**: Connect to real-time job boards and candidate databases.
2. **Enhanced Location Matching**: Use APIs like Google Maps for dynamic location data.
3. **Customizable Weights**: Allow users to adjust scoring weights for different factors.
4. **Improved Semantic Models**: Fine-tune models for domain-specific skill matching.
5. **UI Development**: Build a user-friendly interface for recruiters and candidates.

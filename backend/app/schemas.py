from typing import List, Optional
from pydantic import BaseModel, Field

# --- Sub-models ---
class Education(BaseModel):
    degree: str
    field: str
    cgpa: float

# --- Input Models ---
class CandidateProfile(BaseModel):
    skills: List[str]
    experience_years: int = Field(..., ge=0)
    preferred_locations: List[str]
    preferred_roles: List[str]
    expected_salary: int = Field(..., gt=0)
    education: Education

class JobPosting(BaseModel):
    job_id: str
    title: str
    required_skills: List[str]
    experience_required: str  # e.g., "0-2 years"
    location: str
    salary_range: List[int]   # [min, max]
    company: str

class MatchingRequest(BaseModel):
    candidate: CandidateProfile
    jobs: List[JobPosting]

# --- Output Models ---
class ScoreBreakdown(BaseModel):
    skill_match: float
    location_match: float
    salary_match: float
    experience_match: float
    role_match: float

class JobMatchResult(BaseModel):
    job_id: str
    match_score: float
    breakdown: ScoreBreakdown
    missing_skills: List[str]
    recommendation_reason: str

class MatchingResponse(BaseModel):
    matches: List[JobMatchResult]
from fastapi import FastAPI, HTTPException
from .schemas import MatchingRequest, MatchingResponse
from .services import match_candidate_to_jobs as MatchingService

app = FastAPI(
    title="Wevolve Job Matching Engine",
    description="A multi-factor scoring algorithm API for job candidates.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "job-matcher"}

@app.post("/match", response_model=MatchingResponse)
def match_jobs(payload: MatchingRequest):
    """
    Evaluates a candidate profile against a list of job postings.
    Returns ranked matches with detailed scoring breakdowns.
    """
    if not payload.jobs:
        return MatchingResponse(matches=[])
    
    try:
        results = MatchingService(payload)
        return results
    except Exception as e:
        # Log error in real production
        raise HTTPException(status_code=500, detail=f"Scoring engine error: {str(e)}")
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import math
from pydantic import BaseModel
from typing import List
from .schemas import MatchingRequest, MatchingResponse, JobMatchResult, ScoreBreakdown

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

import math

def cosine_sim(a,b):
    return cosine_similarity([a],[b])[0][0]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

print(haversine(28.61, 77.23, 19.07, 72.87)) 

CITY_COORDS={
"Bangalore":(12.971600, 77.594600),
"Hyderabad":(17.385000, 78.486700),
"Pune":(18.520400, 73.856700),
"Gurgaon":(28.459500, 77.026600),
"Chennai":(13.082700, 80.270700),
"Noida":(28.535500, 77.391000),
"Mumbai":(19.076000, 72.877700),
"Kolkata": (22.572600, 88.363900),
"Ahmedabad": (23.022500, 72.571400),
"Delhi":(28.613900, 77.209000)
}

def compute_skill_score(cand_skills,job_skills):
    cand_text=" ".join(cand_skills)
    job_text= " ".join(job_skills)
    cand_emb= model.encode(cand_text,normalize_embeddings=True)
    job_emb= model.encode(job_text,normalize_embeddings=True)
    return cosine_sim(cand_emb,job_emb)*100

def compute_role_score(cand_roles,job_title):
    cand_text=" ".join(cand_roles)
    job_text= " ".join(job_title)
    for cand_role in cand_roles:
        if(cand_role==job_title):
            return 100
    cand_emb= model.encode(cand_text,normalize_embeddings=True)
    job_emb= model.encode(job_text,normalize_embeddings=True)
    return cosine_sim(cand_emb,job_emb)*100

def compute_location_score(candidate_locations, job_location , willing_to_relocate=True):
    if job_location=="Remote":
        return 100
    best_score=0
    for city in candidate_locations:
        if city in CITY_COORDS and job_location in CITY_COORDS:
            d= haversine(*CITY_COORDS[city],*CITY_COORDS[job_location])
            if d<=10:
                best_score=max(best_score,100)
            elif d<=50:
                best_score=max(best_score,80)
            elif d<=200:
                best_score=max(best_score,50)
    if best_score==0 and willing_to_relocate:
            best_score=60
    return best_score

def compute_experience_score(cand_exp,job_exp_range):
    min_exp,max_exp= job_exp_range
    if cand_exp >= min_exp:
        return 100
    elif cand_exp>=min_exp-1:
        return 70
    else:
        return 40
    
def compute_salary_score(expected_salary,job_salary_range):
    low,high = job_salary_range
    if expected_salary<=high:
        return 100
    elif expected_salary<=high*1.1:
        return 70
    else:
        return 30

def get_missing_skills(cand_skills,job_skills):
    return list(set(job_skills)-set(cand_skills))       

def generate_reason(skill_score,role_score,location_score,experience_score,missing_skills,matched_skills,job_skills):
    positives=[]
    gaps=[]
    if skill_score>=70:
        positives.append(f"Strong skill alignment with {len(matched_skills)}/{len(job_skills)} required skills")
    if role_score>=80:
        positives.append("Profile closely matche job role")
    if location_score==100:
        positives.append("Preferred location matches job role")
    if experience_score==100:
        positives.append("Experience level matches the requirement")
    if missing_skills:
        gaps.append("Needs to upskill his/her skills")
    
    reason=[]
    if positives:
        reason.append(positives[0])
        if len(positives)>1:
            reason.append(positives[1])
        if gaps:
            reason.append(gaps[0])
        
        return " ".join(reason)
    

def match_candidate_to_jobs(request: MatchingRequest) -> MatchingResponse:
    """
    Processes a MatchingRequest and returns a MatchingResponse.
    """
    candidate = request.candidate
    jobs = request.jobs

    results = []
    for job in jobs:
        skill_score = float(compute_skill_score(candidate.skills, job.required_skills))
        matched_skills = list(set(candidate.skills) & set(job.required_skills))
        role_score = float(compute_role_score(candidate.preferred_roles, job.title))
        location_score = float(compute_location_score(candidate.preferred_locations, job.location))
        experience_score = float(compute_experience_score(candidate.experience_years, parse_experience_range(job.experience_required)))
        salary_score = float(compute_salary_score(candidate.expected_salary, job.salary_range))
        missing_skills = get_missing_skills(candidate.skills, job.required_skills)

        final_match_score = (
            0.4 * skill_score +
            0.2 * role_score +
            0.15 * location_score +
            0.15 * salary_score +
            0.1 * experience_score
        )

        recommendation_reason = generate_reason(
            skill_score, role_score, location_score,
            experience_score, missing_skills, matched_skills, job.required_skills
        )

        #Threshold is set so that jobs with low match score are not shown. only the suitable ones are shown in a priority order
        if final_match_score >= 75:
            results.append(JobMatchResult(
                job_id=job.job_id,
                match_score=round(final_match_score, 1),
                breakdown=ScoreBreakdown(
                    skill_match=round(skill_score, 1),
                    role_match=round(role_score, 1),
                    location_match=round(location_score, 1),
                    salary_match=round(salary_score, 1),
                    experience_match=round(experience_score, 1)
                ),
                missing_skills=missing_skills,
                recommendation_reason=recommendation_reason
            ))

    # Sort results by match score in descending order
    results = sorted(results, key=lambda x: x.match_score, reverse=True)

    return MatchingResponse(matches=results)

# Helper function to parse experience range
def parse_experience_range(exp_str: str):
    """Parses '0-2 years' into (0, 2). Handles edge cases gracefully."""
    try:
        parts = exp_str.lower().replace('years', '').replace('year', '').split('-')
        if len(parts) == 2:
            return int(parts[0].strip()), int(parts[1].strip())
        elif len(parts) == 1 and '+' in parts[0]:
            val = int(parts[0].replace('+', '').strip())
            return val, 100  # Cap at 100 for open-ended
        return 0, 0
    except:
        return 0, 0  # Fallback
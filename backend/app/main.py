import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

app = FastAPI(title="FLUTESTAR Employer Portal API", version="0.2.0")

# ALLOWED_ORIGINS is a comma-separated list of origins, configurable via
# environment variable. Falls back to "*" for local development so nothing
# breaks if the variable is unset, but production deployments MUST set
# ALLOWED_ORIGINS explicitly (see .env.example).
_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if _allowed_origins_env.strip() == "*":
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = False
else:
    ALLOWED_ORIGINS = [o.strip() for o in _allowed_origins_env.split(",") if o.strip()]
    ALLOW_CREDENTIALS = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmployerRegistration(BaseModel):
    company: str = Field(min_length=2, max_length=200)
    contact: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    website: Optional[str] = None
    location: str = Field(min_length=2, max_length=120)
    organization_type: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=3000)

class RequirementSubmission(BaseModel):
    employer_id: int = Field(ge=1)
    requirement: str
    role: str = Field(min_length=2, max_length=200)
    count: int = Field(ge=1, le=10000)
    location: str
    qualification: str
    experience: str
    priority: str
    required_within: str
    start_date: Optional[str] = None
    duration: Optional[str] = None
    target_date: Optional[str] = None
    budget: Optional[str] = None
    skills: str = Field(min_length=2, max_length=5000)
    details: str = Field(min_length=2, max_length=10000)

@app.get("/")
def root():
    return {"service": "FLUTESTAR Employer Portal API", "version": app.version, "status": "running"}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/employers")
def get_employers(
    db: Session = Depends(get_db),
):
    employers = (
        db.query(models.Employer)
        .order_by(models.Employer.id.asc())
        .all()
    )

    return {
        "success": True,
        "count": len(employers),
        "employers": [
            {
                "id": employer.id,
                "company": employer.company,
                "contact": employer.contact,
                "email": employer.email,
                "phone": employer.phone,
                "website": employer.website,
                "location": employer.location,
                "organization_type": employer.organization_type,
                "description": employer.description,
            }
            for employer in employers
        ],
    }

@app.get("/api/employers/{employer_id}")
def get_employer(
    employer_id: int,
    db: Session = Depends(get_db),
):
    employer = (
        db.query(models.Employer)
        .filter(models.Employer.id == employer_id)
        .first()
    )

    if employer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Employer with id {employer_id} not found.",
        )

    return {
        "success": True,
        "employer": {
            "id": employer.id,
            "company": employer.company,
            "contact": employer.contact,
            "email": employer.email,
            "phone": employer.phone,
            "website": employer.website,
            "location": employer.location,
            "organization_type": employer.organization_type,
            "description": employer.description,
        },
    }


@app.get("/api/requirements")
def get_requirements(
    db: Session = Depends(get_db),
):
    requirements = (
        db.query(models.EmployerRequirement)
        .order_by(models.EmployerRequirement.id)
        .all()
    )

    return {
        "success": True,
        "count": len(requirements),
        "requirements": [
            {
                "id": requirement.id,
                "employer_id": requirement.employer_id,
                "requirement": requirement.requirement,
                "role": requirement.role,
                "count": requirement.count,
                "location": requirement.location,
                "qualification": requirement.qualification,
                "experience": requirement.experience,
                "priority": requirement.priority,
                "required_within": requirement.required_within,
                "start_date": requirement.start_date,
                "duration": requirement.duration,
                "target_date": requirement.target_date,
                "budget": requirement.budget,
                "skills": requirement.skills,
                "details": requirement.details,
                "created_at": requirement.created_at,
            }
            for requirement in requirements
        ],
    }

@app.get("/api/requirements/{requirement_id}")
def get_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
):
    requirement = (
        db.query(models.EmployerRequirement)
        .filter(models.EmployerRequirement.id == requirement_id)
        .first()
    )

    if requirement is None:
        raise HTTPException(
            status_code=404,
            detail=f"Requirement with id {requirement_id} not found.",
        )

    return {
        "success": True,
        "requirement": {
            "id": requirement.id,
            "employer_id": requirement.employer_id,
            "requirement": requirement.requirement,
            "role": requirement.role,
            "count": requirement.count,
            "location": requirement.location,
            "qualification": requirement.qualification,
            "experience": requirement.experience,
            "priority": requirement.priority,
            "required_within": requirement.required_within,
            "start_date": requirement.start_date,
            "duration": requirement.duration,
            "target_date": requirement.target_date,
            "budget": requirement.budget,
            "skills": requirement.skills,
            "details": requirement.details,
            "created_at": requirement.created_at,
        },
    }










@app.get("/api/employer/lookup")
def lookup_employer_by_email(
    email: str,
    db: Session = Depends(get_db),
):
    """
    MVP employer lookup by business email, used by the frontend "existing
    employer" login screen.

    NOTE - KNOWN LIMITATION: this endpoint does not check a password. It is
    intentionally an MVP stand-in until real authentication (password
    hashing + session/JWT) is implemented. Do not treat this as a secure
    login in production; see Phase 6 security notes in the project docs.
    """
    employer = (
        db.query(models.Employer)
        .filter(models.Employer.email == email)
        .first()
    )

    if employer is None:
        raise HTTPException(
            status_code=404,
            detail="No employer found with that business email.",
        )

    return {
        "success": True,
        "employer": {
            "id": employer.id,
            "company": employer.company,
            "contact": employer.contact,
            "email": employer.email,
            "phone": employer.phone,
            "website": employer.website,
            "location": employer.location,
            "organization_type": employer.organization_type,
            "description": employer.description,
        },
    }


@app.get("/api/employers/{employer_id}/requirements")
def get_employer_requirements(
    employer_id: int,
    db: Session = Depends(get_db),
):
    employer = db.get(models.Employer, employer_id)

    if employer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Employer with id {employer_id} not found.",
        )

    requirements = (
        db.query(models.EmployerRequirement)
        .filter(models.EmployerRequirement.employer_id == employer_id)
        .order_by(models.EmployerRequirement.id)
        .all()
    )

    return {
        "success": True,
        "employer_id": employer.id,
        "company": employer.company,
        "count": len(requirements),
        "requirements": [
            {
                "id": requirement.id,
                "employer_id": requirement.employer_id,
                "requirement": requirement.requirement,
                "role": requirement.role,
                "count": requirement.count,
                "location": requirement.location,
                "qualification": requirement.qualification,
                "experience": requirement.experience,
                "priority": requirement.priority,
                "required_within": requirement.required_within,
                "start_date": requirement.start_date,
                "duration": requirement.duration,
                "target_date": requirement.target_date,
                "budget": requirement.budget,
                "skills": requirement.skills,
                "details": requirement.details,
                "created_at": requirement.created_at,
            }
            for requirement in requirements
        ],
    }


@app.post("/api/employer/register")
def register_employer(
    payload: EmployerRegistration,
    db: Session = Depends(get_db),
):
    employer = models.Employer(
        company=payload.company,
        contact=payload.contact,
        email=str(payload.email),
        phone=payload.phone,
        website=payload.website,
        location=payload.location,
        organization_type=payload.organization_type,
        description=payload.description,
    )

    db.add(employer)
    db.commit()
    db.refresh(employer)

    return {
        "success": True,
        "message": "Employer registration saved successfully.",
        "employer_id": employer.id,
        "storage": "sqlite",
    }

@app.post("/api/employer/requirement")
def submit_requirement(
    payload: RequirementSubmission,
    db: Session = Depends(get_db),
):
    employer = db.get(models.Employer, payload.employer_id)

    if employer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Employer with id {payload.employer_id} not found."
        )


    requirement = models.EmployerRequirement(
        employer_id=payload.employer_id,
	requirement=payload.requirement,
        role=payload.role,
        count=payload.count,
        location=payload.location,
        qualification=payload.qualification,
        experience=payload.experience,
        priority=payload.priority,
        required_within=payload.required_within,
        start_date=payload.start_date,
        duration=payload.duration,
        target_date=payload.target_date,
        budget=payload.budget,
        skills=payload.skills,
        details=payload.details,
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return {
        "success": True,
        "message": "Employer requirement saved successfully.",
        "requirement_id": requirement.id,
        "storage": "sqlite",
    }

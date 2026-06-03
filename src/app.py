"""
Slalom Capabilities Management System API

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models import Capability, CapabilityConsultant

app = FastAPI(title="Slalom Capabilities Management API",
              description="API for managing consulting capabilities and consultant expertise")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

INITIAL_CAPABILITIES = {
    "Cloud Architecture": {
        "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["AWS Solutions Architect", "Azure Architect Expert"],
        "industry_verticals": ["Healthcare", "Financial Services", "Retail"],
        "capacity": 40,  # hours per week available across team
        "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"]
    },
    "Data Analytics": {
        "description": "Advanced data analysis, visualization, and machine learning solutions",
        "practice_area": "Technology", 
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Tableau Desktop Specialist", "Power BI Expert", "Google Analytics"],
        "industry_verticals": ["Retail", "Healthcare", "Manufacturing"],
        "capacity": 35,
        "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"]
    },
    "DevOps Engineering": {
        "description": "CI/CD pipeline design, infrastructure automation, and containerization",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"], 
        "certifications": ["Docker Certified Associate", "Kubernetes Admin", "Jenkins Certified"],
        "industry_verticals": ["Technology", "Financial Services"],
        "capacity": 30,
        "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"]
    },
    "Digital Strategy": {
        "description": "Digital transformation planning and strategic technology roadmaps",
        "practice_area": "Strategy",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Digital Transformation Certificate", "Agile Certified Practitioner"],
        "industry_verticals": ["Healthcare", "Financial Services", "Government"],
        "capacity": 25,
        "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"]
    },
    "Change Management": {
        "description": "Organizational change leadership and adoption strategies",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Prosci Certified", "Lean Six Sigma Black Belt"],
        "industry_verticals": ["Healthcare", "Manufacturing", "Government"],
        "capacity": 20,
        "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"]
    },
    "UX/UI Design": {
        "description": "User experience design and digital product innovation",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Adobe Certified Expert", "Google UX Design Certificate"],
        "industry_verticals": ["Retail", "Healthcare", "Technology"],
        "capacity": 30,
        "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"]
    },
    "Cybersecurity": {
        "description": "Information security strategy, risk assessment, and compliance",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["CISSP", "CISM", "CompTIA Security+"],
        "industry_verticals": ["Financial Services", "Healthcare", "Government"],
        "capacity": 25,
        "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"]
    },
    "Business Intelligence": {
        "description": "Enterprise reporting, data warehousing, and business analytics",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Microsoft BI Certification", "Qlik Sense Certified"],
        "industry_verticals": ["Retail", "Manufacturing", "Financial Services"],
        "capacity": 35,
        "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"]
    },
    "Agile Coaching": {
        "description": "Agile transformation and team coaching for scaled delivery",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Certified Scrum Master", "SAFe Agilist", "ICAgile Certified"],
        "industry_verticals": ["Technology", "Financial Services", "Healthcare"],
        "capacity": 20,
        "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"]
    }
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_capabilities(db: Session) -> None:
    if db.query(Capability).first():
        return

    for capability_name, payload in INITIAL_CAPABILITIES.items():
        capability = Capability(
            name=capability_name,
            description=payload["description"],
            practice_area=payload["practice_area"],
            skill_levels=payload["skill_levels"],
            certifications=payload["certifications"],
            industry_verticals=payload["industry_verticals"],
            capacity=payload["capacity"],
        )
        db.add(capability)
        db.flush()

        for consultant_email in payload["consultants"]:
            db.add(
                CapabilityConsultant(
                    capability_id=capability.id,
                    email=consultant_email,
                )
            )

    db.commit()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with SessionLocal() as db:
        seed_initial_capabilities(db)


def build_capabilities_response(db: Session) -> dict:
    response = {}
    capabilities = db.query(Capability).all()
    for capability in capabilities:
        response[capability.name] = {
            "description": capability.description,
            "practice_area": capability.practice_area,
            "skill_levels": capability.skill_levels,
            "certifications": capability.certifications,
            "industry_verticals": capability.industry_verticals,
            "capacity": capability.capacity,
            "consultants": [c.email for c in capability.consultants],
        }
    return response


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
def get_capabilities(db: Session = Depends(get_db)):
    return build_capabilities_response(db)


@app.post("/capabilities/{capability_name}/register")
def register_for_capability(
    capability_name: str,
    email: str,
    db: Session = Depends(get_db),
):
    """Register a consultant for a capability"""
    capability = (
        db.query(Capability)
        .filter(Capability.name == capability_name)
        .first()
    )
    if capability is None:
        raise HTTPException(status_code=404, detail="Capability not found")

    already_registered = (
        db.query(CapabilityConsultant)
        .filter(
            CapabilityConsultant.capability_id == capability.id,
            CapabilityConsultant.email == email,
        )
        .first()
    )
    if already_registered is not None:
        raise HTTPException(
            status_code=400,
            detail="Consultant is already registered for this capability"
        )

    db.add(CapabilityConsultant(capability_id=capability.id, email=email))
    db.commit()
    return {"message": f"Registered {email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
def unregister_from_capability(
    capability_name: str,
    email: str,
    db: Session = Depends(get_db),
):
    """Unregister a consultant from a capability"""
    capability = (
        db.query(Capability)
        .filter(Capability.name == capability_name)
        .first()
    )
    if capability is None:
        raise HTTPException(status_code=404, detail="Capability not found")

    consultant_registration = (
        db.query(CapabilityConsultant)
        .filter(
            CapabilityConsultant.capability_id == capability.id,
            CapabilityConsultant.email == email,
        )
        .first()
    )
    if consultant_registration is None:
        raise HTTPException(
            status_code=400,
            detail="Consultant is not registered for this capability"
        )

    db.delete(consultant_registration)
    db.commit()
    return {"message": f"Unregistered {email} from {capability_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import APIRouter, Depends, HTTPException, status
from models import MessageIn
from sqlalchemy.orm import Session
from db import SessionLocal, Job

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
def create_job(data: MessageIn, db: Session = Depends(get_db)):
    job = Job(
        message=data.message,
        web_search=data.web_search,
        image_gen=data.image_gen,
        deep_research=data.deep_research
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": job.status}

@router.get("/jobs/{job_id}")
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job nicht gefunden")
    return {
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "mode": job.mode,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

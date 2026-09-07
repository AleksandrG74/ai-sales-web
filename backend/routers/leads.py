from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import sys
import os

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, LeadDB
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/leads", tags=["Leads"])

@router.get("/")
async def get_leads(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0)
):
    query = db.query(LeadDB)
    if status:
        query = query.filter(LeadDB.status == status)
    if min_score:
        query = query.filter(LeadDB.intent_score >= min_score)
    total = query.count()
    leads = query.order_by(LeadDB.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "leads": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "username": l.username,
                "message": l.message[:200] + "..." if len(l.message) > 200 else l.message,
                "source": l.source,
                "region": l.region,
                "intent": l.intent,
                "intent_score": l.intent_score,
                "product": l.product,
                "status": l.status,
                "created_at": l.created_at.isoformat() if l.created_at else None
            }
            for l in leads
        ]
    }

@router.get("/status-stats")
async def get_status_stats(db: Session = Depends(get_db)):
    total = db.query(LeadDB).count()
    converted = db.query(LeadDB).filter(LeadDB.status == "converted").count()
    return {"total": total, "converted": converted}

@router.get("/funnel")
async def get_funnel(db: Session = Depends(get_db)):
    stages = ["new", "contacted", "in_progress", "closing", "converted"]
    result = {}
    for stage in stages:
        result[stage] = db.query(LeadDB).filter(LeadDB.status == stage).count()
    return result

@router.put("/{lead_id}/status")
async def update_lead_status(lead_id: int, status: str, db: Session = Depends(get_db)):
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = status
    if status == "contacted":
        lead.contacted_at = datetime.utcnow()
    elif status == "converted":
        lead.converted_at = datetime.utcnow()
    db.commit()
    return {"status": "success"}

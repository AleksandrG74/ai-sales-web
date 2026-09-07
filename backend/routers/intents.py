from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, IntentConfigDB
from models import IntentConfig

router = APIRouter(prefix="/api/intents", tags=["Intents"])

@router.get("/")
async def get_intents_config(db: Session = Depends(get_db)):
    configs = db.query(IntentConfigDB).all()
    result = {}
    for c in configs:
        result[c.intent_type] = json.loads(c.keywords) if c.keywords else []
    return result

@router.post("/")
async def update_intents_config(config: IntentConfig, db: Session = Depends(get_db)):
    intents_map = {
        "buying": config.buying,
        "problem": config.problem,
        "seeking": config.seeking,
        "urgency": config.urgency,
    }
    for intent_type, keywords in intents_map.items():
        existing = db.query(IntentConfigDB).filter(IntentConfigDB.intent_type == intent_type).first()
        if existing:
            existing.keywords = json.dumps(keywords)
        else:
            db.add(IntentConfigDB(intent_type=intent_type, keywords=json.dumps(keywords)))
    db.commit()
    return {"status": "success", "message": "Интенты сохранены"}

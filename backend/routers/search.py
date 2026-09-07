from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

# Добавляем путь к корневой папке проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, LeadDB
from client_search.generator import ClientGenerator

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])

class SearchRequest(BaseModel):
    username: str
    product: str = "холодильник"
    channels: Optional[List[str]] = None

class SearchResponse(BaseModel):
    leads: List[dict]

@router.post("/search")
async def search_clients(request: SearchRequest, db: Session = Depends(get_db)):
    """Поиск клиентов через веб-интерфейс"""
    try:
        # Генерируем тестовых клиентов
        generator = ClientGenerator()
        generator.product = request.product
        generator.count = 5
        generator.run()
        
        # Возвращаем последних клиентов
        leads = db.query(LeadDB).order_by(LeadDB.created_at.desc()).limit(10).all()
        
        return {
            "leads": [
                {
                    "user_id": l.user_id,
                    "username": l.username,
                    "message": l.message[:200],
                    "source": l.source,
                    "intent_score": l.intent_score,
                    "status": l.status
                }
                for l in leads
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

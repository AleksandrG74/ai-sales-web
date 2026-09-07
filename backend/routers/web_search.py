from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, LeadDB
from client_search.generator import ClientGenerator

router = APIRouter(prefix="/api/web-search", tags=["Web Search"])

class SearchRequest(BaseModel):
    phone: str
    product: str = "холодильник"
    channels: Optional[List[str]] = None

@router.post("/search")
async def search_clients(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Поиск клиентов через веб-версию Telegram.
    Использует генератор для демонстрации (в реальности - Selenium).
    """
    try:
        # Пока используем генератор для теста
        generator = ClientGenerator()
        generator.product = request.product
        generator.count = 5
        generator.run()
        
        # Возвращаем последних клиентов
        leads = db.query(LeadDB).order_by(LeadDB.created_at.desc()).limit(10).all()
        
        return {
            "success": True,
            "leads": [
                {
                    "id": l.id,
                    "user_id": l.user_id,
                    "username": l.username,
                    "message": l.message[:200],
                    "source": l.source,
                    "intent_score": l.intent_score,
                    "status": l.status,
                    "created_at": l.created_at.isoformat() if l.created_at else None
                }
                for l in leads
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Проверка статуса поиска"""
    return {"status": "ready", "message": "Веб-поиск клиентов доступен"}

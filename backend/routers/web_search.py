"""
Роутер /api/web-search — поиск через subprocess (для веб-UI).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
import subprocess
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db, LeadDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/web-search", tags=["Web Search"])


class WebSearchRequest(BaseModel):
    phone: Optional[str] = None
    product: str = "холодильник"
    channels: Optional[List[str]] = None
    mode: str = "search"


@router.post("/search")
async def search_clients(request: WebSearchRequest, db: Session = Depends(get_db)):
    """Запуск поиска через subprocess."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script = os.path.join(project_root, "client_search", "main.py")
    
    if not os.path.exists(script):
        raise HTTPException(status_code=500, detail="client_search/main.py не найден")
    
    cmd = [sys.executable, script, "--once", "--mode", request.mode]
    
    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=600)
        
        leads = db.query(LeadDB).order_by(LeadDB.created_at.desc()).limit(20).all()
        
        return {
            "success": True,
            "message": f"Поиск завершён (mode={request.mode})",
            "returncode": result.returncode,
            "leads": [
                {
                    "id": l.id,
                    "user_id": l.user_id,
                    "username": l.username,
                    "message": (l.message or "")[:200],
                    "source": l.source,
                    "intent_score": l.intent_score,
                    "status": l.status,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in leads
            ],
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Превышен лимит (10 мин)")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    return {"status": "ready", "message": "Веб-поиск доступен"}

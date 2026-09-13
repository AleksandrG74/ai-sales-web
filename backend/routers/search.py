"""
Роутер /api/orchestrator/search — запускает client_search через subprocess.
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

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])


class SearchRequest(BaseModel):
    username: Optional[str] = None
    product: str = "холодильник"
    channels: Optional[List[str]] = None
    mode: str = "search"


class SearchResponse(BaseModel):
    status: str
    message: str
    leads_count: int
    leads: List[dict]


@router.post("/search", response_model=SearchResponse)
async def search_clients(request: SearchRequest, db: Session = Depends(get_db)):
    """Запускает client_search/main.py --once --mode <mode> через subprocess."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script = os.path.join(project_root, "client_search", "main.py")
    
    if not os.path.exists(script):
        raise HTTPException(status_code=500, detail=f"client_search/main.py не найден: {script}")
    
    cmd = [sys.executable, script, "--once", "--mode", request.mode]
    logger.info(f"🚀 Запуск client_search: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            logger.error(f"stderr: {result.stderr[-500:]}")
        else:
            logger.info("✅ client_search завершён")
        
        leads = db.query(LeadDB).order_by(LeadDB.created_at.desc()).limit(20).all()
        
        return SearchResponse(
            status="ok",
            message=f"Поиск завершён (mode={request.mode})",
            leads_count=len(leads),
            leads=[
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
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="client_search превысил лимит (10 мин)")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

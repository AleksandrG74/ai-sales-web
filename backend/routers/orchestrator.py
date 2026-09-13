from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import sys
import json
import logging
from datetime import datetime
import requests

# Добавляем путь к папке backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, LeadDB, DialogDB, SettingsDB, ProductConfigDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])

class MessageRequest(BaseModel):
    user_id: str
    message: str
    username: Optional[str] = None
    source: str = "telegram"
    product: Optional[str] = None
    region: Optional[str] = None

class MessageResponse(BaseModel):
    response: str
    strategy_used: str
    tokens_used: Optional[int] = None
    lead_id: Optional[int] = None

class LeadCreateRequest(BaseModel):
    user_id: str
    username: Optional[str] = None
    message: str
    source: str
    region: Optional[str] = None
    intent: str = "seeking"
    intent_score: int = 0
    product: str

@router.get("/health")
async def health_check():
    """Проверка здоровья оркестратора"""
    return {"status": "ok", "service": "Orchestrator", "timestamp": datetime.now().isoformat()}

@router.post("/process_message")
async def process_message(req: MessageRequest, db: Session = Depends(get_db)):
    """Обработка сообщения от клиента"""
    logger.info(f"Processing message from user {req.user_id}")
    
    try:
        # Получаем настройки товара
        product_config = db.query(ProductConfigDB).first()
        product_name = product_config.name if product_config else (req.product or "холодильник")
        
        # Находим или создаем клиента
        lead = db.query(LeadDB).filter(LeadDB.user_id == req.user_id).first()
        if not lead:
            lead = LeadDB(
                user_id=req.user_id,
                username=req.username,
                message=req.message[:500],
                source=req.source,
                region=req.region,
                intent="seeking",
                intent_score=50,
                product=product_name,
                status="new"
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)
            logger.info(f"Created new lead with ID {lead.id}")
        
        # Сохраняем сообщение клиента
        user_dialog = DialogDB(
            lead_id=lead.id,
            sender="user",
            message=req.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_dialog)
        db.commit()
        
        # Генерируем ответ (пока мок-ответ)
        response_text = f"Здравствуйте! Благодарю за ваш интерес к {product_name}. Я вижу, что вы ищете качественный вариант. Давайте подберем идеальный {product_name} для ваших потребностей!"
        
        # Сохраняем ответ бота
        bot_dialog = DialogDB(
            lead_id=lead.id,
            sender="bot",
            message=response_text,
            timestamp=datetime.utcnow(),
            strategy_used="fallback"
        )
        db.add(bot_dialog)
        db.commit()
        
        logger.info(f"Response sent to lead {lead.id}")
        
        return MessageResponse(
            response=response_text,
            strategy_used="fallback",
            tokens_used=0,
            lead_id=lead.id
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create_lead")
async def create_lead(req: LeadCreateRequest, db: Session = Depends(get_db)):
    """Создание нового лида"""
    logger.info(f"Creating lead for user {req.user_id}")
    
    try:
        existing = db.query(LeadDB).filter(LeadDB.user_id == req.user_id).first()
        if existing:
            return {"status": "exists", "lead_id": existing.id}
        
        lead = LeadDB(
            user_id=req.user_id,
            username=req.username,
            message=req.message,
            source=req.source,
            region=req.region,
            intent=req.intent,
            intent_score=req.intent_score,
            product=req.product,
            status="new"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        logger.info(f"Created lead with ID {lead.id}")
        return {"status": "success", "lead_id": lead.id}
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_clients(request: dict, db: Session = Depends(get_db)):
    """Поиск клиентов через subprocess client_search/main.py."""
    import subprocess
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script = os.path.join(project_root, "client_search", "main.py")
    mode = request.get("mode", "search")

    if not os.path.exists(script):
        raise HTTPException(status_code=500, detail=f"client_search/main.py не найден: {script}")

    cmd = [sys.executable, script, "--once", "--mode", mode]
    logger.info(f"🚀 Запуск client_search: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            logger.error(f"stderr: {result.stderr[-500:]}")

        leads = db.query(LeadDB).order_by(LeadDB.created_at.desc()).limit(20).all()

        return {
            "status": "ok",
            "message": f"Поиск завершён (mode={mode})",
            "leads": [
                {
                    "user_id": l.user_id,
                    "username": l.username,
                    "message": (l.message or "")[:200],
                    "source": l.source,
                    "intent_score": l.intent_score,
                    "status": l.status,
                }
                for l in leads
            ],
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="client_search превысил лимит (10 мин)")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

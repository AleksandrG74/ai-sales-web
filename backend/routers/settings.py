from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
import json
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class ProactiveSettings(BaseModel):
    enabled: bool = True
    min_intent_score: int = 40
    max_messages_per_day: int = 10
    cooldown_minutes: int = 60
    greeting_template: str = "Здравствуйте! Я заметил, что вы интересуетесь {product}. Чем могу помочь?"
    timezone: str = "Europe/Moscow"
    working_hours_start: str = "09:00"
    working_hours_end: str = "21:00"

class AISettings(BaseModel):
    system_prompt_visual: str
    system_prompt_audial: str
    system_prompt_logical: str
    system_prompt_kinesthetic: str
    fallback_prompt: str
    temperature: float = 0.7
    max_tokens: int = 500

# Хранилище настроек
settings_db = {
    "proactive": {
        "enabled": True,
        "min_intent_score": 40,
        "max_messages_per_day": 10,
        "cooldown_minutes": 60,
        "greeting_template": "Здравствуйте! Я заметил, что вы интересуетесь {product}. Чем могу помочь?",
        "timezone": "Europe/Moscow",
        "working_hours_start": "09:00",
        "working_hours_end": "21:00"
    },
    "ai": {
        "system_prompt_visual": "Ты — продавец-консультант. Клиент — визуал. Используй яркие образы, цвета, формы, визуальные метафоры. Говори о том, как товар выглядит в интерьере. Избегай сухих цифр. Будь эмоциональным, но не перегружай деталями. Цель — вызвать желание обладать товаром.",
        "system_prompt_audial": "Ты — продавец-консультант. Клиент — аудиал. Используй звуковые метафоры, интонации, ритм. Говори о том, как звучит товар или его название. Используй ритмичные фразы. Цель — создать приятное звуковое впечатление от товара.",
        "system_prompt_logical": "Ты — продавец-консультант. Клиент — логик. Используй цифры, факты, логические цепочки. Давай четкие аргументы и сравнения. Структурируй информацию. Цель — показать рациональные преимущества товара.",
        "system_prompt_kinesthetic": "Ты — продавец-консультант. Клиент — кинестетик. Используй тактильные описания, ощущения, движение. Говори о том, как товар ощущается в руках. Используй слова: 'чувствовать', 'касаться', 'двигаться'. Цель — дать почувствовать товар через текст.",
        "fallback_prompt": "Ты — продавец-консультант. Общайся вежливо и профессионально. Помоги клиенту с выбором товара.",
        "temperature": 0.7,
        "max_tokens": 500
    },
    "blacklist": []
}

@router.get("/ai")
async def get_ai_settings():
    return settings_db["ai"]

@router.post("/ai")
async def update_ai_settings(settings: AISettings):
    settings_db["ai"] = {
        "system_prompt_visual": settings.system_prompt_visual,
        "system_prompt_audial": settings.system_prompt_audial,
        "system_prompt_logical": settings.system_prompt_logical,
        "system_prompt_kinesthetic": settings.system_prompt_kinesthetic,
        "fallback_prompt": settings.fallback_prompt,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens
    }
    return {"status": "success", "settings": settings_db["ai"]}

@router.get("/proactive")
async def get_proactive_settings():
    return settings_db["proactive"]

@router.post("/proactive")
async def update_proactive_settings(settings: ProactiveSettings):
    settings_db["proactive"] = {
        "enabled": settings.enabled,
        "min_intent_score": settings.min_intent_score,
        "max_messages_per_day": settings.max_messages_per_day,
        "cooldown_minutes": settings.cooldown_minutes,
        "greeting_template": settings.greeting_template,
        "timezone": settings.timezone,
        "working_hours_start": settings.working_hours_start,
        "working_hours_end": settings.working_hours_end
    }
    return {"status": "success"}

@router.get("/blacklist")
async def get_blacklist():
    return {"blacklist": settings_db["blacklist"]}

@router.post("/blacklist")
async def add_to_blacklist(user_id: str):
    if user_id not in settings_db["blacklist"]:
        settings_db["blacklist"].append(user_id)
    return {"status": "success"}

@router.delete("/blacklist/{user_id}")
async def remove_from_blacklist(user_id: str):
    if user_id in settings_db["blacklist"]:
        settings_db["blacklist"].remove(user_id)
    return {"status": "success"}

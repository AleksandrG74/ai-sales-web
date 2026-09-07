# backend/models.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductConfig(BaseModel):
    name: str
    category: str
    attributes: List[str]
    keywords: List[str]
    industries: List[str]
    regions: List[str]

class IntentConfig(BaseModel):
    buying: List[str]
    problem: List[str]
    seeking: List[str]
    urgency: List[str]

class Lead(BaseModel):
    id: int
    user_id: str
    username: Optional[str]
    message: str
    source: str
    region: Optional[str]
    intent: str
    intent_score: int
    product: str
    status: str
    created_at: datetime

class ModuleStatus(BaseModel):
    name: str
    running: bool
    pid: Optional[int]
    last_activity: Optional[datetime]

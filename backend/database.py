from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import json

Base = declarative_base()

class LeadDB(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    username = Column(String(100), nullable=True)
    message = Column(Text)
    source = Column(String(50))
    region = Column(String(50), nullable=True)
    intent = Column(String(50))
    intent_score = Column(Integer, default=0)
    product = Column(String(100))
    status = Column(String(20), default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    contacted_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)
    profile_json = Column(Text, nullable=True)
    
    dialogs = relationship("DialogDB", back_populates="lead", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_source', 'user_id', 'source'),
        Index('idx_status_score', 'status', 'intent_score'),
    )

class DialogDB(Base):
    __tablename__ = "dialogs"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    sender = Column(String(10))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    strategy_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    
    lead = relationship("LeadDB", back_populates="dialogs")

class ProductConfigDB(Base):
    __tablename__ = "product_config"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    attributes = Column(Text)
    keywords = Column(Text)
    industries = Column(Text)
    regions = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

class IntentConfigDB(Base):
    __tablename__ = "intent_config"
    
    id = Column(Integer, primary_key=True, index=True)
    intent_type = Column(String(50), unique=True)
    keywords = Column(Text)

class SettingsDB(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SourceDB(Base):
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50))
    name = Column(String(100))
    enabled = Column(Boolean, default=True)
    last_scan = Column(DateTime, nullable=True)

class GoalDB(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    trigger_type = Column(String(50))
    trigger_value = Column(String(200))
    success_indicators = Column(Text)
    priority = Column(Integer, default=1)

# Создание движка и сессии
engine = None
SessionLocal = None

def get_db():
    """Получить сессию БД"""
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(db_path=None):
    """Инициализация БД"""
    global engine, SessionLocal
    
    if db_path is None:
        db_path = "backend/data/database.db"
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    
    # Инициализируем настройки по умолчанию
    db = SessionLocal()
    try:
        if not db.query(SettingsDB).filter(SettingsDB.key == "ai_settings").first():
            default_ai_settings = {
                "system_prompt_visual": "Ты — продавец-консультант. Клиент — визуал. Используй яркие образы, цвета, формы, визуальные метафоры.",
                "system_prompt_audial": "Ты — продавец-консультант. Клиент — аудиал. Используй звуковые метафоры, интонации, ритм.",
                "system_prompt_logical": "Ты — продавец-консультант. Клиент — логик. Используй цифры, факты, логические цепочки.",
                "system_prompt_kinesthetic": "Ты — продавец-консультант. Клиент — кинестетик. Используй тактильные описания, ощущения.",
                "fallback_prompt": "Ты — продавец-консультант. Общайся вежливо и профессионально.",
                "temperature": 0.7,
                "max_tokens": 500
            }
            db.add(SettingsDB(key="ai_settings", value=json.dumps(default_ai_settings)))
        
        if not db.query(SettingsDB).filter(SettingsDB.key == "proactive_settings").first():
            default_proactive = {
                "enabled": True,
                "min_intent_score": 40,
                "max_messages_per_day": 10,
                "cooldown_minutes": 60,
                "greeting_template": "Здравствуйте! Я заметил, что вы интересуетесь {product}. Чем могу помочь?",
                "timezone": "Europe/Moscow",
                "working_hours_start": "09:00",
                "working_hours_end": "21:00"
            }
            db.add(SettingsDB(key="proactive_settings", value=json.dumps(default_proactive)))
            
        if not db.query(SettingsDB).filter(SettingsDB.key == "blacklist").first():
            db.add(SettingsDB(key="blacklist", value=json.dumps([])))
            
        db.commit()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации БД: {e}")
    finally:
        db.close()
    
    return SessionLocal

def get_db_session():
    if SessionLocal is None:
        init_db()
    return SessionLocal()

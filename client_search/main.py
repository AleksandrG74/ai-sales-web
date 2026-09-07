#!/usr/bin/env python
"""
Модуль поиска клиентов в Telegram
Использует Telethon для сканирования чатов и каналов
"""
import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import argparse

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_db, LeadDB, ProductConfigDB
from sqlalchemy.orm import Session

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramSearcher:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_id = self.config.get('api_id')
        self.api_hash = self.config.get('api_hash')
        self.phone = self.config.get('phone')
        self.channels = self.config.get('channels', [])
        self.keywords = self.config.get('keywords', [])
        self.product = self.config.get('product', 'холодильник')
        self.threshold = self.config.get('intent_threshold', 40)
        self.scan_limit = self.config.get('scan_limit', 50)
        self.client = None
        self.db_session = None

    async def connect(self):
        """Подключение к Telegram"""
        session_path = os.path.join(os.path.dirname(__file__), '..', 'sessions', 'telegram_session')
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        
        try:
            await self.client.start(phone=self.phone)
            logger.info("✅ Подключен к Telegram API")
            
            # Проверяем авторизацию
            me = await self.client.get_me()
            logger.info(f"👤 Авторизован как: {me.first_name} (@{me.username})")
            return True
            
        except SessionPasswordNeededError:
            logger.error("❌ Требуется двухфакторная аутентификация")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {str(e)}")
            return False

    async def scan_channel(self, channel_name):
        """Сканирование одного канала или чата"""
        try:
            # Получаем сущность канала
            entity = await self.client.get_entity(channel_name)
            logger.info(f"📡 Сканируем: {channel_name}")
            
            # Получаем сообщения
            messages = await self.client.get_messages(entity, limit=self.scan_limit)
            leads_found = 0
            
            for msg in messages:
                if not msg.text:
                    continue
                
                # Проверяем наличие ключевых слов
                score = self.calculate_intent(msg.text)
                if score >= self.threshold:
                    await self.save_lead(msg, channel_name, score)
                    leads_found += 1
            
            logger.info(f"✅ Найдено {leads_found} потенциальных клиентов в {channel_name}")
            return leads_found
            
        except Exception as e:
            logger.error(f"❌ Ошибка сканирования {channel_name}: {str(e)}")
            return 0

    def calculate_intent(self, text):
        """Вычисление индекса готовности (Intent Score)"""
        text_lower = text.lower()
        score = 0
        
        # 1. Проверяем ключевые слова (до 40 баллов)
        matched_keywords = 0
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                matched_keywords += 1
                if matched_keywords >= 4:
                    score += 40
                    break
                score += 10
        
        # 2. Интенты покупки (до 30 баллов)
        buying_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен', 'ищу', 'выбрать']
        for word in buying_words:
            if word in text_lower:
                score += 5
                if score >= 30:
                    break
        
        # 3. Срочность (до 15 баллов)
        urgency_words = ['срочно', 'сегодня', 'завтра', 'быстро', 'горящий', 'скидка']
        for word in urgency_words:
            if word in text_lower:
                score += 3
                if score >= 15:
                    break
        
        # 4. Вопросы (до 15 баллов)
        question_words = ['как', 'что', 'где', 'сколько', 'какой', 'почему', 'когда']
        for word in question_words:
            if word in text_lower and '?' in text:
                score += 3
                if score >= 15:
                    break
        
        return min(score, 100)

    async def save_lead(self, msg, source, score):
        """Сохранение найденного клиента в БД"""
        db = next(get_db())
        
        try:
            # Получаем username
            username = None
            if msg.sender:
                username = msg.sender.username or msg.sender.first_name
            elif msg.from_id:
                username = str(msg.from_id)
            
            # Проверяем, существует ли уже клиент
            existing = db.query(LeadDB).filter(
                LeadDB.user_id == str(msg.sender_id)
            ).first()
            
            if existing:
                # Обновляем если нужно
                if existing.intent_score < score:
                    existing.intent_score = score
                    existing.message = msg.text[:500]
                    db.commit()
                    logger.debug(f"🔄 Обновлён клиент {msg.sender_id} (score: {score})")
                return
            
            # Создаём нового клиента
            lead = LeadDB(
                user_id=str(msg.sender_id),
                username=username,
                message=msg.text[:500],
                source=f"telegram_{source}",
                intent="seeking",
                intent_score=score,
                product=self.product,
                status="new"
            )
            db.add(lead)
            db.commit()
            logger.info(f"💾 Сохранён клиент {msg.sender_id} (score: {score})")
            logger.debug(f"   Сообщение: {msg.text[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def run(self):
        """Запуск сканирования"""
        if not await self.connect():
            logger.error("❌ Не удалось подключиться к Telegram")
            return
        
        total_found = 0
        for channel in self.channels:
            found = await self.scan_channel(channel)
            total_found += found
        
        logger.info("=" * 50)
        logger.info(f"📊 Всего найдено клиентов: {total_found}")
        logger.info("=" * 50)
        
        await self.client.disconnect()
        logger.info("🔌 Отключен от Telegram")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/telegram_config.json',
                       help='Путь к конфигурационному файлу')
    parser.add_argument('--once', action='store_true',
                       help='Запустить один раз и завершить')
    args = parser.parse_args()
    
    # Инициализируем БД
    init_db()
    
    searcher = TelegramSearcher(args.config)
    
    if args.once:
        asyncio.run(searcher.run())
    else:
        # Запускаем в цикле (каждый час)
        import time
        while True:
            asyncio.run(searcher.run())
            logger.info("⏳ Ожидание 1 час до следующего сканирования...")
            time.sleep(3600)

if __name__ == "__main__":
    main()

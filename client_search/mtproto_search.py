#!/usr/bin/env python
"""
Поиск клиентов через MTProto прокси (локальный tg-ws-proxy)
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_db, LeadDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MTProtoSearcher:
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
        self.scan_limit = self.config.get('scan_limit', 20)
        self.client = None

    async def connect(self):
        """Подключение к Telegram через локальный MTProto прокси"""
        session_path = os.path.join(os.path.dirname(__file__), '..', 'sessions', 'telegram_session')
        
        try:
            # Используем локальный MTProto прокси
            # tg-ws-proxy слушает на 127.0.0.1:1443
            self.client = TelegramClient(
                session_path,
                self.api_id,
                self.api_hash
            )
            
            # Подключаемся с явным указанием прокси
            await self.client.start(
                phone=self.phone,
                proxy=('mtproto', '127.0.0.1', 1443, '14a68dd409b093983b6aa9ce9f79c9a5')
            )
            
            me = await self.client.get_me()
            logger.info(f"✅ Подключен к Telegram через MTProto прокси")
            logger.info(f"👤 Авторизован как: {me.first_name} (@{me.username})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {str(e)}")
            return False

    async def scan_channel(self, channel_name):
        try:
            entity = await self.client.get_entity(channel_name)
            logger.info(f"📡 Сканируем: {channel_name}")
            
            messages = await self.client.get_messages(entity, limit=self.scan_limit)
            leads_found = 0
            
            for msg in messages:
                if not msg.text:
                    continue
                    
                score = self.calculate_intent(msg.text)
                if score >= self.threshold:
                    await self.save_lead(msg, channel_name, score)
                    leads_found += 1
            
            logger.info(f"✅ Найдено {leads_found} клиентов в {channel_name}")
            return leads_found
            
        except Exception as e:
            logger.error(f"❌ Ошибка {channel_name}: {str(e)}")
            return 0

    def calculate_intent(self, text):
        text_lower = text.lower()
        score = 0
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                score += 15
        
        buying_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен', 'ищу']
        for word in buying_words:
            if word in text_lower:
                score += 10
        
        return min(score, 100)

    async def save_lead(self, msg, source, score):
        db = next(get_db())
        try:
            existing = db.query(LeadDB).filter(
                LeadDB.user_id == str(msg.sender_id)
            ).first()
            
            if existing:
                return
            
            lead = LeadDB(
                user_id=str(msg.sender_id),
                username=msg.sender.username if msg.sender else None,
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
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def run(self):
        if not await self.connect():
            return
        
        total_found = 0
        for channel in self.channels:
            found = await self.scan_channel(channel)
            total_found += found
        
        logger.info("=" * 50)
        logger.info(f"📊 Всего найдено: {total_found}")
        logger.info("=" * 50)
        
        await self.client.disconnect()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/telegram_config.json')
    args = parser.parse_args()
    
    init_db()
    searcher = MTProtoSearcher(args.config)
    asyncio.run(searcher.run())

if __name__ == "__main__":
    main()

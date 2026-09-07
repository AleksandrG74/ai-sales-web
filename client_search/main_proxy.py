#!/usr/bin/env python
"""
Модуль поиска клиентов в Telegram с поддержкой прокси
"""
import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.network import ConnectionTcpAbridged
import argparse

# Импорты для прокси
from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy
import ssl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_db, LeadDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramSearcherProxy:
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
        self.scan_limit = self.config.get('scan_limit', 30)
        self.proxy_config = self.config.get('proxy', None)
        self.client = None

    async def create_proxy_connection(self):
        """Создание подключения через прокси"""
        if not self.proxy_config:
            return None
            
        try:
            proxy_type = self.proxy_config.get('type', 'socks5')
            proxy_addr = self.proxy_config.get('addr', '127.0.0.1')
            proxy_port = self.proxy_config.get('port', 1080)
            proxy_username = self.proxy_config.get('username', '')
            proxy_password = self.proxy_config.get('password', '')
            
            logger.info(f"🔒 Настройка прокси: {proxy_type}://{proxy_addr}:{proxy_port}")
            
            # Создаём прокси объект
            if proxy_type.upper() == 'SOCKS5':
                proxy = Proxy(
                    proxy_type=ProxyType.SOCKS5,
                    host=proxy_addr,
                    port=proxy_port,
                    username=proxy_username or None,
                    password=proxy_password or None
                )
            elif proxy_type.upper() == 'SOCKS4':
                proxy = Proxy(
                    proxy_type=ProxyType.SOCKS4,
                    host=proxy_addr,
                    port=proxy_port,
                    username=proxy_username or None
                )
            elif proxy_type.upper() == 'HTTP':
                proxy = Proxy(
                    proxy_type=ProxyType.HTTP,
                    host=proxy_addr,
                    port=proxy_port,
                    username=proxy_username or None,
                    password=proxy_password or None
                )
            else:
                logger.error(f"❌ Неподдерживаемый тип прокси: {proxy_type}")
                return None
            
            # Создаём кастомный connector для Telethon
            async def custom_connector(ip, port, **kwargs):
                """Подключение через прокси"""
                try:
                    # Подключаемся через прокси
                    sock = await proxy.connect(
                        dest_host=ip,
                        dest_port=port,
                        timeout=15
                    )
                    
                    # Возвращаем reader/writer
                    return await asyncio.open_connection(
                        host=None,
                        port=None,
                        sock=sock,
                        ssl=ssl.create_default_context() if port == 443 else None,
                        server_hostname=ip if port == 443 else None
                    )
                except Exception as e:
                    logger.error(f"❌ Ошибка подключения через прокси: {str(e)}")
                    raise
            
            return custom_connector
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания прокси: {str(e)}")
            return None

    async def connect(self):
        """Подключение к Telegram через прокси"""
        session_path = os.path.join(os.path.dirname(__file__), '..', 'sessions', 'telegram_session')
        
        try:
            # Создаём прокси-коннектор
            connector = await self.create_proxy_connection()
            
            if connector:
                logger.info("🔒 Подключение через прокси")
                self.client = TelegramClient(
                    session_path,
                    self.api_id,
                    self.api_hash,
                    connection=ConnectionTcpAbridged,
                    connector=connector,
                    connection_retries=3,
                    retry_delay=2
                )
            else:
                logger.info("ℹ️ Прямое подключение (без прокси)")
                self.client = TelegramClient(
                    session_path,
                    self.api_id,
                    self.api_hash,
                    connection=ConnectionTcpAbridged,
                    connection_retries=3,
                    retry_delay=2
                )

            # Подключаемся
            await asyncio.wait_for(
                self.client.start(phone=self.phone),
                timeout=30
            )

            me = await self.client.get_me()
            logger.info(f"✅ Подключен к Telegram")
            logger.info(f"👤 Авторизован как: {me.first_name} (@{me.username})")
            return True

        except asyncio.TimeoutError:
            logger.error("⏰ Таймаут подключения")
            return False
        except SessionPasswordNeededError:
            logger.error("❌ Требуется двухфакторная аутентификация")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {str(e)}")
            return False

    async def scan_channel(self, channel_name):
        """Сканирование канала"""
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
        """Расчёт Intent Score"""
        text_lower = text.lower()
        score = 0
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                score += 15
        
        buying_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен', 'ищу']
        for word in buying_words:
            if word in text_lower:
                score += 10
        
        urgency_words = ['срочно', 'сегодня', 'завтра', 'быстро']
        for word in urgency_words:
            if word in text_lower:
                score += 5
        
        return min(score, 100)

    async def save_lead(self, msg, source, score):
        """Сохранение клиента в БД"""
        db = next(get_db())
        try:
            existing = db.query(LeadDB).filter(
                LeadDB.user_id == str(msg.sender_id)
            ).first()
            
            if existing:
                if existing.intent_score < score:
                    existing.intent_score = score
                    existing.message = msg.text[:500]
                    db.commit()
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
        """Запуск сканирования"""
        if not await self.connect():
            logger.error("❌ Не удалось подключиться")
            return
        
        total_found = 0
        for channel in self.channels:
            found = await self.scan_channel(channel)
            total_found += found
        
        logger.info("=" * 50)
        logger.info(f"📊 Всего найдено: {total_found}")
        logger.info("=" * 50)
        
        await self.client.disconnect()
        logger.info("🔌 Отключен от Telegram")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='configs/telegram_config.json')
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    
    init_db()
    searcher = TelegramSearcherProxy(args.config)
    
    if args.once:
        asyncio.run(searcher.run())
    else:
        import time
        while True:
            asyncio.run(searcher.run())
            logger.info("⏳ Ожидание 1 часа...")
            time.sleep(3600)

if __name__ == "__main__":
    main()

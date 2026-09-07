#!/usr/bin/env python
"""
Тестовый скрипт для работы с MTProto прокси
"""
import asyncio
import os
import sys
from telethon import TelegramClient

# Наши данные
api_id = 35611241
api_hash = "dd41c4667ac94a6d7b62b6f4b922ba84"
phone = "+79195260274"

# Прокси (MTProto)
proxy = ("mtproto", "127.0.0.1", 1443, "14a68dd409b093983b6aa9ce9f79c9a5")

async def main():
    try:
        print("🔒 Подключение к Telegram через MTProto прокси...")
        print(f"   Прокси: 127.0.0.1:1443")
        print(f"   Секрет: 14a68dd409b093983b6aa9ce9f79c9a5")
        
        client = TelegramClient(
            "sessions/test_session",
            api_id,
            api_hash,
            proxy=proxy
        )
        
        await client.start(phone=phone)
        
        me = await client.get_me()
        print(f"\n✅ Успешно! Авторизован как:")
        print(f"   Имя: {me.first_name}")
        print(f"   Username: @{me.username}")
        
        print("\n📡 Проверяем каналы...")
        channels = ["t.me/ru2ch", "t.me/overhear"]
        for channel in channels:
            try:
                entity = await client.get_entity(channel)
                print(f"   ✅ Найден канал: {channel}")
            except Exception as e:
                print(f"   ❌ Не удалось найти {channel}: {e}")
        
        await client.disconnect()
        print("\n✅ Тест завершён")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

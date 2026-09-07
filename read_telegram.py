#!/usr/bin/env python
"""
Простая консольная программа для чтения сообщений из Telegram
Использует Telethon (клиентский API)
"""

import asyncio
import os
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from datetime import datetime

# Конфигурация
API_ID = 35611241
API_HASH = "dd41c4667ac94a6d7b62b6f4b922ba84"
PHONE = "+79195260274"

# Настройка прокси (если нужно)
# Прокси: MTProto через tg-ws-proxy (порт 1443)
PROXY = ("mtproto", "127.0.0.1", 1443, "14a68dd409b093983b6aa9ce9f79c9a5")
USE_PROXY = True  # False - если не используем прокси

async def main():
    print("=" * 50)
    print("📱 Telegram Reader (простая консольная программа)")
    print("=" * 50)
    
    # Создаём клиент
    session_file = "sessions/telegram_reader"
    os.makedirs("sessions", exist_ok=True)
    
    if USE_PROXY:
        print(f"🔒 Используется прокси: MTProto 127.0.0.1:1443")
        client = TelegramClient(session_file, API_ID, API_HASH, proxy=PROXY)
    else:
        print(f"ℹ️ Прямое подключение (без прокси)")
        client = TelegramClient(session_file, API_ID, API_HASH)
    
    try:
        # Подключаемся
        print("⏳ Подключение к Telegram...")
        await client.start(phone=PHONE)
        print("✅ Подключено успешно!")
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"\n👤 Авторизован как: {me.first_name} (@{me.username})")
        
        # Получаем список диалогов (чатов)
        print("\n📋 Получаем список диалогов...")
        dialogs = await client.get_dialogs()
        
        print(f"\n📊 Всего диалогов: {len(dialogs)}")
        print("\n📋 Последние 10 диалогов:")
        print("-" * 60)
        
        for i, dialog in enumerate(dialogs[:10], 1):
            name = dialog.name or "Без названия"
            unread = dialog.unread_count
            print(f"{i:2}. {name[:30]:30} | Непрочитанных: {unread}")
        
        # Выбор диалога для чтения
        print("\n" + "=" * 50)
        print("📖 Чтение сообщений из диалога")
        print("=" * 50)
        
        # Берём первый диалог (самый активный)
        if dialogs:
            target = dialogs[0]
            print(f"\n📌 Выбран диалог: {target.name}")
            print(f"   ID: {target.id}")
            print(f"   Непрочитанных: {target.unread_count}")
            
            # Получаем сообщения
            print("\n⏳ Загрузка последних 20 сообщений...")
            messages = await client.get_messages(target.entity, limit=20)
            
            print(f"\n📨 Последние {len(messages)} сообщений:")
            print("-" * 60)
            
            for i, msg in enumerate(messages, 1):
                sender = msg.sender_id
                date = msg.date.strftime("%d.%m.%Y %H:%M")
                text = msg.text[:100] if msg.text else "[Медиа]"
                
                print(f"{i:2}. [{date}] {sender}: {text}")
                if msg.text and len(msg.text) > 100:
                    print(f"      ... ({len(msg.text)} символов)")
            
        # Поиск по ключевому слову
        print("\n" + "=" * 50)
        print("🔍 Поиск сообщений по ключевому слову")
        print("=" * 50)
        
        search_word = "холодильник"
        print(f"\n🔎 Ищем сообщения с ключевым словом: '{search_word}'")
        
        found = []
        for dialog in dialogs[:5]:
            try:
                messages = await client.get_messages(dialog.entity, limit=50)
                for msg in messages:
                    if msg.text and search_word.lower() in msg.text.lower():
                        found.append({
                            'chat': dialog.name,
                            'date': msg.date.strftime("%d.%m %H:%M"),
                            'text': msg.text[:200],
                            'sender': msg.sender_id
                        })
            except:
                continue
        
        if found:
            print(f"\n✅ Найдено {len(found)} сообщений с '{search_word}':")
            print("-" * 60)
            for i, item in enumerate(found[:10], 1):
                print(f"{i:2}. [{item['chat']}] {item['date']}: {item['text']}")
        else:
            print(f"\n❌ Сообщений с '{search_word}' не найдено")
        
        # Статистика
        print("\n" + "=" * 50)
        print("📊 Статистика диалогов")
        print("=" * 50)
        
        for dialog in dialogs[:5]:
            messages = await client.get_messages(dialog.entity, limit=1)
            last_msg = messages[0].date if messages else "Нет сообщений"
            print(f"📌 {dialog.name[:25]:25} | Последнее: {last_msg.strftime('%d.%m.%Y %H:%M') if messages else 'Нет'}")
        
        print("\n" + "=" * 50)
        print("✅ Программа завершена")
        print("=" * 50)
        
        await client.disconnect()
        
    except SessionPasswordNeededError:
        print("❌ Требуется двухфакторная аутентификация")
        print("   Введите пароль в коде или используйте другой метод")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python
"""
Финальная консольная программа для чтения сообщений из Telegram
Использует SOCKS5 прокси (3proxy)
"""

import asyncio
import os
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, RPCError
import socks

# Данные для входа
API_ID = 35611241
API_HASH = "dd41c4667ac94a6d7b62b6f4b922ba84"
PHONE = "+79195260274"

# Настройка прокси (SOCKS5 через 3proxy)
PROXY = (socks.SOCKS5, "127.0.0.1", 1080)

async def main():
    print("=" * 60)
    print("📱 Консольный клиент Telegram для чтения сообщений")
    print("=" * 60)

    # Создаем папку для сессий
    os.makedirs("sessions", exist_ok=True)
    session_file = "sessions/telegram_reader"

    # Проверяем, запущен ли прокси
    print("\n🔍 Проверка прокси-сервера...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(("127.0.0.1", 1080))
        sock.close()
        print("✅ Прокси-сервер на 127.0.0.1:1080 доступен")
    except Exception:
        print("❌ Прокси-сервер на 127.0.0.1:1080 не отвечает!")
        print("   Запустите 3proxy в отдельном окне:")
        print("   cd /c/Users/52602/ai-sales-web/3proxy")
        print("   ./3proxy.exe 3proxy.cfg")
        print("\n⚠️ Если прокси не работает, программа будет подключаться напрямую.")

    # Создаем клиент
    try:
        print("⏳ Подключение к Telegram через прокси...")
        client = TelegramClient(session_file, API_ID, API_HASH, proxy=PROXY)
        
        # Пытаемся подключиться
        await client.start(phone=PHONE)
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"\n✅ Подключено! Аккаунт: {me.first_name} (@{me.username})")
        
        # Получаем список диалогов
        print("\n📋 Получение списка диалогов...")
        dialogs = await client.get_dialogs()
        print(f"📊 Всего диалогов: {len(dialogs)}")

        # Выводим первые диалоги
        print("\n📌 Ваши последние 5 диалогов:")
        for i, dialog in enumerate(dialogs[:5], 1):
            unread = f"(Не прочитано: {dialog.unread_count})" if dialog.unread_count else ""
            print(f"  {i}. {dialog.name} {unread}")

        # Выбираем диалог для чтения
        print("\n🔢 Введите номер диалога для чтения (или Enter для первого):")
        choice = input().strip()
        
        if choice and choice.isdigit() and 1 <= int(choice) <= len(dialogs):
            target_dialog = dialogs[int(choice) - 1]
        else:
            target_dialog = dialogs[0]
        
        print(f"\n📖 Чтение сообщений из диалога: '{target_dialog.name}'")
        
        # Получаем сообщения
        messages = await client.get_messages(target_dialog.entity, limit=20)
        
        if messages:
            print(f"\n📨 Последние {len(messages)} сообщений:")
            print("-" * 80)
            for i, msg in enumerate(messages, 1):
                date = msg.date.strftime("%H:%M")
                sender = msg.sender_id or "Неизвестно"
                text = msg.text[:100] if msg.text else "[Медиа или пересланное сообщение]"
                print(f"{i:2}. [{date}] {text}")
        else:
            print("\n📭 В этом диалоге нет сообщений.")

        # Поиск по ключевому слову (опционально)
        print("\n🔍 Введите ключевое слово для поиска (или Enter для пропуска):")
        search_word = input().strip()
        
        if search_word:
            print(f"\n🔎 Поиск сообщений по слову '{search_word}'...")
            found = []
            for dialog in dialogs[:10]:
                try:
                    msgs = await client.get_messages(dialog.entity, limit=30)
                    for msg in msgs:
                        if msg.text and search_word.lower() in msg.text.lower():
                            found.append({
                                'chat': dialog.name,
                                'text': msg.text[:200]
                            })
                except:
                    continue
            
            if found:
                print(f"\n✅ Найдено {len(found)} сообщений с '{search_word}':")
                for i, item in enumerate(found[:10], 1):
                    print(f"  {i}. [{item['chat']}] {item['text']}")
            else:
                print(f"❌ Сообщений с '{search_word}' не найдено.")

        await client.disconnect()
        print("\n✅ Работа завершена.")

    except SessionPasswordNeededError:
        print("❌ Требуется двухфакторная аутентификация.")
    except RPCError as e:
        print(f"❌ Ошибка Telegram API: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())

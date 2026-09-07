import asyncio
from telethon import TelegramClient
import socks
import logging

# Включаем логирование для отладки
logging.basicConfig(level=logging.INFO)

# Ваши данные
API_ID = 35611241
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'
PHONE = '+79195260274'

# Прокси данные (из вашего скриншота)
PROXY_HOST = '186.65.114.69'
PROXY_PORT = 9039
PROXY_USER = 'OMc5Ew'
PROXY_PASS = 'DVogDX'

# Создаём прокси для Telethon
# Telethon принимает прокси в формате (тип, хост, порт, логин, пароль)
PROXY = (socks.SOCKS5, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

print("=" * 60)
print("📱 Telegram Консольный клиент (с прокси)")
print("=" * 60)

# Создаём клиент с прокси
client = TelegramClient('my_session_proxy', API_ID, API_HASH, proxy=PROXY)

async def main():
    try:
        print("⏳ Подключение к Telegram через прокси...")
        print(f"🔒 Прокси: {PROXY_HOST}:{PROXY_PORT}")
        
        await client.start(phone=PHONE)
        
        me = await client.get_me()
        print(f"✅ Успешное подключение!")
        print(f"👤 Аккаунт: {me.first_name} (@{me.username})")
        
        print("\n📋 Список ваших каналов и диалогов:")
        print("-" * 60)
        
        dialogs = []
        async for dialog in client.iter_dialogs(limit=30):
            dialogs.append(dialog)
            print(f"   ID: {dialog.id:15} | Название: {dialog.name[:40]}")
        
        print("-" * 60)
        print(f"📊 Всего диалогов: {len(dialogs)}")
        
        print("\n" + "=" * 60)
        print("📖 ЧТЕНИЕ СООБЩЕНИЙ")
        print("=" * 60)
        
        target_id_str = input("Введите ID канала для чтения сообщений: ").strip()
        
        if not target_id_str:
            print("❌ ID не введён")
            return
        
        try:
            target_id = int(target_id_str)
            print(f"\n📖 Чтение сообщений из канала ID: {target_id}")
            print("-" * 60)
            
            messages = []
            async for message in client.iter_messages(target_id, limit=15):
                messages.append(message)
            
            if not messages:
                print("📭 Сообщений нет")
                return
            
            for i, message in enumerate(messages, 1):
                try:
                    sender = await message.get_sender()
                    sender_name = getattr(sender, 'title', None) or getattr(sender, 'username', None) or "Unknown"
                    date_str = message.date.strftime('%Y-%m-%d %H:%M:%S')
                    text = message.text if message.text else "[Медиа]"
                    
                    print(f"\n{i}. [{date_str}] {sender_name}:")
                    print(f"   {text[:300]}")
                    if len(text) > 300:
                        print(f"   ... (ещё {len(text)-300} символов)")
                    print("-" * 50)
                except Exception as e:
                    print(f"⚠️ Ошибка при чтении сообщения: {e}")
            
            print(f"\n✅ Прочитано сообщений: {len(messages)}")
            
        except ValueError:
            print("❌ Ошибка: введите число")
        except Exception as e:
            print(f"❌ Ошибка при чтении: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Работа завершена")
        print("=" * 60)
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Прокси не работает")
        print("   2. Неверный API_ID или API_HASH")
        print("   3. Нет интернета")

if __name__ == '__main__':
    asyncio.run(main())

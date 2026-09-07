import asyncio
from telethon import TelegramClient

API_ID = 35611241
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'
PHONE = '+79195260274'

# MTProto прокси (tg-ws-proxy)
PROXY = ('mtproto', '127.0.0.1', 1443, '14a68dd409b093983b6aa9ce9f79c9a5')

print("📱 Telegram клиент (MTProto прокси)")
print("🔒 Прокси: 127.0.0.1:1443")

client = TelegramClient('my_session_mtproto', API_ID, API_HASH, proxy=PROXY)

async def main():
    try:
        await client.start(phone=PHONE)
        me = await client.get_me()
        print(f"✅ Подключено! Аккаунт: {me.first_name}")
        
        print("\n📋 Список диалогов:")
        async for dialog in client.iter_dialogs(limit=15):
            print(f"   ID: {dialog.id} | {dialog.name}")
        
        await client.disconnect()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

asyncio.run(main())

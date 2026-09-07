import asyncio
from telethon import TelegramClient

# Вставьте ваши данные, полученные на my.telegram.org
API_ID = 35611241        # Замените на ваш api_id (целое число)
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'  # Замените на ваш api_hash (строка)
PHONE = '+79195260274'  # Ваш номер телефона с международным кодом

client = TelegramClient('my_session', API_ID, API_HASH)

async def main():
    await client.start(phone=PHONE)
    print("Успешное подключение к Telegram!\n")

    print("--- Список ваших каналов и диалогов ---")
    async for dialog in client.iter_dialogs(limit=20):
        print(f"ID: {dialog.id} | Тип: {'Канал/Группа' if dialog.is_channel else 'Чат/ЛС'} | Название: {dialog.name}")

    print("\n------------------------------------------------")
    target_id_str = input("Введите ID канала или чата для чтения сообщений: ").strip()
    
    try:
        target_id = int(target_id_str)
        print("\n--- Последние 10 сообщений ---")
        async for message in client.iter_messages(target_id, limit=10):
            sender = await message.get_sender()
            sender_name = getattr(sender, 'title', None) or getattr(sender, 'username', None) or "Unknown"
            date_str = message.date.strftime('%Y-%m-%d %H:%M:%S')
            text = message.text if message.text else "[Медиа-файл или системное сообщение]"
            print(f"[{date_str}] {sender_name}: {text}")
            print("-" * 30)
            
    except ValueError:
        print("Ошибка: введен неверный ID.")
    except Exception as e:
        print(f"Произошла ошибка при чтении сообщений: {e}")

if __name__ == '__main__':
    asyncio.run(main())

import asyncio
from telethon import TelegramClient
import socks
import time

API_ID = 35611241
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'
PHONE = '+79195260274'

# Список прокси для теста
proxies = [
    {'host': '8.221.141.88', 'port': 1080, 'type': 'socks4'},
    {'host': '47.104.28.135', 'port': 4216, 'type': 'socks4'},
    {'host': '101.200.158.109', 'port': 8080, 'type': 'socks4'},
    {'host': '8.213.195.191', 'port': 37, 'type': 'socks4'},
]

async def test_proxy(proxy_info):
    print(f"\n🔍 Тестируем прокси: {proxy_info['host']}:{proxy_info['port']} ({proxy_info['type']})")
    
    proxy_type = socks.SOCKS4 if proxy_info['type'] == 'socks4' else socks.SOCKS5
    proxy = (proxy_type, proxy_info['host'], proxy_info['port'])
    
    try:
        client = TelegramClient('test_session', API_ID, API_HASH, proxy=proxy)
        
        # Устанавливаем таймаут 15 секунд
        await asyncio.wait_for(
            client.start(phone=PHONE),
            timeout=15
        )
        
        me = await client.get_me()
        print(f"✅ РАБОТАЕТ! Прокси {proxy_info['host']}:{proxy_info['port']} - {me.first_name}")
        await client.disconnect()
        return True, proxy_info
        
    except asyncio.TimeoutError:
        print(f"❌ Таймаут: {proxy_info['host']}:{proxy_info['port']}")
        return False, None
    except Exception as e:
        print(f"❌ Ошибка: {proxy_info['host']}:{proxy_info['port']} - {str(e)[:50]}")
        return False, None

async def main():
    print("=" * 60)
    print("🔍 Тестирование прокси для Telegram")
    print("=" * 60)
    
    for proxy in proxies:
        success, working = await test_proxy(proxy)
        if success:
            print("\n" + "=" * 60)
            print(f"🎉 Найден рабочий прокси: {working['host']}:{working['port']}")
            print("=" * 60)
            return working
    
    print("\n❌ Ни один прокси не работает")
    return None

if __name__ == '__main__':
    working = asyncio.run(main())
    
    if working:
        print(f"\n✅ Рабочий прокси: {working['host']}:{working['port']}")
        print("Сохраните его для использования.")
    else:
        print("\n💡 Попробуйте другие прокси из списка.")

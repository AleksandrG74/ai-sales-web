import asyncio
from telethon import TelegramClient
import socks

API_ID = 35611241
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'
PHONE = '+79195260274'

# HTTP/HTTPS прокси из вашего списка
# (Telethon может работать с HTTP через SOCKS5 обёртку)
proxies = [
    {'host': '14.186.61.187', 'port': 8080, 'type': 'http'},  # Вьетнам
    {'host': '123.140.146.34', 'port': 8080, 'type': 'http'}, # Южная Корея
    {'host': '190.145.194.210', 'port': 443, 'type': 'https'}, # Колумбия
    {'host': '167.86.93.118', 'port': 8080, 'type': 'http'},  # Германия
]

async def test_proxy(proxy_info):
    print(f"\n🔍 Тестируем: {proxy_info['host']}:{proxy_info['port']} ({proxy_info['type']})")
    
    # HTTP прокси используем как SOCKS5 (некоторые работают)
    proxy = (socks.SOCKS5, proxy_info['host'], proxy_info['port'])
    
    try:
        client = TelegramClient('test_session', API_ID, API_HASH, proxy=proxy)
        
        await asyncio.wait_for(
            client.start(phone=PHONE),
            timeout=15
        )
        
        me = await client.get_me()
        print(f"✅ РАБОТАЕТ! {proxy_info['host']}:{proxy_info['port']}")
        await client.disconnect()
        return True, proxy_info
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)[:80]}")
        return False, None

async def main():
    print("=" * 60)
    print("🔍 Тестирование HTTP/HTTPS прокси")
    print("=" * 60)
    
    for proxy in proxies:
        success, working = await test_proxy(proxy)
        if success:
            print("\n" + "=" * 60)
            print(f"🎉 Рабочий прокси: {working['host']}:{working['port']}")
            print("=" * 60)
            return working
    
    print("\n❌ HTTP/HTTPS прокси не работают с Telegram")
    print("💡 Используйте веб-версию: python web_telegram_simple.py")
    return None

if __name__ == '__main__':
    asyncio.run(main())

import asyncio
from telethon import TelegramClient
import socks

API_ID = 35611241
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'
PHONE = '+79195260274'

# Новые прокси из списка
proxies = [
    {'host': '8.211.42.167', 'port': 1080, 'type': 'socks4'},
    {'host': '8.211.51.115', 'port': 1080, 'type': 'socks4'},
    {'host': '94.131.12.128', 'port': 1080, 'type': 'socks4'},
    {'host': '82.200.235.134', 'port': 1080, 'type': 'socks4'},
    {'host': '47.250.11.111', 'port': 1080, 'type': 'socks4'},
    {'host': '67.201.39.14', 'port': 1080, 'type': 'socks4'},
    {'host': '87.117.11.57', 'port': 1080, 'type': 'socks4'},
    {'host': '8.210.17.35', 'port': 1080, 'type': 'socks4'},
    {'host': '8.220.141.8', 'port': 1080, 'type': 'socks4'},
]

async def test_proxy(proxy_info):
    print(f"\n🔍 Тестируем: {proxy_info['host']}:{proxy_info['port']}")
    
    proxy = (socks.SOCKS4, proxy_info['host'], proxy_info['port'])
    
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
        print(f"❌ Ошибка: {str(e)[:60]}")
        return False, None

async def main():
    print("=" * 60)
    print("🔍 Тестирование прокси для Telegram")
    print("=" * 60)
    
    for proxy in proxies:
        success, working = await test_proxy(proxy)
        if success:
            print("\n" + "=" * 60)
            print(f"🎉 Рабочий прокси: {working['host']}:{working['port']}")
            print("=" * 60)
            return working
    
    print("\n❌ Ни один прокси не работает")
    return None

if __name__ == '__main__':
    working = asyncio.run(main())
    
    if working:
        print(f"\n✅ Рабочий прокси: {working['host']}:{working['port']}")
    else:
        print("\n💡 Все прокси не работают с Telegram.")
        print("   Используйте веб-версию: python web_telegram_simple.py")

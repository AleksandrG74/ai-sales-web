import asyncio
from telethon import TelegramClient
import socks

API_ID = 35611241
API_HASH = 'dd41c4667ac94a6d7b62b6f4b922ba84'
PHONE = '+79195260274'

# Прокси, помеченные для Telegram
proxies = [
    {'host': '157.20.233.65', 'port': 3125, 'type': 'https', 'name': 'Telegram API'},
    {'host': '5.130.50.118', 'port': 1080, 'type': 'socks5', 'name': 'SOCKS5 Россия'},
    {'host': '204.152.192.24', 'port': 10808, 'type': 'socks5', 'name': 'HTTPS/SOCKS5 США'},
    {'host': '103.79.183.158', 'port': 1080, 'type': 'socks4', 'name': 'SOCKS4 Бангладеш'},
]

async def test_proxy(proxy_info):
    print(f"\n🔍 Тестируем: {proxy_info['name']} ({proxy_info['host']}:{proxy_info['port']})")
    
    # Определяем тип прокси
    if proxy_info['type'] == 'socks5':
        proxy = (socks.SOCKS5, proxy_info['host'], proxy_info['port'])
    elif proxy_info['type'] == 'socks4':
        proxy = (socks.SOCKS4, proxy_info['host'], proxy_info['port'])
    else:  # HTTP/HTTPS используем как SOCKS5
        proxy = (socks.SOCKS5, proxy_info['host'], proxy_info['port'])
    
    try:
        client = TelegramClient('test_session', API_ID, API_HASH, proxy=proxy)
        
        await asyncio.wait_for(
            client.start(phone=PHONE),
            timeout=20
        )
        
        me = await client.get_me()
        print(f"✅ РАБОТАЕТ! {proxy_info['name']} - {me.first_name}")
        await client.disconnect()
        return True, proxy_info
        
    except asyncio.TimeoutError:
        print(f"❌ Таймаут")
        return False, None
    except Exception as e:
        print(f"❌ Ошибка: {str(e)[:80]}")
        return False, None

async def main():
    print("=" * 60)
    print("🔍 Тестирование прокси для Telegram API")
    print("=" * 60)
    
    for proxy in proxies:
        success, working = await test_proxy(proxy)
        if success:
            print("\n" + "=" * 60)
            print(f"🎉 РАБОЧИЙ ПРОКСИ: {working['host']}:{working['port']}")
            print(f"   Тип: {working['type']}")
            print("=" * 60)
            print("\n✅ Сохраните эти данные для подключения к Telegram!")
            return working
    
    print("\n❌ Ни один прокси не работает")
    print("\n💡 Рекомендация: используйте веб-версию")
    print("   python web_telegram_simple.py")
    return None

if __name__ == '__main__':
    working = asyncio.run(main())
    
    if working:
        print(f"\n📋 Итоговые данные:")
        print(f"   Прокси: {working['host']}:{working['port']}")
        print(f"   Тип: {working['type']}")
        print(f"   Назначение: {working['name']}")

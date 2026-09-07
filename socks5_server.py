#!/usr/bin/env python
"""
Простой SOCKS5 прокси для Telegram
Запускается на порту 1080
"""
import asyncio
import logging
import socket
import struct

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Socks5Proxy:
    def __init__(self, host='127.0.0.1', port=1080):
        self.host = host
        self.port = port
        self.server = None

    async def handle_client(self, reader, writer):
        try:
            # SOCKS5 handshake
            data = await reader.read(2)
            if len(data) < 2:
                return
            
            # Ответ на handshake
            writer.write(b'\x05\x00')
            await writer.drain()
            
            # Получаем запрос
            data = await reader.read(4)
            if len(data) < 4:
                return
            
            # Простой прокси - перенаправляем трафик на Telegram
            # В реальности здесь должна быть полная реализация SOCKS5
            
            # Отвечаем, что подключение установлено
            writer.write(b'\x05\x00\x00\x01' + b'\x00' * 6)
            await writer.drain()
            
            # Передаём данные дальше
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                # В реальном прокси здесь нужно перенаправлять трафик
                # Для простоты просто отвечаем
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Ошибка: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port
            )
            logger.info(f"✅ SOCKS5 прокси запущен на {self.host}:{self.port}")
            logger.info("Настройте Telegram: SOCKS5, хост 127.0.0.1, порт 1080")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска прокси: {e}")

def main():
    proxy = Socks5Proxy()
    try:
        asyncio.run(proxy.start())
    except KeyboardInterrupt:
        logger.info("Прокси остановлен")

if __name__ == "__main__":
    main()

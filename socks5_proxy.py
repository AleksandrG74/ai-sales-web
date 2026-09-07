#!/usr/bin/env python
"""
Простой SOCKS5 прокси на Python для Telegram
"""
import socket
import threading
import logging
import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_client(client_sock):
    try:
        # SOCKS5 handshake
        data = client_sock.recv(2)
        if not data or len(data) < 2:
            client_sock.close()
            return
        
        # Отвечаем на handshake
        client_sock.send(b'\x05\x00')
        
        # Получаем запрос
        data = client_sock.recv(4)
        if not data or len(data) < 4:
            client_sock.close()
            return
        
        # Простой ответ (для демонстрации)
        client_sock.send(b'\x05\x00\x00\x01' + b'\x00' * 6)
        
        # Держим соединение открытым
        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            # Для теста просто эхо
            client_sock.send(data)
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        client_sock.close()

def start_proxy(host='127.0.0.1', port=1080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    
    logger.info(f"✅ SOCKS5 прокси запущен на {host}:{port}")
    logger.info("Настройте Telegram: SOCKS5, хост 127.0.0.1, порт 1080")
    
    while True:
        client, addr = server.accept()
        logger.info(f"Подключение от {addr}")
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_proxy()

#!/usr/bin/env python
"""
Полноценный SOCKS5 прокси на Python с использованием PySocks
"""
import socket
import threading
import logging
import sys
import select

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Socks5Proxy:
    def __init__(self, host='127.0.0.1', port=1080):
        self.host = host
        self.port = port
        self.running = True

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        server.settimeout(1.0)
        
        logger.info(f"✅ SOCKS5 прокси запущен на {self.host}:{self.port}")
        logger.info(f"Настройте Telegram: SOCKS5, хост 127.0.0.1, порт 1080")
        
        while self.running:
            try:
                client, addr = server.accept()
                logger.info(f"Подключение от {addr}")
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Ошибка при принятии соединения: {e}")
                
        server.close()
        logger.info("Прокси остановлен")

    def handle_client(self, client_sock):
        try:
            # SOCKS5 Handshake
            data = client_sock.recv(262)
            if not data or data[0] != 0x05:
                client_sock.close()
                return
            
            # Отправляем ответ на handshake
            client_sock.send(b'\x05\x00')
            
            # Получаем запрос
            data = client_sock.recv(262)
            if not data:
                client_sock.close()
                return
            
            # Проверяем версию и команду
            if data[0] != 0x05 or data[1] != 0x01:
                client_sock.close()
                return
            
            # Получаем адрес и порт
            addr_type = data[3]
            if addr_type == 0x01:  # IPv4
                addr = socket.inet_ntoa(data[4:8])
                port = int.from_bytes(data[8:10], byteorder='big')
            elif addr_type == 0x03:  # Доменное имя
                name_len = data[4]
                addr = data[5:5+name_len].decode('utf-8')
                port = int.from_bytes(data[5+name_len:7+name_len], byteorder='big')
            else:
                client_sock.close()
                return
            
            logger.info(f"Подключение к {addr}:{port}")
            
            # Создаём подключение к целевому серверу
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.settimeout(30)
            
            try:
                target_sock.connect((addr, port))
                # Отправляем успешный ответ
                client_sock.send(b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + b'\x00\x00')
                
                # Перенаправляем трафик
                self.bridge(client_sock, target_sock)
                
            except Exception as e:
                logger.error(f"Ошибка подключения к {addr}:{port}: {e}")
                client_sock.send(b'\x05\x01\x00\x01' + b'\x00' * 6)
            finally:
                target_sock.close()
                
        except Exception as e:
            logger.error(f"Ошибка обработки клиента: {e}")
        finally:
            client_sock.close()

    def bridge(self, sock1, sock2):
        """Перенаправление трафика между двумя сокетами"""
        socks = [sock1, sock2]
        while True:
            try:
                rlist, _, _ = select.select(socks, [], [], 30)
                if not rlist:
                    continue
                    
                for sock in rlist:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return
                        if sock is sock1:
                            sock2.send(data)
                        else:
                            sock1.send(data)
                    except:
                        return
            except:
                return

if __name__ == "__main__":
    try:
        proxy = Socks5Proxy()
        proxy.start()
    except KeyboardInterrupt:
        logger.info("Прокси остановлен пользователем")
        sys.exit(0)

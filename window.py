# window.py - Отдельное окно для веб-интерфейса с логированием
import webview
import threading
import time
import socket
import sys
import os
from datetime import datetime

# Создаем папку для логов
os.makedirs("logs", exist_ok=True)

def log_message(msg):
    """Записывает сообщение в файл и выводит в консоль"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    with open("logs/window.log", "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

def wait_for_server(host="127.0.0.1", port=8000, timeout=10):
    """Ожидает, пока сервер запустится"""
    log_message(f"⏳ Ожидание сервера {host}:{port} (таймаут {timeout} сек)...")
    start_time = time.time()
    attempt = 0
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                log_message(f"✅ Сервер запущен и готов! (попытка {attempt})")
                return True
        except Exception as e:
            log_message(f"⚠️ Ошибка при проверке: {e}")
        time.sleep(0.5)
        if attempt % 4 == 0:  # Каждые 2 секунды
            log_message(f"⏳ Ожидание... {attempt} попытка")
    log_message(f"❌ Сервер не запустился за {timeout} секунд!")
    return False

def start_server():
    """Запускает FastAPI сервер в отдельном потоке"""
    log_message("🚀 Запуск сервера...")
    try:
        import uvicorn
        from backend.main import app
        log_message("✅ Uvicorn и backend импортированы успешно")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
        log_message("✅ Сервер завершил работу")
    except Exception as e:
        log_message(f"❌ Ошибка запуска сервера: {e}")
        import traceback
        log_message(traceback.format_exc())

def check_server_reload(window):
    """Проверяет сервер и перезагружает окно"""
    log_message("🔍 Запущен поток проверки сервера")
    
    # Ждем запуска сервера
    if wait_for_server(timeout=15):
        log_message("✅ Сервер готов! Перезагружаем окно...")
        try:
            # Пробуем перезагрузить через JavaScript
            log_message("🔄 Выполняем location.reload()")
            window.evaluate_js('location.reload()')
            log_message("✅ Перезагрузка выполнена")
        except Exception as e:
            log_message(f"❌ Ошибка при перезагрузке: {e}")
            import traceback
            log_message(traceback.format_exc())
    else:
        log_message("❌ Сервер не запустился, окно останется пустым")

def on_closed():
    """Вызывается при закрытии окна"""
    log_message("🛑 Окно закрыто пользователем")

def main():
    log_message("=" * 60)
    log_message("🔄 ЗАПУСК ПРИЛОЖЕНИЯ")
    log_message("=" * 60)
    log_message(f"📁 Текущая директория: {os.getcwd()}")
    
    # Проверяем, что файлы существуют
    log_message("📋 Проверка файлов...")
    if os.path.exists("window.py"):
        log_message("✅ window.py найден")
    else:
        log_message("❌ window.py НЕ найден!")
    
    if os.path.exists("backend/main.py"):
        log_message("✅ backend/main.py найден")
    else:
        log_message("❌ backend/main.py НЕ найден!")
    
    # Запускаем сервер в фоновом потоке
    log_message("🔄 Запуск серверного потока...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    log_message("✅ Серверный поток запущен")
    
    # Небольшая задержка перед открытием окна
    log_message("⏳ Пауза 1 секунда перед открытием окна...")
    time.sleep(1)
    
    # Создаем окно
    log_message("🌐 Создание окна...")
    try:
        window = webview.create_window(
            title="AI Sales Agent",
            url="http://127.0.0.1:8000",
            width=1400,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(900, 600)
        )
        log_message(f"✅ Окно создано: {window}")
    except Exception as e:
        log_message(f"❌ Ошибка создания окна: {e}")
        import traceback
        log_message(traceback.format_exc())
        return
    
    # Запускаем поток для перезагрузки (проверка сервера)
    log_message("🔄 Запуск потока проверки сервера...")
    check_thread = threading.Thread(
        target=check_server_reload, 
        args=(window,), 
        daemon=True
    )
    check_thread.start()
    log_message("✅ Поток проверки запущен")
    
    # Запускаем окно
    log_message("🚀 Запуск WebView...")
    try:
        webview.start(debug=False, http_server=True)
        log_message("✅ WebView завершил работу")
    except Exception as e:
        log_message(f"❌ Ошибка WebView: {e}")
        import traceback
        log_message(traceback.format_exc())

if __name__ == "__main__":
    main()

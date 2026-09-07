import webview
import threading
import time
import socket
import sys

def wait_for_server(host="127.0.0.1", port=8000, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def start_server():
    import uvicorn
    from backend.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def main():
    print("🚀 Запуск сервера...")
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    
    print("⏳ Ожидание сервера...")
    if not wait_for_server():
        print("❌ Сервер не запустился!")
        return
    
    print("✅ Сервер запущен!")
    print("🌐 Открываем окно...")
    
    webview.create_window(
        "AI Sales Agent",
        "http://127.0.0.1:8000",
        width=1200,
        height=700,
        resizable=True
    )
    webview.start()

if __name__ == "__main__":
    main()
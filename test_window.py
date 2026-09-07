import webview

def main():
    # Создаем простейшее окно с приветствием
    window = webview.create_window(
        title="Тестовое окно",
        url="<h1>Привет! Это тестовое окно.</h1><p>Если вы это видите - WebView работает!</p>",
        width=600,
        height=400
    )
    webview.start()

if __name__ == "__main__":
    main()

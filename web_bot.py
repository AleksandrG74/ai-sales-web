#!/usr/bin/env python
"""
Бот, работающий через веб-версию Telegram
Использует Selenium для автоматизации браузера
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WebTelegramBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.keywords = ["холодильник", "купить", "нужен", "ищу"]
        
    def setup_driver(self):
        """Настройка браузера"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ Браузер запущен")
        
    def open_telegram(self):
        """Открываем web.telegram.org"""
        print("📱 Открываем web.telegram.org...")
        self.driver.get("https://web.telegram.org/k/")
        
        print("\n✅ Войдите в Telegram (QR-код или номер телефона)")
        print("⏳ После входа нажмите Enter...")
        input()
        return True
    
    def read_messages(self):
        """Читает новые сообщения"""
        print("\n📖 Чтение сообщений...")
        
        # Ищем непрочитанные сообщения
        unread = self.driver.find_elements(By.CSS_SELECTOR, ".unread")
        print(f"📨 Найдено непрочитанных: {len(unread)}")
        
        # Кликаем по первому непрочитанному
        if unread:
            unread[0].click()
            time.sleep(2)
        
        # Получаем сообщения
        messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
        
        results = []
        for msg in messages[-10:]:
            text = msg.text
            if text and len(text) > 5:
                results.append(text)
        
        return results
    
    def send_message(self, chat, text):
        """Отправляет сообщение"""
        try:
            # Находим поле ввода
            input_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".input-message"))
            )
            input_field.clear()
            input_field.send_keys(text)
            
            # Отправляем
            send_btn = self.driver.find_element(By.CSS_SELECTOR, ".send-button")
            send_btn.click()
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def analyze_message(self, text):
        """Анализирует сообщение"""
        score = 0
        text_lower = text.lower()
        
        for kw in self.keywords:
            if kw in text_lower:
                score += 20
        
        buy_words = ['купить', 'хочу', 'нужен']
        for word in buy_words:
            if word in text_lower:
                score += 15
        
        return min(score, 100)
    
    def run(self):
        """Запуск"""
        print("=" * 60)
        print("🤖 Telegram Бот (через веб-версию)")
        print("=" * 60)
        
        self.setup_driver()
        self.open_telegram()
        
        print("\n🔄 Ожидание сообщений...")
        print("   (нажмите Ctrl+C для выхода)")
        
        try:
            while True:
                # Читаем сообщения
                messages = self.read_messages()
                
                for msg in messages:
                    score = self.analyze_message(msg)
                    if score > 50:
                        print(f"\n💬 Найдено: {msg[:50]}... (Score: {score}%)")
                        # Здесь можно отправить ответ
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Остановка...")
        
        self.driver.quit()

if __name__ == "__main__":
    bot = WebTelegramBot()
    bot.run()

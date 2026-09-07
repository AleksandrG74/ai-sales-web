#!/usr/bin/env python
"""
Программа для парсинга сообщений из web.telegram.org
Использует Selenium для извлечения реальных данных из браузера
"""

import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TelegramWebParser:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = []
        self.keywords = ["холодильник", "купить", "нужен", "ищу", "техника"]
        
    def setup_driver(self):
        """Настройка браузера"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Используем ваш существующий профиль Chrome с VPN
        # (если вы используете Chrome с расширением VPN)
        # Укажите путь к вашему профилю
        # options.add_argument("--user-data-dir=C:/Users/52602/AppData/Local/Google/Chrome/User Data")
        # options.add_argument("--profile-directory=Default")
        
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
        
        # Ждём загрузки чатов
        time.sleep(3)
        return True
    
    def get_chats(self):
        """Получаем список чатов"""
        print("\n📋 Получаем список чатов...")
        
        try:
            # Ищем элементы чатов
            chat_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.chat-item")
            
            if not chat_elements:
                # Пробуем другие селекторы
                chat_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'chat')]")
            
            chats = []
            for el in chat_elements[:10]:  # Берём первые 10 чатов
                try:
                    name = el.text.split('\n')[0] if el.text else "Без названия"
                    if name and len(name) > 1:
                        chats.append({
                            'element': el,
                            'name': name
                        })
                except:
                    continue
            
            print(f"✅ Найдено чатов: {len(chats)}")
            return chats
            
        except Exception as e:
            print(f"❌ Ошибка получения чатов: {e}")
            return []
    
    def read_messages_from_chat(self, chat_element):
        """Читает сообщения из конкретного чата"""
        try:
            # Кликаем по чату
            chat_element.click()
            time.sleep(2)
            
            # Ждём загрузки сообщений
            messages = self.driver.find_elements(By.CSS_SELECTOR, "div.message")
            
            if not messages:
                messages = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'message')]")
            
            texts = []
            for msg in messages[:20]:  # Берём первые 20 сообщений
                try:
                    text = msg.text
                    if text and len(text) > 5:
                        texts.append(text)
                except:
                    continue
            
            return texts
            
        except Exception as e:
            print(f"❌ Ошибка чтения: {e}")
            return []
    
    def analyze_messages(self, messages, chat_name):
        """Анализирует сообщения на наличие ключевых слов"""
        found = []
        
        for msg in messages:
            score = self.calculate_score(msg)
            if score > 30:
                found.append({
                    'chat': chat_name,
                    'message': msg[:200],
                    'score': score
                })
        
        return found
    
    def calculate_score(self, text):
        """Вычисляет Intent Score"""
        score = 0
        text_lower = text.lower()
        
        for kw in self.keywords:
            if kw in text_lower:
                score += 20
        
        buy_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен']
        for word in buy_words:
            if word in text_lower:
                score += 15
        
        urgency = ['срочно', 'сегодня', 'завтра', 'быстро']
        for word in urgency:
            if word in text_lower:
                score += 10
        
        return min(score, 100)
    
    def run(self):
        """Запуск парсинга"""
        print("=" * 50)
        print("📱 Telegram Парсер (web.telegram.org)")
        print("=" * 50)
        
        self.setup_driver()
        
        if not self.open_telegram():
            self.driver.quit()
            return
        
        # Получаем чаты
        chats = self.get_chats()
        
        all_results = []
        
        for chat in chats:
            print(f"\n📌 Чат: {chat['name']}")
            messages = self.read_messages_from_chat(chat['element'])
            
            if messages:
                print(f"   📨 Прочитано сообщений: {len(messages)}")
                results = self.analyze_messages(messages, chat['name'])
                all_results.extend(results)
                
                # Показываем найденные сообщения
                for res in results:
                    print(f"   🔍 Найдено: {res['message'][:50]}... (Score: {res['score']}%)")
            else:
                print("   ❌ Сообщений не найдено")
        
        # Сохраняем результаты
        self.save_results(all_results)
        
        # Закрываем браузер
        print("\n⏳ Нажмите Enter для закрытия браузера...")
        input()
        self.driver.quit()
        
        return all_results
    
    def save_results(self, results):
        """Сохраняет результаты в файл"""
        if not results:
            print("\n❌ Клиенты не найдены")
            return
        
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ПОИСКА")
        print("=" * 50)
        
        # Группируем по чатам
        chats = {}
        for r in results:
            chat_name = r['chat']
            if chat_name not in chats:
                chats[chat_name] = []
            chats[chat_name].append(r)
        
        for chat_name, items in chats.items():
            print(f"\n📌 Чат: {chat_name}")
            for i, item in enumerate(items, 1):
                status = "Готов купить" if item['score'] > 70 else "Интересуется"
                print(f"   {i}. {item['message'][:60]}...")
                print(f"      🎯 Score: {item['score']}% | {status}")
        
        # Сохраняем в JSON
        output = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }
        
        with open('telegram_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в telegram_results.json")
        print(f"   Всего найдено: {len(results)}")

if __name__ == "__main__":
    parser = TelegramWebParser()
    parser.run()

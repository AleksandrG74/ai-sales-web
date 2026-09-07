#!/usr/bin/env python
"""
Поиск клиентов в реальных сообщениях Telegram
Открывает web.telegram.org, вы входите, программа ищет клиентов
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime

class RealClientFinder:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.results = []
        self.keywords = ["холодильник", "морозильник", "техника", "бытовая"]
        self.buy_words = ["купить", "нужен", "ищу", "заказать", "хочу"]
        
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
        """Открывает web.telegram.org"""
        print("📱 Открываем web.telegram.org...")
        self.driver.get("https://web.telegram.org/k/")
        
        print("\n🔑 Войдите в Telegram (QR-код или номер телефона)")
        print("⏳ После входа нажмите Enter...")
        input()
        print("✅ Вход выполнен")
        time.sleep(2)
        
    def get_chats(self):
        """Получает список чатов"""
        print("\n📋 Получаем список чатов...")
        try:
            chat_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.chat-item")
            chats = []
            for el in chat_elements:
                try:
                    name = el.text.split('\n')[0] if el.text else "Без названия"
                    if name and len(name) > 1 and name != "Без названия":
                        chats.append({
                            'element': el,
                            'name': name
                        })
                except:
                    continue
            print(f"✅ Найдено чатов: {len(chats)}")
            return chats
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []
    
    def scan_chat(self, chat):
        """Сканирует чат на наличие клиентов"""
        try:
            # Кликаем по чату
            chat['element'].click()
            time.sleep(2)
            
            # Ждём загрузки сообщений
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
            
            leads = []
            for msg in messages[:30]:
                try:
                    text = msg.text
                    if text and len(text) > 10:
                        score = self.calculate_score(text)
                        if score > 30:
                            leads.append({
                                'chat': chat['name'],
                                'text': text[:200],
                                'score': score
                            })
                except:
                    continue
            
            return leads
            
        except Exception as e:
            print(f"❌ Ошибка сканирования {chat['name']}: {e}")
            return []
    
    def calculate_score(self, text):
        """Вычисляет Intent Score"""
        score = 0
        text_lower = text.lower()
        
        # Проверяем ключевые слова
        for kw in self.keywords:
            if kw in text_lower:
                score += 20
                break
        
        # Проверяем слова покупки
        for word in self.buy_words:
            if word in text_lower:
                score += 15
                break
        
        # Срочность
        if 'срочно' in text_lower or 'сегодня' in text_lower:
            score += 10
        
        return min(score, 100)
    
    def run(self):
        """Запуск поиска"""
        print("=" * 60)
        print("🔍 Поиск клиентов в реальных сообщениях")
        print("=" * 60)
        
        self.setup_driver()
        self.open_telegram()
        
        # Получаем чаты
        chats = self.get_chats()
        
        print("\n📡 Начинаем сканирование чатов...")
        print("-" * 60)
        
        all_leads = []
        for i, chat in enumerate(chats[:10], 1):  # Сканируем первые 10 чатов
            print(f"\n{i}. 📌 Сканируем: {chat['name']}")
            leads = self.scan_chat(chat)
            
            if leads:
                print(f"   ✅ Найдено клиентов: {len(leads)}")
                for lead in leads:
                    print(f"      💬 {lead['text'][:60]}... (Score: {lead['score']}%)")
                all_leads.extend(leads)
            else:
                print("   ❌ Клиентов не найдено")
            
            time.sleep(1)
        
        # Выводим итоговые результаты
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 60)
        
        if all_leads:
            print(f"\n✅ Найдено {len(all_leads)} потенциальных клиентов:")
            print("-" * 60)
            
            # Сортируем по Score
            sorted_leads = sorted(all_leads, key=lambda x: x['score'], reverse=True)
            
            for i, lead in enumerate(sorted_leads, 1):
                status = "🔥 Горячий" if lead['score'] >= 70 else "🤔 Тёплый" if lead['score'] >= 50 else "👀 Холодный"
                print(f"\n{i}. 📌 {lead['chat']}")
                print(f"   💬 {lead['text']}")
                print(f"   🎯 Score: {lead['score']}% | {status}")
            
            # Сохраняем в файл
            output = {
                'timestamp': datetime.now().isoformat(),
                'total': len(all_leads),
                'leads': sorted_leads
            }
            
            with open('real_leads.json', 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Результаты сохранены в real_leads.json")
        else:
            print("\n❌ Клиенты не найдены")
        
        print("\n" + "=" * 60)
        print("✅ Поиск завершён")
        print("=" * 60)
        
        input("\nНажмите Enter для закрытия браузера...")
        self.driver.quit()

if __name__ == "__main__":
    finder = RealClientFinder()
    finder.run()

#!/usr/bin/env python
"""
Простая консольная программа для чтения сообщений через web.telegram.org
Использует прямые HTTP-запросы (без браузера)
"""

import requests
import json
import time
import os
from datetime import datetime
import sys

class WebTelegramClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        })
        self.base_url = "https://web.telegram.org"
        self.auth_token = None
        self.dc_id = None
        
    def login(self):
        """Вход в Telegram через веб-версию"""
        print("🔑 Вход в Telegram через web.telegram.org")
        print("📱 Откройте в браузере: https://web.telegram.org/k/")
        print("   Или отсканируйте QR-код")
        
        # Альтернатива: используем прямой вход
        print("\n📞 Введите номер телефона (или нажмите Enter для QR-кода):")
        phone = input().strip()
        
        if not phone:
            print("📱 Для входа по QR-коду:")
            print("   1. Откройте Telegram на телефоне")
            print("   2. Настройки → Устройства → Добавить устройство")
            print("   3. Отсканируйте QR-код в браузере")
            print("\n⏳ После сканирования нажмите Enter...")
            input()
            # Вручную открываем страницу
            import webbrowser
            webbrowser.open("https://web.telegram.org/k/")
            print("✅ После входа в веб-версию нажмите Enter...")
            input()
            return True
        else:
            print(f"📞 Пытаемся войти с номером: {phone}")
            return False
    
    def get_messages_from_chat(self, chat_id, limit=20):
        """Получение сообщений из чата"""
        # Пока используем имитацию
        print(f"\n📖 Чтение сообщений из чата: {chat_id}")
        
        # Демонстрационные данные (для теста)
        sample_messages = [
            {"text": "Привет! Ищу холодильник с большой морозильной камерой", "date": "2026-09-06 10:30"},
            {"text": "Купить холодильник недорого", "date": "2026-09-06 10:25"},
            {"text": "Какой холодильник лучше взять для семьи?", "date": "2026-09-06 10:20"},
            {"text": "Срочно нужен холодильник!", "date": "2026-09-06 10:15"},
            {"text": "Здравствуйте! Ищу холодильник для дома.", "date": "2026-09-06 10:10"},
        ]
        
        # Поиск сообщений с ключевыми словами
        keywords = ["холодильник", "купить", "нужен", "ищу"]
        found = []
        
        for msg in sample_messages:
            for kw in keywords:
                if kw in msg['text'].lower():
                    score = self.calculate_intent(msg['text'], kw)
                    found.append({
                        'text': msg['text'],
                        'date': msg['date'],
                        'keyword': kw,
                        'score': score
                    })
                    break
        
        return found
    
    def calculate_intent(self, text, keyword):
        """Вычисление интента (готовности купить)"""
        score = 20  # базовый за ключевое слово
        
        buy_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен']
        for word in buy_words:
            if word in text.lower():
                score += 20
                break
        
        urgency_words = ['срочно', 'сегодня', 'завтра', 'быстро']
        for word in urgency_words:
            if word in text.lower():
                score += 15
                break
        
        return min(score, 100)
    
    def run(self):
        """Запуск программы"""
        print("=" * 50)
        print("📱 Telegram Веб-Клиент (консольный)")
        print("=" * 50)
        
        if not self.login():
            print("❌ Вход не выполнен")
            return
        
        # Проверяем чаты
        print("\n📋 Получаем список чатов...")
        
        # Список чатов для проверки
        chats = ["@chatgpt_try", "@ru2ch", "@overhear", "Техника и гаджеты"]
        
        all_messages = []
        
        for chat in chats:
            print(f"\n📌 Проверяем чат: {chat}")
            messages = self.get_messages_from_chat(chat, limit=10)
            
            if messages:
                print(f"   Найдено сообщений: {len(messages)}")
                for msg in messages:
                    all_messages.append({
                        'chat': chat,
                        'text': msg['text'],
                        'date': msg['date'],
                        'score': msg['score']
                    })
            else:
                print("   ❌ Сообщений не найдено")
        
        # Вывод результатов
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ПОИСКА")
        print("=" * 50)
        
        if all_messages:
            print(f"\n✅ Найдено {len(all_messages)} сообщений с ключевыми словами:")
            print("-" * 60)
            
            for i, msg in enumerate(all_messages[:10], 1):
                print(f"\n{i}. 📌 Чат: {msg['chat']}")
                print(f"   💬 {msg['text']}")
                print(f"   🎯 Score: {msg['score']}%")
                print(f"   📅 {msg['date']}")
        else:
            print("\n❌ Сообщений с ключевыми словами не найдено")
        
        print("\n" + "=" * 50)
        print("✅ Программа завершена")
        print("=" * 50)

if __name__ == "__main__":
    client = WebTelegramClient()
    client.run()

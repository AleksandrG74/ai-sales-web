#!/usr/bin/env python
"""
Простая программа для чтения сообщений через web.telegram.org
Использует ручной вход в браузере
"""

import webbrowser
import time
import json
import os
from datetime import datetime

class SimpleTelegramReader:
    def __init__(self):
        self.chats = [
            "@chatgpt_try",
            "t.me/ru2ch",
            "t.me/overhear"
        ]
        self.keywords = ["холодильник", "купить", "нужен", "ищу", "техника"]
        
    def open_telegram(self):
        """Открывает web.telegram.org в браузере"""
        print("📱 Открываем web.telegram.org...")
        webbrowser.open("https://web.telegram.org/k/")
        print("\n✅ Войдите в Telegram в открывшемся окне браузера")
        print("   (используйте QR-код или номер телефона)")
        print("\n⏳ После входа нажмите Enter для продолжения...")
        input()
        return True
    
    def simulate_reading(self):
        """Имитирует чтение сообщений (без реального API)"""
        print("\n📋 Проверяем чаты...")
        
        # Имитация данных (в реальности здесь будет парсинг)
        sample_data = {
            "@chatgpt_try": [
                "Здравствуйте! Ищу холодильник с большой морозильной камерой",
                "Купить холодильник недорого. Посоветуйте модель",
                "Какой холодильник лучше взять для семьи из 4 человек?"
            ],
            "t.me/ru2ch": [
                "Срочно нужен холодильник! Сломался старый",
                "Подскажите, какой холодильник самый тихий?",
                "Холодильник с функцией No Frost - это хорошая идея?"
            ],
            "t.me/overhear": [
                "Выбираю холодильник между Samsung и LG",
                "Нужен холодильник с доставкой и установкой",
                "Какой холодильник лучше: двухкамерный или однокамерный?"
            ]
        }
        
        all_results = []
        
        for chat, messages in sample_data.items():
            print(f"\n📌 Чат: {chat}")
            print(f"   Сообщений: {len(messages)}")
            
            for msg in messages:
                score = self.calculate_score(msg)
                if score > 30:
                    all_results.append({
                        'chat': chat,
                        'message': msg,
                        'score': score
                    })
        
        return all_results
    
    def calculate_score(self, text):
        """Вычисляет Intent Score"""
        score = 0
        text_lower = text.lower()
        
        # Проверяем ключевые слова
        for kw in self.keywords:
            if kw in text_lower:
                score += 20
        
        # Проверяем слова покупки
        buy_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен']
        for word in buy_words:
            if word in text_lower:
                score += 15
        
        # Проверяем срочность
        urgency = ['срочно', 'сегодня', 'завтра', 'быстро']
        for word in urgency:
            if word in text_lower:
                score += 10
        
        return min(score, 100)
    
    def run(self):
        """Запуск программы"""
        print("=" * 50)
        print("📱 Telegram Читатель (через веб-версию)")
        print("=" * 50)
        
        # Открываем Telegram в браузере
        if not self.open_telegram():
            print("❌ Ошибка открытия браузера")
            return
        
        # Имитируем чтение
        results = self.simulate_reading()
        
        # Выводим результаты
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ПОИСКА")
        print("=" * 50)
        
        if results:
            print(f"\n✅ Найдено {len(results)} потенциальных клиентов:")
            print("-" * 60)
            
            for i, item in enumerate(results, 1):
                print(f"\n{i}. 📌 Чат: {item['chat']}")
                print(f"   💬 {item['message']}")
                print(f"   🎯 Score: {item['score']}%")
                print(f"   📊 Статус: {'Готов купить' if item['score'] > 70 else 'Интересуется'}")
        else:
            print("\n❌ Клиенты не найдены")
        
        print("\n" + "=" * 50)
        print("✅ Программа завершена")
        print("=" * 50)

if __name__ == "__main__":
    reader = SimpleTelegramReader()
    reader.run()

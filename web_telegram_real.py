#!/usr/bin/env python
"""
Telegram Читатель - работа с реальными сообщениями
Копируйте сообщения из веб-версии Telegram и вставляйте в программу
"""

import json
import re
from datetime import datetime

class TelegramRealReader:
    def __init__(self):
        self.keywords = ["холодильник", "купить", "нужен", "ищу", "техника", "морозильник"]
        self.buy_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен', 'ищу']
        self.urgency = ['срочно', 'сегодня', 'завтра', 'быстро', 'сейчас']
        
    def analyze_text(self, text):
        """Анализирует текст сообщений"""
        results = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Ищем ключевые слова
            score = self.calculate_score(line)
            
            if score > 20:
                results.append({
                    'text': line[:300],
                    'score': score,
                    'length': len(line)
                })
        
        return results
    
    def calculate_score(self, text):
        """Вычисляет Intent Score"""
        score = 0
        text_lower = text.lower()
        
        # Ключевые слова товара
        for kw in self.keywords:
            if kw in text_lower:
                score += 20
                break
        
        # Слова покупки
        for word in self.buy_words:
            if word in text_lower:
                score += 15
                break
        
        # Срочность
        for word in self.urgency:
            if word in text_lower:
                score += 10
                break
        
        # Вопросы
        if '?' in text or 'как' in text_lower or 'что' in text_lower:
            score += 5
        
        return min(score, 100)
    
    def get_messages_from_user(self):
        """Получает сообщения от пользователя"""
        print("\n📝 Введите сообщения из Telegram:")
        print("   (Скопируйте текст из веб-версии Telegram и вставьте сюда)")
        print("   (Закончите ввод пустой строкой)")
        print("-" * 60)
        
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        return '\n'.join(lines)
    
    def save_results(self, results):
        """Сохраняет результаты в файл"""
        if not results:
            return
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'results': results
        }
        
        with open('telegram_leads.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в telegram_leads.json")
    
    def print_results(self, results):
        """Выводит результаты"""
        if not results:
            print("\n❌ Клиенты не найдены")
            return
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("=" * 60)
        
        print(f"\n✅ Найдено {len(results)} потенциальных клиентов:")
        print("-" * 60)
        
        # Сортируем по Score
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        for i, item in enumerate(sorted_results, 1):
            score = item['score']
            if score >= 70:
                status = "🔥 ГОТОВ КУПИТЬ"
                emoji = "🔥"
            elif score >= 50:
                status = "🤔 АКТИВНО ИНТЕРЕСУЕТСЯ"
                emoji = "🤔"
            elif score >= 30:
                status = "👀 ПРОЯВЛЯЕТ ИНТЕРЕС"
                emoji = "👀"
            else:
                status = "❄️ ХОЛОДНЫЙ"
                emoji = "❄️"
            
            text = item['text']
            if len(text) > 80:
                text = text[:80] + "..."
            
            print(f"\n{i}. {emoji} {text}")
            print(f"   🎯 Score: {score}% | {status}")
    
    def run(self):
        """Запуск программы"""
        print("=" * 60)
        print("📱 Telegram Читатель - Реальные сообщения")
        print("=" * 60)
        
        print("\n📋 Инструкция:")
        print("1. Откройте web.telegram.org/k/ в браузере")
        print("2. Перейдите в любой чат")
        print("3. Выделите и скопируйте сообщения (Ctrl+C)")
        print("4. Вставьте их в программу")
        print("5. Нажмите Enter дважды для завершения ввода")
        print("-" * 60)
        
        # Получаем сообщения
        text = self.get_messages_from_user()
        
        if not text:
            print("\n❌ Сообщения не введены")
            return
        
        # Анализируем
        results = self.analyze_text(text)
        
        # Выводим результаты
        self.print_results(results)
        
        # Сохраняем
        if results:
            self.save_results(results)
        
        print("\n" + "=" * 60)
        print("✅ Программа завершена")
        print("=" * 60)

if __name__ == "__main__":
    reader = TelegramRealReader()
    reader.run()

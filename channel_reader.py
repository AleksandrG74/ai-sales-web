#!/usr/bin/env python
"""
Программа для чтения сообщений из каналов Telegram
Использует веб-версию через копирование
"""

import json
import re
from datetime import datetime

class ChannelReader:
    def __init__(self):
        self.channels = []
        self.keywords = ["холодильник", "купить", "нужен", "ищу", "техника"]
        
    def add_channel(self, name, messages):
        """Добавляет канал с сообщениями"""
        self.channels.append({
            'name': name,
            'messages': messages,
            'analyzed': []
        })
    
    def analyze_channel(self, channel):
        """Анализирует сообщения в канале"""
        results = []
        for msg in channel['messages']:
            score = self.calculate_score(msg)
            if score > 30:
                results.append({
                    'text': msg[:200],
                    'score': score
                })
        channel['analyzed'] = results
        return results
    
    def calculate_score(self, text):
        score = 0
        text_lower = text.lower()
        
        for kw in self.keywords:
            if kw in text_lower:
                score += 20
                break
        
        buy_words = ['купить', 'хочу', 'нужен']
        for word in buy_words:
            if word in text_lower:
                score += 15
                break
        
        return min(score, 100)
    
    def run(self):
        print("=" * 60)
        print("📢 Чтение сообщений из каналов Telegram")
        print("=" * 60)
        
        print("\n📋 Инструкция:")
        print("1. Откройте web.telegram.org/k/ в браузере")
        print("2. Откройте нужный канал (например, @tech_news)")
        print("3. Скопируйте сообщения из канала")
        print("4. Вставьте их в программу")
        print("5. Повторите для других каналов")
        print("-" * 60)
        
        while True:
            print("\n📌 Введите название канала (или Enter для завершения):")
            channel_name = input().strip()
            
            if not channel_name:
                break
            
            print(f"📝 Вставьте сообщения из канала {channel_name}:")
            print("   (Закончите ввод пустой строкой)")
            print("-" * 40)
            
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            
            if lines:
                self.add_channel(channel_name, lines)
                print(f"✅ Канал '{channel_name}' добавлен ({len(lines)} сообщений)")
        
        # Анализируем все каналы
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("=" * 60)
        
        total_leads = 0
        for channel in self.channels:
            results = self.analyze_channel(channel)
            total_leads += len(results)
            
            print(f"\n📌 Канал: {channel['name']}")
            print(f"   Всего сообщений: {len(channel['messages'])}")
            print(f"   Найдено клиентов: {len(results)}")
            
            for i, item in enumerate(results[:5], 1):
                print(f"   {i}. {item['text'][:60]}... (Score: {item['score']}%)")
        
        print("\n" + "=" * 60)
        print(f"✅ Всего найдено клиентов: {total_leads}")
        print("=" * 60)

if __name__ == "__main__":
    reader = ChannelReader()
    reader.run()

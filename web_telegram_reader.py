#!/usr/bin/env python
"""
Простая консольная программа для чтения сообщений через web.telegram.org
Использует библиотеку selenium для эмуляции браузера
"""

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WebTelegramReader:
    def __init__(self, phone, product="холодильник"):
        self.phone = phone
        self.product = product
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Настройка браузера для работы с web.telegram.org"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Добавляем user-agent чтобы не отличали от обычного пользователя
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Отключаем GPU для стабильности
        chrome_options.add_argument("--disable-gpu")
        
        # Запускаем браузер
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
        # Устанавливаем размер окна
        self.driver.set_window_size(1200, 800)
        
        print("✅ Браузер запущен")
        
    def login_to_telegram(self):
        """Вход в Telegram через веб-версию"""
        print("🔑 Открываем web.telegram.org...")
        self.driver.get("https://web.telegram.org/k/")
        
        try:
            # Ждём поле для ввода номера телефона
            print("⏳ Ожидаем загрузку страницы...")
            
            # Пробуем разные селекторы для ввода номера
            selectors = [
                "//input[@placeholder='Номер телефона']",
                "//input[@type='tel']",
                "//input[@name='phone']",
                "//input[contains(@class, 'input-field')]"
            ]
            
            phone_input = None
            for selector in selectors:
                try:
                    phone_input = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if phone_input:
                print("📱 Вводим номер телефона...")
                phone_input.clear()
                phone_input.send_keys(self.phone)
                
                # Находим кнопку "Далее"
                next_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Далее')]")))
                next_btn.click()
                
                print("⏳ Ожидаем код подтверждения...")
                print("   📲 Введите код, который пришёл в Telegram, в появившемся поле")
                
                # Ждём ввода кода пользователем вручную
                input("   Нажмите Enter после ввода кода...")
                
                # Ждём загрузки основного интерфейса
                time.sleep(5)
                print("✅ Вход выполнен успешно!")
                return True
            else:
                print("❌ Не удалось найти поле ввода телефона")
                return False
                
        except TimeoutException:
            print("❌ Таймаут при загрузке страницы")
            return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
    
    def search_channels(self, keywords):
        """Поиск каналов по ключевым словам"""
        print(f"\n🔍 Ищем каналы по ключевым словам: {keywords}")
        
        try:
            # Находим поле поиска
            search_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Поиск']")))
            search_input.clear()
            search_input.send_keys(keywords)
            time.sleep(2)
            
            # Получаем список результатов
            results = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'chat-item')]")
            
            channels = []
            for result in results[:5]:  # Берём первые 5
                try:
                    name = result.text.split('\n')[0] if result.text else "Без названия"
                    channels.append(name)
                except:
                    continue
            
            print(f"📡 Найдено каналов: {len(channels)}")
            return channels
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return []
    
    def read_messages(self, channel_name, limit=10):
        """Чтение сообщений из канала"""
        print(f"\n📖 Читаем сообщения из канала: {channel_name}")
        
        try:
            # Ищем канал по имени
            search_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Поиск']")))
            search_input.clear()
            search_input.send_keys(channel_name)
            time.sleep(2)
            
            # Нажимаем на канал
            channel = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{channel_name}')]")))
            channel.click()
            time.sleep(3)
            
            # Ждём загрузки сообщений
            messages = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'message')]")
            
            results = []
            for msg in messages[:limit]:
                try:
                    text = msg.text
                    if text and len(text) > 5:
                        results.append(text)
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ Ошибка чтения: {e}")
            return []
    
    def search_leads(self, keywords, channels_to_scan=3):
        """Поиск потенциальных клиентов в каналах"""
        print("\n🔍 Начинаем поиск потенциальных клиентов...")
        
        # Сначала ищем каналы
        all_channels = self.search_channels("продажа техника")
        if not all_channels:
            all_channels = ["Техника и гаджеты", "Купить-Продать"]
        
        leads = []
        
        for channel in all_channels[:channels_to_scan]:
            print(f"\n📡 Сканируем канал: {channel}")
            messages = self.read_messages(channel, limit=5)
            
            for msg in messages:
                score = self.calculate_intent(msg)
                if score > 30:
                    leads.append({
                        'channel': channel,
                        'message': msg[:200],
                        'score': score,
                        'source': 'web_telegram'
                    })
            
            time.sleep(2)
        
        return leads
    
    def calculate_intent(self, text):
        """Вычисление интента (готовности купить)"""
        score = 0
        text_lower = text.lower()
        
        # Ключевые слова товара
        product_keywords = [self.product, 'холодильник', 'морозильник', 'техника']
        for word in product_keywords:
            if word in text_lower:
                score += 15
                break
        
        # Слова покупки
        buy_words = ['купить', 'приобрести', 'заказать', 'нужен', 'ищу']
        for word in buy_words:
            if word in text_lower:
                score += 20
                break
        
        # Вопросы
        question_words = ['как', 'что', 'где', 'сколько', 'какой']
        for word in question_words:
            if word in text_lower and '?' in text:
                score += 10
                break
        
        return min(score, 100)
    
    def run(self):
        """Запуск программы"""
        print("=" * 50)
        print("🤖 Telegram Веб-Сканер")
        print("=" * 50)
        
        self.setup_driver()
        
        if not self.login_to_telegram():
            self.driver.quit()
            return
        
        # Ищем клиентов
        leads = self.search_leads(self.product)
        
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ПОИСКА")
        print("=" * 50)
        
        if leads:
            for i, lead in enumerate(leads, 1):
                print(f"\n{i}. 📌 Канал: {lead['channel']}")
                print(f"   💬 Сообщение: {lead['message']}")
                print(f"   🎯 Score: {lead['score']}%")
                print(f"   📱 Источник: {lead['source']}")
        else:
            print("\n❌ Клиенты не найдены")
        
        print("\n⏳ Программа завершена. Закройте браузер вручную или нажмите Enter...")
        input()
        
        self.driver.quit()

if __name__ == "__main__":
    import sys
    
    phone = "+79195260274"
    product = "холодильник"
    
    if len(sys.argv) > 1:
        phone = sys.argv[1]
    if len(sys.argv) > 2:
        product = sys.argv[2]
    
    reader = WebTelegramReader(phone, product)
    reader.run()

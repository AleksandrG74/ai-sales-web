#!/usr/bin/env python
"""
Тестовый скрипт для проверки всей системы
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Проверка здоровья оркестратора"""
    try:
        resp = requests.get(f"{BASE_URL}/api/orchestrator/health", timeout=5)
        if resp.status_code == 200:
            print("✅ Оркестратор работает")
            print(f"   Ответ: {resp.json()}")
            return True
        else:
            print(f"❌ Оркестратор вернул статус {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к оркестратору: {str(e)}")
        print("   Убедитесь, что бэкенд запущен: python backend/main.py")
        return False

def test_process_message():
    """Тест обработки сообщения"""
    print("\n--- Тест обработки сообщения ---")
    
    payload = {
        "user_id": "test_user_123",
        "username": "test_user",
        "message": "Здравствуйте! Я ищу хороший холодильник. Подскажите, какие у вас есть варианты?",
        "source": "telegram"
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/orchestrator/process_message",
            json=payload,
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Сообщение обработано")
            print(f"   Ответ: {data.get('response', '')[:100]}...")
            print(f"   Стратегия: {data.get('strategy_used', 'unknown')}")
            print(f"   Lead ID: {data.get('lead_id', 'N/A')}")
            return True
        else:
            print(f"❌ Ошибка: {resp.status_code}")
            print(f"   {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def test_create_lead():
    """Тест создания лида"""
    print("\n--- Тест создания лида ---")
    
    payload = {
        "user_id": "test_user_456",
        "username": "test_user2",
        "message": "Ищу холодильник с большим морозильником",
        "source": "telegram",
        "region": "Moscow",
        "intent": "buying",
        "intent_score": 80,
        "product": "Холодильник"
    }
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/orchestrator/create_lead",
            json=payload,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Лид создан")
            print(f"   Status: {data.get('status')}")
            print(f"   Lead ID: {data.get('lead_id')}")
            return True
        else:
            print(f"❌ Ошибка: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def test_web_ui():
    """Проверка веб-интерфейса"""
    print("\n--- Проверка веб-интерфейса ---")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        if resp.status_code == 200:
            print("✅ Веб-интерфейс доступен")
            print(f"   URL: {BASE_URL}")
            return True
        else:
            print(f"❌ Ошибка: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("🧪 Тестирование AI Sales Agent")
    print("=" * 50)
    print()
    
    # Проверяем веб-интерфейс
    test_web_ui()
    
    print()
    print("-" * 50)
    
    # Проверяем оркестратор
    if not test_health():
        print("\n⚠️ Убедитесь, что бэкенд запущен:")
        print("   python backend/main.py")
        sys.exit(1)
    
    print()
    print("-" * 50)
    
    # Тестируем обработку сообщения
    test_process_message()
    
    print()
    print("-" * 50)
    
    # Тестируем создание лида
    test_create_lead()
    
    print()
    print("=" * 50)
    print("✅ Тестирование завершено")
    print("=" * 50)
    print()
    print("🌐 Откройте в браузере: http://localhost:8000")
    print("📚 API документация: http://localhost:8000/docs")

if __name__ == "__main__":
    main()

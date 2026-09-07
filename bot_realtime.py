#!/usr/bin/env python
"""
Telegram бот для работы в реальном времени
Принимает и отправляет сообщения
"""

import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (уже есть в .env)
TOKEN = "8429143552:AAGh15qvJYQRu7sNuqFdgeHaA0SJu43vlsA"

# Создаём бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище для клиентов (в реальном проекте - БД)
clients = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Приветствие при команде /start"""
    await message.answer(
        "🤖 Привет! Я бот для поиска клиентов.\n\n"
        "📝 Просто напишите, что вы ищете, и я помогу!\n"
        "Например: 'Ищу холодильник' или 'Купить технику'"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Справка"""
    await message.answer(
        "📖 Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Эта справка\n"
        "/stats - Статистика\n"
        "/clients - Список клиентов\n\n"
        "💬 Просто напишите сообщение - я его обработаю!"
    )

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика"""
    stats = f"""
📊 Статистика бота:
• Всего клиентов: {len(clients)}
• Активных диалогов: {len([c for c in clients.values() if c.get('status') == 'active'])}
• Сообщений обработано: {sum(c.get('messages', 0) for c in clients.values())}
    """
    await message.answer(stats)

@dp.message(Command("clients"))
async def cmd_clients(message: Message):
    """Список клиентов"""
    if not clients:
        await message.answer("📭 Клиентов пока нет")
        return
    
    text = "📋 Список клиентов:\n\n"
    for i, (user_id, data) in enumerate(list(clients.items())[:10], 1):
        text += f"{i}. {data.get('name', user_id)} - Score: {data.get('score', 0)}%\n"
    
    await message.answer(text)

@dp.message()
async def handle_message(message: Message):
    """Обработка всех сообщений"""
    user_id = str(message.from_user.id)
    user_name = message.from_user.full_name
    text = message.text
    
    # Сохраняем клиента
    if user_id not in clients:
        clients[user_id] = {
            'name': user_name,
            'messages': 0,
            'status': 'new',
            'score': 0,
            'last_message': text,
            'first_seen': datetime.now().isoformat()
        }
    
    clients[user_id]['messages'] += 1
    clients[user_id]['last_message'] = text
    
    # Анализируем сообщение
    score = calculate_score(text)
    clients[user_id]['score'] = max(clients[user_id]['score'], score)
    
    # Определяем статус
    if score > 70:
        status = "🔥 Готов купить!"
        clients[user_id]['status'] = 'hot'
    elif score > 40:
        status = "🤔 Интересуется"
        clients[user_id]['status'] = 'warm'
    else:
        status = "❄️ Холодный"
        clients[user_id]['status'] = 'cold'
    
    # Отвечаем
    response = generate_response(text, score, status)
    await message.answer(response)
    
    # Логируем
    logger.info(f"📨 {user_name}: {text[:50]}... (Score: {score}%)")

def calculate_score(text):
    """Вычисляет Intent Score"""
    score = 0
    text_lower = text.lower()
    
    keywords = ["холодильник", "купить", "нужен", "ищу", "техника", "морозильник"]
    for kw in keywords:
        if kw in text_lower:
            score += 20
    
    buy_words = ['купить', 'приобрести', 'заказать', 'хочу', 'нужен']
    for word in buy_words:
        if word in text_lower:
            score += 15
    
    urgency = ['срочно', 'сегодня', 'завтра', 'быстро', 'сейчас']
    for word in urgency:
        if word in text_lower:
            score += 10
    
    return min(score, 100)

def generate_response(text, score, status):
    """Генерирует ответ"""
    if score > 70:
        return f"🔥 Отлично! Я вижу, вы заинтересованы! Напишите, что именно вас интересует? (Score: {score}%)"
    elif score > 40:
        return f"🤔 Интересно! Расскажите подробнее, что вы ищете? (Score: {score}%)"
    else:
        return f"👋 Здравствуйте! Чем могу помочь? (Score: {score}%)"

async def main():
    """Запуск бота"""
    logger.info("🚀 Бот запускается...")
    logger.info(f"📱 Бот: @sasa74bot")
    logger.info(f"🤖 Токен: {TOKEN[:10]}...")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен")

import asyncio
import logging
import os
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import aiohttp
import json
from dotenv import load_dotenv

# Добавляем путь к backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/telegram.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000/api/orchestrator/process_message")

if not BOT_TOKEN or BOT_TOKEN == "your-telegram-bot-token-here":
    logger.error("TELEGRAM_BOT_TOKEN not configured!")
    print("⚠️ Ошибка: TELEGRAM_BOT_TOKEN не задан в .env файле")
    print("   Получите токен у @BotFather в Telegram")
    sys.exit(1)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатуры
def get_main_keyboard():
    """Основная клавиатура"""
    buttons = [
        [KeyboardButton(text="📦 Каталог"), KeyboardButton(text="ℹ️ О нас")],
        [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    logger.info(f"User {message.from_user.id} started bot")
    
    welcome_text = (
        "👋 Здравствуйте! Я ваш виртуальный помощник по подбору товаров.\n\n"
        "Я помогу вам:\n"
        "• Найти идеальный товар\n"
        "• Ответить на вопросы\n"
        "• Подобрать оптимальные варианты\n\n"
        "Просто напишите, что вас интересует, и я помогу!"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🤖 Как я могу помочь?\n\n"
        "1️⃣ Напишите, что вы ищете\n"
        "2️⃣ Задайте вопрос о товаре\n"
        "3️⃣ Используйте кнопки для навигации\n\n"
        "Я всегда готов помочь!"
    )
    await message.answer(help_text)

@dp.message(lambda msg: msg.text in ["📦 Каталог", "ℹ️ О нас", "📞 Контакты", "❓ Помощь"])
async def handle_buttons(message: Message):
    """Обработчик кнопок"""
    responses = {
        "📦 Каталог": "📦 Наши товары:\n• Холодильники\n• Стиральные машины\n• Плиты\n• Мелкая техника\n\nУточните, что вас интересует?",
        "ℹ️ О нас": "ℹ️ Мы - современная компания по продаже бытовой техники.\n\n✅ Гарантия качества\n✅ Доступные цены\n✅ Быстрая доставка\n✅ Профессиональные консультации",
        "📞 Контакты": "📞 Свяжитесь с нами:\n\n📱 Телефон: +7 (900) 123-45-67\n✉️ Email: sales@example.com\n📍 Адрес: ул. Примерная, д. 123\n\n⏰ Режим работы: 9:00 - 21:00 ежедневно",
        "❓ Помощь": "❓ Часто задаваемые вопросы:\n\n• Как выбрать холодильник?\n• Какие гарантии?\n• Доставка и установка?\n• Способы оплаты?\n\nНапишите свой вопрос, и я отвечу!"
    }
    
    await message.answer(responses.get(message.text, "Я вас не понял. Пожалуйста, уточните."))

@dp.message()
async def handle_message(message: Message):
    """Обработка всех текстовых сообщений"""
    logger.info(f"Received message from {message.from_user.id}: {message.text[:50]}...")
    
    # Показываем индикатор набора
    await bot.send_chat_action(message.chat.id, "typing")
    
    # Отправляем в оркестратор
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": str(message.from_user.id),
            "username": message.from_user.username or message.from_user.full_name,
            "message": message.text,
            "source": "telegram"
        }
        
        try:
            async with session.post(
                ORCHESTRATOR_URL,
                json=payload,
                timeout=30
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data.get("response", "Извините, я не смог обработать запрос.")
                    await message.answer(response, reply_markup=get_main_keyboard())
                else:
                    error_text = await resp.text()
                    logger.error(f"Orchestrator error {resp.status}: {error_text}")
                    await message.answer(
                        "⚠️ Извините, сервер временно недоступен. Попробуйте позже.",
                        reply_markup=get_main_keyboard()
                    )
        except asyncio.TimeoutError:
            logger.error("Orchestrator timeout")
            await message.answer(
                "⏰ Сервер не отвечает. Попробуйте позже.",
                reply_markup=get_main_keyboard()
            )
        except aiohttp.ClientError as e:
            logger.error(f"Connection error: {str(e)}")
            await message.answer(
                "🔌 Ошибка соединения. Проверьте, запущен ли оркестратор.",
                reply_markup=get_main_keyboard()
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            await message.answer(
                "❌ Произошла ошибка. Пожалуйста, попробуйте позже.",
                reply_markup=get_main_keyboard()
            )

async def main():
    """Главная функция запуска бота"""
    logger.info("Starting Telegram Bot...")
    logger.info(f"Orchestrator URL: {ORCHESTRATOR_URL}")
    
    try:
        # Проверяем соединение с оркестратором
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/orchestrator/health", timeout=5) as resp:
                if resp.status == 200:
                    logger.info("✓ Orchestrator is available")
                else:
                    logger.warning("⚠️ Orchestrator returned status: " + str(resp.status))
    except:
        logger.warning("⚠️ Cannot connect to orchestrator. Make sure it's running.")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")

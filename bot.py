# bot.py
from aiogram import Bot, Dispatcher, Router
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN

# Включаем HTML‑парсинг по умолчанию
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
router = Router()
dp = Dispatcher()
dp.include_router(router)

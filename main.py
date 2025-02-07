# main.py
import asyncio
import logging
from bot import dp, bot
# Импортируем все обработчики, чтобы они зарегистрировались в роутере
import handlers.start
import handlers.admin
import handlers.chat_member

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.exception("Ошибка в polling. Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

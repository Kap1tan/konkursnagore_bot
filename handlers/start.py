# handlers/start.py
import logging
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import bot, router
from config import CHANNEL_ID, ADMIN_IDS
from data import referral_data, users_data
from utils import save_referral_data, save_users_data

async def register_user(user: types.User) -> bool:
    """
    Регистрирует пользователя, если его нет в файле.
    Если регистрация прошла успешно (новый пользователь), возвращает True,
    а также отправляет сообщение админам.
    """
    user_id = str(user.id)
    if user_id not in users_data:
        users_data[user_id] = {
            "username": user.username or user.full_name,
            "status": "active"
        }
        save_users_data(users_data)
        # Отправляем сообщение админам о регистрации нового пользователя
        message_text = (
            f"Зарегистрирован новый пользователь: "
            f"<a href='tg://user?id={user.id}'>{user.username or user.full_name}</a>"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, message_text)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения админу {admin_id}: {e}")
        return True
    return False

async def process_subscriber(chat: types.Chat, user: types.User) -> None:
    """
    Обрабатывает подписчика: создаёт или выдает реферальную ссылку.
    """
    user_id = user.id
    if str(user_id) in referral_data and referral_data[str(user_id)].get("invite_link"):
        invite_link = referral_data[str(user_id)]["invite_link"]
    else:
        try:
            invite = await bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                name=str(user_id),  # имя ссылки – ID пользователя
                expire_date=None,   # бессрочно
                member_limit=0      # без ограничения по количеству использований
            )
            invite_link = invite.invite_link
            referral_data[str(user_id)] = {
                "invite_link": invite_link,
                "count": 0,
                "username": user.username or user.full_name
            }
            save_referral_data(referral_data)
        except Exception as e:
            logging.error(f"Ошибка при создании ссылки для пользователя {user_id}: {e}")
            await bot.send_message(chat.id, "Ошибка при создании реферальной ссылки.")
            return

    await bot.send_message(
        chat.id,
        f"✅ <b>Ваша персональная реферальная ссылка:</b>\n\n"
        f"<code>{invite_link}</code>\n\n"
        f"Поделитесь ею с друзьями и приглашайте их в наш канал!"
    )

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    # Регистрируем пользователя и, если он новый – отправляем уведомление админам
    await register_user(message.from_user)
    text = (
        '<b>Добро пожаловать в "Конкурс на Горе"!</b>\n\n'
        "🏆 <b>Призы:</b>\n"
        "🥇 1 место: 500 грамм пыльцы и банка мёда\n"
        "🥈 2 место: 200 грамм пыльцы\n"
        "🥉 3 место: 100 грамм пыльцы\n"
        "🏅 4 место: купон на 15% скидку на любой продукт\n\n"
        "Нажмите кнопку ниже, чтобы <b>начать опыление</b> и получить вашу персональную реферальную ссылку."
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐝 начать опыление 🐝", callback_data="start_pollination")]
    ])
    await message.answer(text, reply_markup=inline_kb)

@router.message(Command("link"))
async def cmd_link(message: types.Message) -> None:
    await process_subscriber(message.chat, message.from_user)

@router.callback_query(F.data == "start_pollination")
async def callback_start_pollination(callback: types.CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except Exception as e:
        logging.error(f"Не удалось удалить сообщение: {e}")
    await process_subscriber(callback.message.chat, callback.from_user)

# handlers/admin.py
import os
import tempfile
import asyncio
import logging
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from bot import bot, router
from config import ADMIN_IDS
from data import referral_data, users_data
from utils import get_invite_word, save_referral_data

@router.message(Command("referrals"))
async def cmd_referrals(message: types.Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав для использования этой команды.")
        return

    sorted_refs = sorted(referral_data.items(), key=lambda item: item[1].get("count", 0), reverse=True)
    top4 = sorted_refs[:4]
    if not top4:
        text = "Топ рефералов отсутствует."
    else:
        text = "🏆 <b>Топ рефералов</b>:\n\n"
        rank = 1
        for user_id, info in top4:
            username = info.get("username", "Неизвестно")
            count = info.get("count", 0)
            text += f"{rank}. <a href='tg://user?id={user_id}'>{username}</a> — {count} {get_invite_word(count)}\n"
            rank += 1
    await message.answer(text)

@router.message(Command("admin"))
async def cmd_admin(message: types.Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет доступа к этой команде.")
        return
    total_users = len(users_data)
    active_users = sum(1 for u in users_data.values() if u.get("status") == "active")
    removed_users = sum(1 for u in users_data.values() if u.get("status") == "removed")
    admin_text = (
        "📊 <b>Админ панель</b>:\n\n"
        f"Всего пользователей: <b>{total_users}</b>\n"
        f"Активных пользователей: <b>{active_users}</b>\n"
        f"Удалили бота: <b>{removed_users}</b>\n\n"
        "Выберите действие:"
    )
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать всех рефералов", callback_data="download_referrals")],
        [InlineKeyboardButton(text="📋 Скачать всех юзеров", callback_data="download_users")],
        [InlineKeyboardButton(text="💬 Создать рассылку", callback_data="create_broadcast")]
    ])
    await message.answer(admin_text, reply_markup=inline_kb)

@router.callback_query(F.data == "download_referrals")
async def callback_download_referrals(callback: types.CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("У вас нет доступа.", show_alert=True)
        return
    lines = []
    for user_id, info in referral_data.items():
        username = info.get("username", "Неизвестно")
        count = info.get("count", 0)
        invite_link = info.get("invite_link", "")
        line = f"Имя: {username}, ID: {user_id}, Приглашено: {count} {get_invite_word(count)}, Ссылка: {invite_link}"
        lines.append(line)
    text_content = "\n".join(lines) if lines else "Статистика пуста."
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(text_content)
        tmp_path = tmp.name
    document = FSInputFile(tmp_path)
    await bot.send_document(
        chat_id=callback.from_user.id,
        document=document,
        caption="Статистика по рефералам"
    )
    os.remove(tmp_path)
    await callback.answer()

@router.callback_query(F.data == "download_users")
async def callback_download_users(callback: types.CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("У вас нет доступа.", show_alert=True)
        return
    lines = []
    for user_id, info in users_data.items():
        username = info.get("username", "Неизвестно")
        user_link = f"tg://user?id={user_id}"
        line = f"Имя: {username}, Ссылка: {user_link}"
        lines.append(line)
    text_content = "\n".join(lines) if lines else "Список пользователей пуст."
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(text_content)
        tmp_path = tmp.name
    document = FSInputFile(tmp_path)
    await bot.send_document(
        chat_id=callback.from_user.id,
        document=document,
        caption="Список всех пользователей"
    )
    os.remove(tmp_path)
    await callback.answer()

broadcast_mode = False

@router.callback_query(F.data == "create_broadcast")
async def callback_create_broadcast(callback: types.CallbackQuery) -> None:
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("У вас нет доступа.", show_alert=True)
        return
    global broadcast_mode
    broadcast_mode = True
    await callback.message.answer(
        "Отправьте сообщение, которое нужно разослать всем активным пользователям.\n\n"
        "<b>Поддерживаются:</b> \n"
        "- <b>Текст</b> (без форматирования)\n"
        "- <b>Фото</b> (С описанием,без форматирования)\n"
        "- <b>Видео</b> (С описанием,без форматирования)\n"
        "- <b>Документ</b> (С описанием,без форматирования)\n"
        "- <b>Аудио</b> (С описанием,без форматирования)\n"
        "- <b>Голосовое сообщение</b> (С описанием,без форматирования)\n"
        "- <b>Видеосообщение</b>"
    )
    await callback.answer()

@router.message()
async def handle_broadcast(message: types.Message) -> None:
    global broadcast_mode
    if message.from_user.id not in ADMIN_IDS or not broadcast_mode:
        return
    count = 0
    for user_id, info in users_data.items():
        if info.get("status") == "active":
            try:
                if message.photo:
                    photo_id = message.photo[-1].file_id
                    await bot.send_photo(chat_id=int(user_id), photo=photo_id, caption=message.caption or "")
                elif message.video:
                    await bot.send_video(chat_id=int(user_id), video=message.video.file_id,
                                         caption=message.caption or "")
                elif message.document:
                    await bot.send_document(chat_id=int(user_id), document=message.document.file_id,
                                            caption=message.caption or "")
                elif message.audio:
                    await bot.send_audio(chat_id=int(user_id), audio=message.audio.file_id,
                                         caption=message.caption or "")
                elif message.voice:
                    await bot.send_voice(chat_id=int(user_id), voice=message.voice.file_id,
                                         caption=message.caption or "")
                elif message.video_note:
                    await bot.send_video_note(chat_id=int(user_id), video_note=message.video_note.file_id)
                else:
                    await bot.send_message(chat_id=int(user_id), text=message.text)
                count += 1
                await asyncio.sleep(0.05)  # небольшая задержка для обхода лимитов
            except Exception as e:
                logging.error(f"Ошибка при рассылке пользователю {user_id}: {e}")
    await message.answer(f"Рассылка отправлена {count} пользователям.")
    broadcast_mode = False

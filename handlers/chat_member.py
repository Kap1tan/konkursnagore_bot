# handlers/chat_member.py
import logging
from aiogram import types
from bot import bot, router
from data import users_data, referral_data, credited_referrals, save_credited_referrals
from utils import save_users_data, save_referral_data
from config import CHANNEL_ID

@router.my_chat_member()
async def on_my_chat_member(update: types.ChatMemberUpdated) -> None:
    if update.chat.type != "private":
        return
    user_id = str(update.chat.id)
    if update.new_chat_member.status in ["kicked", "left"]:
        if user_id in users_data:
            users_data[user_id]["status"] = "removed"
            save_users_data(users_data)
            logging.info(f"Пользователь {user_id} удалил бота.")

@router.chat_member()
async def on_chat_member_update(update: types.ChatMemberUpdated) -> None:
    if update.chat.id != CHANNEL_ID:
        return
    if update.invite_link is None:
        return
    if update.new_chat_member.status != "member":
        return
    ref_name = update.invite_link.name
    if not ref_name:
        return
    try:
        referrer_id = str(int(ref_name))
    except ValueError:
        return

    new_user_id = str(update.new_chat_member.user.id)
    # Если пользователь уже был засчитан – выходим без начисления
    if new_user_id in credited_referrals:
        return

    # Засчитываем пользователя – добавляем его ID в список засчитанных
    credited_referrals.add(new_user_id)
    save_credited_referrals()

    if referrer_id in referral_data:
        referral_data[referrer_id]["count"] += 1
    else:
        referral_data[referrer_id] = {
            "invite_link": "",
            "count": 1,
            "username": ""
        }
    save_referral_data(referral_data)
    logging.info(f"Пользователь по ссылке {referrer_id} пригласил нового участника (user_id: {new_user_id}).")

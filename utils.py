# utils.py
import os
import json
import logging
from config import REFERRALS_FILE, USERS_FILE

def load_json_data(filename: str) -> dict:
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logging.error(f"Ошибка чтения файла {filename}: {e}")
            data = {}
    else:
        data = {}
    return data

def save_json_data(filename: str, data: dict) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка записи в файл {filename}: {e}")

def load_referral_data() -> dict:
    return load_json_data(REFERRALS_FILE)

def save_referral_data(data: dict) -> None:
    save_json_data(REFERRALS_FILE, data)

def load_users_data() -> dict:
    return load_json_data(USERS_FILE)

def save_users_data(data: dict) -> None:
    save_json_data(USERS_FILE, data)

def get_invite_word(count: int) -> str:
    return "приглашенный" if count == 1 else "приглашенных"

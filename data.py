# data.py
from utils import load_referral_data, load_users_data, load_json_data, save_json_data
from config import CREDITED_REFERRALS_FILE

referral_data = load_referral_data()
users_data = load_users_data()

# Загружаем список пользователей, для которых уже был засчитан реферал,
# и преобразуем его в множество для быстрого поиска.
credited_data = load_json_data(CREDITED_REFERRALS_FILE)
credited_referrals = set(credited_data.get("credited", []))

def save_credited_referrals():
    from utils import save_json_data
    save_json_data(CREDITED_REFERRALS_FILE, {"credited": list(credited_referrals)})

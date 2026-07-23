import time
from datetime import datetime, date

def give_daily_bonus(user_id, user_data_dict):
    today = date.today().isoformat()
    if user_data_dict.get("last_daily") != today:
        user_data_dict["balance"] += 100
        user_data_dict["last_daily"] = today
        return True, user_data_dict
    return False, user_data_dict

def can_spin(user_data):
    if user_data.get("status") == "ban":
        return False
    current_time = time.time()
    last_spin = user_data.get("last_spin", 0.0)
    upgrade_level = user_data.get("upgrade_level", 0)
    cooldown = 10 - (upgrade_level * 0.25)
    return current_time - last_spin >= cooldown

def get_remaining_cooldown(user_data):
    current_time = time.time()
    last_spin = user_data.get("last_spin", 0.0)
    upgrade_level = user_data.get("upgrade_level", 0)
    cooldown = 10 - (upgrade_level * 0.25)
    remaining = cooldown - (current_time - last_spin)
    return max(0, remaining)

def calculate_win(dice_value: int, multiplier_level: int = 0) -> int:
    # Комбинации авто-выигрышей на слот-машине Telegram: 1, 22, 43, 64
    win_values = {1: 20, 22: 40, 43: 60, 64: 100}
    
    base_win = win_values.get(dice_value, 0)
    
    # Дополнительно даем за "почти выигрышные" комбинации
    if base_win == 0 and dice_value in [7, 11, 18, 33, 55]:
        base_win = 15
        
    if base_win > 0:
        multiplier = 1 + (multiplier_level * 0.1)
        return int(base_win * multiplier)
    return 0

def get_win_text(win_amount: int, current_balance: int) -> str:
    return f"🎉 Выигрыш! Вы получили {win_amount} баллов!\n💎 Ваш баланс: {current_balance} баллов."

def is_within_referral_period(referral_date_str):
    """Проверяет, прошло ли менее 3 дней с момента регистрации по рефералу"""
    if not referral_date_str:
        return False
    try:
        ref_date = datetime.strptime(referral_date_str, "%Y-%m-%d").date()
        today = date.today()
        return (today - ref_date).days <= 3
    except Exception:
        return False

def calculate_referral_bonus(win_amount, referrer_id, referral_date_str):
    """Вычисляет реферальный бонус (10%)"""
    if not referrer_id or not referral_date_str:
        return 0
    if is_within_referral_period(referral_date_str):
        return max(1, int(win_amount * 0.1))
    return 0
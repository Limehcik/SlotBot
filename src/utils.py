from functools import wraps
import time
from datetime import datetime, date
from aiogram import types

from database import get_user

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
    """ Рассчитывает выигрыш для Telegram Slot Machine (dice_value от 1 до 64). """
    
    # 1. Три семерки (777) - Максимальный джекпот (dice_value = 64)
    if dice_value == 64:
        base_win = 3000

    # 2. Три одинаковых символа (BAR, Ягода, Лимон)
    elif dice_value in (1, 22, 43):
        base_win = 500

    # 3. Две семерки (7-7-X, 7-X-7, X-7-7)
    elif dice_value in (16, 32, 48, 52, 56, 60, 61, 62, 63, 49, 50, 51):
        base_win = 150

    # 4. Две пары обычных символов (BAR-BAR-X, Лимон-Лимон-X и т.д.)
    elif dice_value in (
        2, 3, 4, 5, 9, 13, 17, 21, 23, 24, 25, 29, 33, 37, 41, 42, 44, 45, 
        6, 11, 26, 31, 46, 57, 7, 10, 27, 30, 47, 58, 8, 12, 28, 34, 38, 59
    ):
        base_win = 50

    # 5. Проигрышные комбинации (все символы разные)
    else:
        base_win = 0

    # Расчет множителя (multiplier_level = 1 дает +10%, 2 -> +20% и т.д.)
    if base_win > 0:
        multiplier = 1.0 + (multiplier_level * 0.1)
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

def admin_only(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        user_id = str(message.from_user.id)
        admin_data = get_user(user_id)
        
        if admin_data.get("status") != "admin":
            await message.answer("❌ Недостаточно прав!")
            return
            
        return await func(message, *args, **kwargs)
        
    return wrapper
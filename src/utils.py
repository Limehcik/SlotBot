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

def calculate_multiplier(dice_value: int, multiplier_level: int = 0) -> int:
    """
    Рассчитывает выигрыш для Telegram Slot Machine (dice_value от 1 до 64).
    
    Символы Telegram Casino (0-3):
    0 = BAR
    1 = Вишня (Ягода)
    2 = Лимон
    3 = Семерка (7)
    """
    if not (1 <= dice_value <= 64):
        return 0

    # Преобразуем dice_value (1-64) в значения трех барабанов (каждый от 0 до 3)
    val = dice_value - 1
    right = val % 4
    center = (val // 4) % 4
    left = val // 16

    reels = (left, center, right)

    # 1. Три семерки (777) — x300
    if reels == (3, 3, 3):
        return 300.0

    # 2. Три одинаковых обычных символа (BAR, Вишня, Лимон) — x50
    elif left == center == right:
        return 50.0

    # 3. Две семерки (7-7-X, 7-X-7, X-7-7) — x15
    elif reels.count(3) == 2:
        return 15.0

    # 4. Две пары / пара любых обычных символов — x5
    elif left == center or left == right or center == right:
        return 5.0

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
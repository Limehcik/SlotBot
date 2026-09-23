from aiogram import types, F
from aiogram.filters import Command
import asyncio
import time
from datetime import date, datetime

from database import get_user, update_user, find_user_by_referral_code
from keyboards import create_reply_keyboard, create_slots_keyboard
from utils import give_daily_bonus, can_spin, get_remaining_cooldown, calculate_multiplier, get_win_text, calculate_referral_bonus

async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or ""
    
    # Проверяем, есть ли юзер ДО вызова get_user
    # Чтобы понять, новый он или нет
    import sqlite3
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    conn.close()
    
    is_new_user = not exists
    user_data = get_user(user_id, username)
    
    referral_code = None
    parts = message.text.split()
    if len(parts) > 1:
        referral_code = parts[1]
        
    if referral_code and is_new_user:
        referrer_id = find_user_by_referral_code(referral_code)
        
        if referrer_id and referrer_id != user_id:
            today_str = date.today().isoformat()
            update_user(user_id, {
                "referred_by": referrer_id,
                "referral_date": today_str
            })
            
            # Обновляем счетчик пригласившего
            referrer = get_user(referrer_id)
            update_user(referrer_id, {
                "referrals_count": referrer.get("referrals_count", 0) + 1
            })
            
            try:
                await message.bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 По вашей реферальной ссылке зарегистрировался новый пользователь (@{username if username else user_id})!"
                )
            except Exception:
                pass

    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n"
        f"🎰 Добро пожаловать в симулятор слотов!\n"
        f"💎 Вам начислено 500 стартовых баллов.\n\n"
        f"Жмите кнопку ниже, чтобы начать игру!",
        reply_markup=create_reply_keyboard()
    )

async def spin_slots(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    if user_data.get("status") == "ban":
        await message.answer("❌ Вы забанены админом!")
        return
        
    if not can_spin(user_data):
        rem = get_remaining_cooldown(user_data)
        await message.answer(f"⏳ Подождите еще {rem:.1f} сек перед следующей прокруткой!")
        return
        
    if user_data["balance"] < user_data.get("current_bet", 10):
        await message.answer("❌ Недостаточно баллов для прокрутки! Уменьшите ставку.")
        return
        
    # Списываем ставку
    update_user(user_id, {
        "balance": user_data["balance"] - user_data.get("current_bet", 10),
        "last_spin": time.time(),
        "total_spins": user_data.get("total_spins", 0) + 1
    })
    
    msg = await message.answer_dice(emoji="🎰")
    dice_value = msg.dice.value
    
    await asyncio.sleep(2.0)
    
    # Свежие данные после списания
    user_data = get_user(user_id)

    combo_mult = calculate_multiplier(dice_value)
    
    # 2. Учитываем прокачку пользователя (level 1 = +10% к выигрышу и т.д.)
    user_mult_level = user_data.get("multiplier_level", 0)
    perk_mult = 1.0 + (user_mult_level * 0.1)

    # 3. Итоговый выигрыш = ставка * комбинация * прокачка
    win_amount = int(user_data.get("current_bet", 10) * combo_mult * perk_mult)
    
    user_updates = {}
    if win_amount > 0:
        user_updates["balance"] = user_data["balance"] + win_amount
        user_updates["total_wins"] = user_data.get("total_wins", 0) + 1
        update_user(user_id, user_updates)
        
        # Начисление реферального бонуса пригласителю
        ref_bonus = calculate_referral_bonus(win_amount, user_data.get("referred_by"), user_data.get("referral_date"))
        if ref_bonus > 0:
            ref_id = user_data["referred_by"]
            referrer = get_user(ref_id)
            update_user(ref_id, {
                "balance": referrer["balance"] + ref_bonus,
                "referral_bonus": referrer.get("referral_bonus", 0) + ref_bonus
            })
            try:
                await message.bot.send_message(ref_id, f"👥 Реферальный бонус! Вы получили {ref_bonus} баллов от игры вашего друга (@{user_data['username']})!")
            except Exception: pass
            
        await message.answer(get_win_text(win_amount, get_user(user_id)["balance"]))
    else:
        await message.answer(f"😢 Вы ничего не выиграли.\n💎 Остаток баланса: {user_data['balance']} баллов.")

async def daily_bonus_handler(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    success, updated_data = give_daily_bonus(user_id, user_data)
    if success:
        update_user(user_id, {
            "balance": updated_data["balance"],
            "last_daily": updated_data["last_daily"]
        })
        await message.answer("🎁 Вы получили ежедневный бонус 100 баллов!\n💎 Ваш баланс увеличен.")
    else:
        await message.answer("❌ Вы уже забирали бонус сегодня! Приходите завтра.")

async def show_stats(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    total_spins = user_data.get("total_spins", 0)
    total_wins = user_data.get("total_wins", 0)
    win_rate = (total_wins / total_spins * 100) if total_spins > 0 else 0
    
    mult_level = user_data.get("multiplier_level", 0)
    multiplier = 1 + (mult_level * 0.1)
    bot_info = await message.bot.get_me()
    
    await message.answer(
        f"📈 *Ваша статистика:*\n\n"
        f"🎰 Всего прокруток: {total_spins}\n"
        f"🎉 Успешных спинов: {total_wins}\n"
        f"📈 Процент выигрышей: {win_rate:.1f}%\n"
        f"🔧 Уровень скорости: {user_data.get('upgrade_level', 0)}\n"
        f"💰 Уровень множителя: {mult_level} (x{multiplier:.1f})\n"
        f"💎 Баланс: {user_data['balance']} баллов\n\n"
        f"🔗 Реферальная ссылка:\n"
        f"https://t.me/{bot_info.username}?start={user_data.get('referral_code')}",
        reply_markup=create_reply_keyboard(),
        parse_mode="Markdown"
    )

async def show_menu(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    cooldown = 10 - (user_data.get("upgrade_level", 0) * 0.25)
    multiplier = 1 + (user_data.get("multiplier_level", 0) * 0.1)
    
    await message.answer(
        f"🎰 *Меню слотов*\n"
        f"💎 Баланс: {user_data['balance']} баллов\n\n"
        f"⏱️ Кулдаун крутки: {cooldown:.2f} сек\n"
        f"📈 Множитель выигрыша: x{multiplier:.1f}",
        reply_markup=create_reply_keyboard(),
        parse_mode="Markdown"
    )

async def show_slots_menu(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user(user_id)
    current_bet = user_data.get("current_bet", 10)
    balance = user_data.get("balance", 0)
    
    await message.answer(
        f"🎰 **Режим игры в Слоты**\n\n"
        f"💰 Ваш баланс: `{balance}` баллов\n"
        f"🎯 Текущая ставка: `{current_bet}` баллов\n\n"
        f"Регулируйте ставку кнопками ниже и крутите!",
        reply_markup=create_slots_keyboard(current_bet, balance),
        parse_mode="Markdown"
    )

async def process_bet_but(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    balance = user_data.get("balance", 0)
    current_bet = user_data.get("current_bet", 10)
    text = message.text

    # Логика изменения ставки
    if text == "-50k": new_bet = current_bet - 50000
    elif text == "-1k": new_bet = current_bet - 1000
    elif text == "-100": new_bet = current_bet - 100
    elif text == "+100": new_bet = current_bet + 100
    elif text == "+1k": new_bet = current_bet + 1000
    elif text == "+50k": new_bet = current_bet + 50000
    elif text == "-1M": new_bet = current_bet - 1000000
    elif text == "+1M": new_bet = current_bet + 1000000
    elif text == "MIN(10)": new_bet = 10
    elif text == f"1/2 ({balance // 2})": new_bet = max(10, balance // 2)
    elif text == f"MAX({balance})": new_bet = max(10, balance)
    else: new_bet = current_bet

    # Ограничения (от 10 до текущего баланса)
    new_bet = max(10, min(new_bet, balance if balance >= 10 else 10))

    update_user(user_id, {"current_bet": new_bet})

    # Переотправляем клавиатуру с обновленной суммой на кнопке "Крутить"
    await message.answer(
        f"Ваша ставка изменена на: **{new_bet:,}** баллов.",
        reply_markup=create_slots_keyboard(new_bet, balance),
        parse_mode="Markdown"
    )
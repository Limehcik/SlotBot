from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import asyncio
import time
from datetime import date, datetime

from database import get_user, update_user, load_user_data
from keyboards import create_reply_keyboard, create_cancel_keyboard
from utils import give_daily_bonus, can_spin, get_remaining_cooldown, calculate_win, get_win_text

async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or ""
    
    user_data = get_user(user_id, username)
    upgrade_level = user_data.get("upgrade_level", 0)
    multiplier_level = user_data.get("multiplier_level", 0)
    cooldown = 10 - (upgrade_level * 0.25)
    multiplier = 1 + (multiplier_level * 0.1)
    
    await message.answer(
        f"🎰 Добро пожаловать в слоты!\n💎 Баланс: {user_data['balance']} баллов\n\n"
        f"⚡ Текущая скорость: {cooldown:.2f} сек между вращениями\n"
        f"💰 Текущий множитель: x{multiplier:.1f}\n"
        f"🔧 Уровень скорости: {upgrade_level}\n"
        f"💎 Уровень множителя: {multiplier_level}\n\n"
        "🎰 Крути слоты - ставка 10 баллов\n"
        "🎁 Ежедневный бонус - 100 баллов каждый день\n"
        "⚡ Улучшить скорость - уменьшить время ожидания\n"
        "💰 Улучшить множитель - увеличить выигрыши",
        reply_markup=create_reply_keyboard()
    )

async def spin_slots(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or ""
    
    user_data = get_user(user_id, username)
    
    if user_data.get("status") == "ban":
        await message.answer("❌ Вы забанены и не можете играть!")
        return
    
    if not can_spin(user_data):
        remaining = get_remaining_cooldown(user_data)
        await message.answer(
            f"⏳ Подождите еще {remaining:.1f} секунд перед следующим вращением!",
            reply_markup=create_reply_keyboard()
        )
        return
    
    if user_data["balance"] < 10:
        await message.answer("❌ Недостаточно баллов! Минимальная ставка: 10 баллов\n\n🎁 Получи ежедневный бонус или жди завтра")
        return
    
    # Обновляем данные пользователя
    updates = {
        "balance": user_data["balance"] - 10,
        "last_spin": time.time(),
        "total_spins": user_data.get("total_spins", 0) + 1
    }
    update_user(user_id, updates)
    
    dice_message = await message.answer_dice(emoji="🎰")
    await asyncio.sleep(2)
    
    dice_value = dice_message.dice.value
    multiplier_level = user_data.get("multiplier_level", 0)
    win_amount = calculate_win(dice_value, multiplier_level)
    
    # Обновляем баланс и статистику выигрышей
    new_updates = {
        "balance": updates["balance"] + win_amount
    }
    if win_amount > 0:
        new_updates["total_wins"] = user_data.get("total_wins", 0) + 1
    
    update_user(user_id, new_updates)
    
    result_text = get_win_text(win_amount)
    await message.answer(
        f"{result_text}\n💎 Баланс: {updates['balance'] + win_amount} баллов",
        reply_markup=create_reply_keyboard()
    )

async def daily_bonus(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    if user_data.get("status") == "ban":
        await message.answer("❌ Вы забанены и не можете получать бонусы!")
        return
        
    success, updated_data = give_daily_bonus(user_id, user_data)
    
    if success:
        update_user(user_id, updated_data)
        await message.answer(f"🎁 Получен ежедневный бонус: 100 баллов!\n💎 Баланс: {updated_data['balance']} баллов", 
                           reply_markup=create_reply_keyboard())
    else:
        today = date.today()
        last_date = datetime.strptime(user_data["last_daily"], "%Y-%m-%d").date()
        next_date = last_date.replace(day=last_date.day + 1)
        await message.answer(f"❌ Бонус уже получен сегодня!\n🎁 Следующий бонус: {next_date.strftime('%d.%m.%Y')}", 
                           reply_markup=create_reply_keyboard())

async def show_stats(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    total_spins = user_data.get("total_spins", 0)
    total_wins = user_data.get("total_wins", 0)
    win_rate = (total_wins / total_spins * 100) if total_spins > 0 else 0
    
    multiplier_level = user_data.get("multiplier_level", 0)
    multiplier = 1 + (multiplier_level * 0.1)
    
    await message.answer(
        f"📊 Статистика игры:\n\n"
        f"🎰 Всего вращений: {total_spins}\n"
        f"🎯 Выигрышных спинов: {total_wins}\n"
        f"📈 Процент выигрышей: {win_rate:.1f}%\n"
        f"🔧 Уровень скорости: {user_data.get('upgrade_level', 0)}\n"
        f"💰 Уровень множителя: {multiplier_level} (x{multiplier:.1f})\n"
        f"💎 Баланс: {user_data.get('balance', 500)} баллов",
        reply_markup=create_reply_keyboard()
    )

async def show_menu(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or ""
    
    user_data = get_user(user_id, username)
    upgrade_level = user_data.get("upgrade_level", 0)
    multiplier_level = user_data.get("multiplier_level", 0)
    cooldown = 10 - (upgrade_level * 0.25)
    multiplier = 1 + (multiplier_level * 0.1)
    
    await message.answer(
        f"🎰 Меню слотов\n💎 Баланс: {user_data['balance']} баллов\n\n"
        f"⚡ Текущая скорость: {cooldown:.2f} сек между вращениями\n"
        f"💰 Текущий множитель: x{multiplier:.1f}\n"
        f"🔧 Уровень скорости: {upgrade_level}\n"
        f"💎 Уровень множителя: {multiplier_level}\n\n"
        "🎰 Крути слоты - ставка 10 баллов\n"
        "🎁 Ежедневный бонус - 100 баллов каждый день\n"
        "⚡ Улучшить скорость - уменьшить время ожидания\n"
        "💰 Улучшить множитель - увеличить выигрыши",
        reply_markup=create_reply_keyboard()
    )
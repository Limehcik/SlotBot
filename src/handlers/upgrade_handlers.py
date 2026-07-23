from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import get_user, update_user
from keyboards import create_upgrade_keyboard
from utils import calculate_win

async def upgrade_speed(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    upgrade_level = user_data.get("upgrade_level", 0)
    upgrade_cost = user_data.get("upgrade_cost", 500)
    balance = user_data["balance"]
    current_cooldown = 10 - (upgrade_level * 0.25)
    new_cooldown = 10 - ((upgrade_level + 1) * 0.25)
    
    keyboard = create_upgrade_keyboard("speed", upgrade_cost)
    
    await message.answer(
        f"⚡ Улучшение скорости\n\n"
        f"🔧 Текущий уровень: {upgrade_level}\n"
        f"⏱️ Текущее время ожидания: {current_cooldown:.2f} сек\n"
        f"⏱️ Новое время ожидания: {new_cooldown:.2f} сек\n"
        f"💰 Стоимость улучшения: {upgrade_cost} баллов\n"
        f"💎 Ваш баланс: {balance} баллов",
        reply_markup=keyboard
    )

async def upgrade_multiplier(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    multiplier_level = user_data.get("multiplier_level", 0)
    multiplier_cost = user_data.get("multiplier_cost", 1000)
    balance = user_data["balance"]
    current_multiplier = 1 + (multiplier_level * 0.1)
    new_multiplier = 1 + ((multiplier_level + 1) * 0.1)
    
    # Пример выигрышей для демонстрации
    example_win_current = calculate_win(1, multiplier_level)  # Джекпот
    example_win_new = calculate_win(1, multiplier_level + 1)
    
    keyboard = create_upgrade_keyboard("multiplier", multiplier_cost)
    
    await message.answer(
        f"💰 Улучшение множителя\n\n"
        f"💎 Текущий уровень: {multiplier_level}\n"
        f"📈 Текущий множитель: x{current_multiplier:.1f}\n"
        f"📈 Новый множитель: x{new_multiplier:.1f}\n\n"
        f"🎯 Пример выигрыша:\n"
        f"• Сейчас: {example_win_current} баллов\n"
        f"• После улучшения: {example_win_new} баллов\n\n"
        f"💰 Стоимость улучшения: {multiplier_cost} баллов\n"
        f"💎 Ваш баланс: {balance} баллов",
        reply_markup=keyboard
    )

async def buy_upgrade(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    data_parts = callback.data.split("_")
    upgrade_type = data_parts[1]
    cost = int(data_parts[2])
    
    user_data = get_user(user_id)
    
    if user_data["balance"] < cost:
        await callback.answer("❌ Недостаточно баллов!", show_alert=True)
        return
    
    updates = {
        "balance": user_data["balance"] - cost
    }
    
    if upgrade_type == "speed":
        updates["upgrade_level"] = user_data.get("upgrade_level", 0) + 1
        updates["upgrade_cost"] = int(cost * 1.8)
        new_cooldown = 10 - (updates["upgrade_level"] * 0.25)
        
        update_user(user_id, updates)
        await callback.message.edit_text(
            f"⚡ Улучшение скорости приобретено!\n\n"
            f"🔧 Новый уровень: {updates['upgrade_level']}\n"
            f"⏱️ Новое время ожидания: {new_cooldown:.2f} сек\n"
            f"💎 Следующее улучшение: {updates['upgrade_cost']} баллов\n"
            f"💰 Остаток баланса: {updates['balance']} баллов"
        )
    
    elif upgrade_type == "multiplier":
        updates["multiplier_level"] = user_data.get("multiplier_level", 0) + 1
        updates["multiplier_cost"] = int(cost * 2.0)
        new_multiplier = 1 + (updates["multiplier_level"] * 0.1)
        
        update_user(user_id, updates)
        await callback.message.edit_text(
            f"💰 Улучшение множителя приобретено!\n\n"
            f"💎 Новый уровень: {updates['multiplier_level']}\n"
            f"📈 Новый множитель: x{new_multiplier:.1f}\n"
            f"💎 Следующее улучшение: {updates['multiplier_cost']} баллов\n"
            f"💰 Остаток баланса: {updates['balance']} баллов"
        )
    
    await callback.answer()
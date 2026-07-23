from aiogram import types
from database import get_user, update_user
from keyboards import create_upgrade_keyboard

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
        f"⚡ *Улучшение скорости*\n\n"
        f"🔧 Текущий уровень: {upgrade_level}\n"
        f"⏱️ Текущее время ожидания: {current_cooldown:.2f} сек\n"
        f"⏱️ Новое время ожидания: {new_cooldown:.2f} сек\n"
        f"💰 Стоимость улучшения: {upgrade_cost} баллов\n"
        f"💎 Ваш баланс: {balance} баллов",
        reply_markup=keyboard, parse_mode="Markdown"
    )

async def upgrade_multiplier(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    mult_level = user_data.get("multiplier_level", 0)
    mult_cost = user_data.get("multiplier_cost", 1000)
    balance = user_data["balance"]
    
    keyboard = create_upgrade_keyboard("multiplier", mult_cost)
    await message.answer(
        f"💰 *Улучшение множителя*\n\n"
        f"🔧 Текущий уровень: {mult_level} (x{1 + mult_level*0.1:.1f})\n"
        f"📈 Новый множитель: x{1 + (mult_level+1)*0.1:.1f}\n"
        f"💰 Стоимость улучшения: {mult_cost} баллов\n"
        f"💎 Ваш баланс: {balance} баллов",
        reply_markup=keyboard, parse_mode="Markdown"
    )

async def buy_upgrade(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = get_user(user_id)
    
    parts = callback.data.split("_")
    upgrade_type = parts[1]
    cost = int(parts[2])
    
    if user_data["balance"] < cost:
        await callback.answer("❌ Недостаточно баллов!", show_alert=True)
        return
        
    updates = {"balance": user_data["balance"] - cost}
    
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
            f"🔧 Новый уровень: {updates['multiplier_level']} (x{new_multiplier:.1f})\n"
            f"💎 Следующее улучшение: {updates['multiplier_cost']} баллов\n"
            f"残 Остаток баланса: {updates['balance']} баллов"
        )
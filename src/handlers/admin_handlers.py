from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import load_user_data, save_user_data, get_user, update_user
from keyboards import create_reply_keyboard, create_cancel_keyboard
from utils import find_user_by_username, convert_entities_to_html

logger = logging.getLogger(__name__)

class BroadcastState(StatesGroup):
    waiting_for_message = State()

async def ban_user(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: /ban @username или /ban user_id")
            return
        
        target = parts[1].replace('@', '')
        
        if target.isdigit():
            target_user_id = target
        else:
            target_user_id = find_user_by_username(target, user_data)
        
        if not target_user_id or target_user_id not in user_data:
            await message.answer("❌ Пользователь не найден!")
            return
        
        if user_data[target_user_id].get("status") == "admin":
            await message.answer("❌ Нельзя забанить администратора!")
            return
        
        user_data[target_user_id]["status"] = "ban"
        save_user_data(user_data)
        
        username = user_data[target_user_id].get("username", "без username")
        await message.answer(f"✅ Пользователь @{username} забанен!")
        
    except Exception as e:
        logger.error(f"Error in ban_user: {e}")
        await message.answer("❌ Ошибка при выполнении команды")

async def unban_user(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Использование: /unban @username или /unban user_id")
            return
        
        target = parts[1].replace('@', '')
        
        if target.isdigit():
            target_user_id = target
        else:
            target_user_id = find_user_by_username(target, user_data)
        
        if not target_user_id or target_user_id not in user_data:
            await message.answer("❌ Пользователь не найден!")
            return
        
        user_data[target_user_id]["status"] = "norm"
        save_user_data(user_data)
        
        username = user_data[target_user_id].get("username", "без username")
        await message.answer(f"✅ Пользователь @{username} разбанен!")
        
    except Exception as e:
        logger.error(f"Error in unban_user: {e}")
        await message.answer("❌ Ошибка при выполнении команды")

async def give_points(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ Использование: /give @username amount или /give user_id amount")
            return
        
        target = parts[1].replace('@', '')
        amount = int(parts[2])
        
        if target.isdigit():
            target_user_id = target
        else:
            target_user_id = find_user_by_username(target, user_data)
        
        if not target_user_id:
            target_user_id = target
            if target_user_id not in user_data:
                user_data[target_user_id] = {
                    "balance": 500, 
                    "last_daily": "",
                    "last_spin": 0,
                    "upgrade_level": 0,
                    "multiplier_level": 0,
                    "upgrade_cost": 500,
                    "multiplier_cost": 1000,
                    "total_spins": 0,
                    "total_wins": 0,
                    "status": "norm",
                    "username": target if not target.isdigit() else ""
                }
        
        user_data[target_user_id]["balance"] += amount
        save_user_data(user_data)
        
        username = user_data[target_user_id].get("username", "без username")
        await message.answer(f"✅ Выдано {amount} баллов пользователю @{username}")
        
    except (IndexError, ValueError) as e:
        logger.error(f"Error in give_points: {e}")
        await message.answer("❌ Использование: /give @username amount")

async def take_points(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ Использование: /take @username amount или /take user_id amount")
            return
        
        target = parts[1].replace('@', '')
        amount = int(parts[2])
        
        if target.isdigit():
            target_user_id = target
        else:
            target_user_id = find_user_by_username(target, user_data)
        
        if not target_user_id or target_user_id not in user_data:
            await message.answer("❌ Пользователь не найден!")
            return
        
        if user_data[target_user_id]["balance"] < amount:
            amount = user_data[target_user_id]["balance"]
        
        user_data[target_user_id]["balance"] -= amount
        save_user_data(user_data)
        
        username = user_data[target_user_id].get("username", "без username")
        await message.answer(f"✅ Изъято {amount} баллов у пользователя @{username}")
        
    except (IndexError, ValueError) as e:
        logger.error(f"Error in take_points: {e}")
        await message.answer("❌ Использование: /take @username amount")

async def message_command(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    cancel_keyboard = create_cancel_keyboard()
    
    await message.answer("📨 Напишите сообщение для рассылки всем пользователям:", reply_markup=cancel_keyboard)
    await state.set_state(BroadcastState.waiting_for_message)

async def save_to_cloud_cmd(message: types.Message):
    """Сохраняет локальные данные в облако"""
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        from database import save_to_cloud
        success, result_msg = save_to_cloud()
        await message.answer(result_msg)
        
    except Exception as e:
        logger.error(f"Error in save_to_cloud: {e}")
        await message.answer(f"❌ Ошибка: {e}")

async def load_from_cloud_cmd(message: types.Message):
    """Загружает данные из облака в локальный файл"""
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        from database import load_from_cloud
        success, result_msg = load_from_cloud()
        await message.answer(result_msg)
        
    except Exception as e:
        logger.error(f"Error in load_from_cloud: {e}")
        await message.answer(f"❌ Ошибка: {e}")

async def reload_cache_cmd(message: types.Message):
    """Очищает кэш (старый reload)"""
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_data.get(user_id, {}).get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    try:
        from database import reload_cache
        result_msg = reload_cache()
        await message.answer(result_msg)
        
    except Exception as e:
        logger.error(f"Error in reload_cache: {e}")
        await message.answer(f"❌ Ошибка: {e}")

async def process_broadcast_message(message: types.Message, state: FSMContext, bot):
    if message.text == "❌ Отмена":
        await message.answer("❌ Рассылка отменена", reply_markup=create_reply_keyboard())
        await state.clear()
        return
    
    formatted_text = convert_entities_to_html(message.text, message.entities)
    
    user_data = load_user_data()
    success_count = 0
    fail_count = 0
    
    for target_user_id in user_data.keys():
        try:
            await bot.send_message(
                chat_id=target_user_id, 
                text=formatted_text,
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"Не удалось отправить сообщение пользователю {target_user_id}: {e}")
    
    await message.answer(
        f"✅ Рассылка завершена!\n\n📊 Статистика:\n• Отправлено: {success_count}\n• Не удалось: {fail_count}",
        reply_markup=create_reply_keyboard()
    )
    await state.clear()
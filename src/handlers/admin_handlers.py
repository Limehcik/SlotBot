from aiogram import types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from database import get_user, update_user, get_all_user_ids, find_user_by_username
from keyboards import create_reply_keyboard, create_cancel_keyboard

logger = logging.getLogger(__name__)

class BroadcastState(StatesGroup):
    waiting_for_message = State()

async def ban_user(message: types.Message):
    user_id = str(message.from_user.id)
    admin_data = get_user(user_id)
    
    if admin_data.get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Использование: /ban @username или /ban user_id")
        return
        
    target = parts[1].replace('@', '')
    target_user_id = target if target.isdigit() else find_user_by_username(target)
    
    if not target_user_id:
        await message.answer("❌ Пользователь не найден в базе данных!")
        return
        
    update_user(target_user_id, {"status": "ban"})
    await message.answer(f"🚫 Пользователь {target} успешно забанен!")

async def unban_user(message: types.Message):
    user_id = str(message.from_user.id)
    admin_data = get_user(user_id)
    
    if admin_data.get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Использование: /unban @username или /unban user_id")
        return
        
    target = parts[1].replace('@', '')
    target_user_id = target if target.isdigit() else find_user_by_username(target)
    
    if not target_user_id:
        await message.answer("❌ Пользователь не найден в базе данных!")
        return
        
    update_user(target_user_id, {"status": "norm"})
    await message.answer(f"✅ Пользователь {target} успешно разбанен!")

async def give_points(message: types.Message):
    user_id = str(message.from_user.id)
    admin_data = get_user(user_id)
    if admin_data.get("status") != "admin": return

    parts = message.text.split()
    if len(parts) < 3: return
    
    target = parts[1].replace('@', '')
    amount = int(parts[2])
    target_user_id = target if target.isdigit() else find_user_by_username(target)
    
    if target_user_id:
        user = get_user(target_user_id)
        update_user(target_user_id, {"balance": user["balance"] + amount})
        await message.answer(f"💰 Начислено {amount} баллов пользователю {target}!")

async def take_points(message: types.Message):
    user_id = str(message.from_user.id)
    admin_data = get_user(user_id)
    if admin_data.get("status") != "admin": return

    parts = message.text.split()
    if len(parts) < 3: return
    
    target = parts[1].replace('@', '')
    amount = int(parts[2])
    target_user_id = target if target.isdigit() else find_user_by_username(target)
    
    if target_user_id:
        user = get_user(target_user_id)
        update_user(target_user_id, {"balance": max(0, user["balance"] - amount)})
        await message.answer(f"📉 Забрано {amount} баллов у пользователя {target}!")

async def message_command(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    admin_data = get_user(user_id)
    
    if admin_data.get("status") != "admin":
        await message.answer("❌ Недостаточно прав!")
        return
    
    await message.answer("📨 Напишите сообщение для рассылки всем пользователям (можно использовать форматирование ТГ):", 
                         reply_markup=create_cancel_keyboard())
    await state.set_state(BroadcastState.waiting_for_message)

async def process_broadcast_message(message: types.Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Отмена":
        await message.answer("❌ Рассылка отменена", reply_markup=create_reply_keyboard())
        await state.clear()
        return
    
    # ВОТ ОНА — МАГИЯ AIOGRAM 3! Забираем готовый HTML со всеми entities автоматически!
    formatted_text = message.html_text
    
    await message.answer("⏳ Начинаю рассылку...")
    await state.clear()
    
    user_ids = get_all_user_ids()
    success_count = 0
    fail_count = 0
    
    for target_user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=target_user_id, 
                text=formatted_text,
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"Ошибка отправки пользователю {target_user_id}: {e}")
            
    await message.answer(
        f"📢 Рассылка завершена!\n\n"
        f"✅ Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}", 
        reply_markup=create_reply_keyboard()
    )
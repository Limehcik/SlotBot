from aiogram import types
from database import get_user, get_referrals
from keyboards import create_referral_keyboard

async def show_referral_info(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = get_user(user_id)
    
    referral_code = user_data.get("referral_code")
    referrals_count = user_data.get("referrals_count", 0)
    referral_bonus = user_data.get("referral_bonus", 0)
    
    bot_info = await message.bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={referral_code}"
    
    text = (
        f"👥 *Реферальная система*\n\n"
        f"🎯 Приглашайте друзей и получайте 10% от их выигрышей первые 3 дня!\n\n"
        f"📊 *Статистика:*\n"
        f"• Приглашено друзей: {referrals_count}\n"
        f"• Заработано бонусов: {referral_bonus} баллов\n\n"
        f"🔗 *Ваша реферальная ссылка:*\n"
        f"`{referral_link}`\n\n"
        f"📋 Просто отправьте эту ссылку другу!"
    )
    
    keyboard = create_referral_keyboard(referral_code)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

async def handle_referral_callback(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    data = callback.data
    
    if data.startswith("copy_ref_"):
        referral_code = data.replace("copy_ref_", "")
        bot_info = await callback.bot.get_me()
        referral_link = f"https://t.me/{bot_info.username}?start={referral_code}"
        
        await callback.answer("Ссылка готова для копирования! 📋", show_alert=True)
        await callback.message.answer(f"🔗 *Реферальная ссылка:*\n`{referral_link}`\n\nСкопируйте и отправьте другу!", parse_mode="Markdown")
    
    elif data == "my_refs":
        referrals = get_referrals(user_id)
        
        if not referrals:
            await callback.answer("У вас пока нет рефералов 😢", show_alert=True)
            return
        
        text = "👥 *Ваши рефералы:*\n\n"
        for i, ref in enumerate(referrals, start=1):
            username_str = f"@{ref['username']}" if ref['username'] else f"ID: {ref['user_id']}"
            text += f"{i}. {username_str} — Баланс: {ref['balance']} баллов\n"
            
        await callback.message.answer(text, parse_mode="Markdown")
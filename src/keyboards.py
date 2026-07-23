from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def create_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 КРУТИТЬ СЛОТЫ (10 баллов)")],
            [KeyboardButton(text="💰 Улучшить множитель"), KeyboardButton(text="⚡ Улучшить скорость")],
            [KeyboardButton(text="🎁 Ежедневный бонус"), KeyboardButton(text="📈 Статистика")],
            [KeyboardButton(text="👥 Реферальная система"), KeyboardButton(text="📋 Меню")]
        ],
        resize_keyboard=True
    )

def create_upgrade_keyboard(upgrade_type, cost):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🛒 Купить за {cost} баллов", callback_data=f"buy_{upgrade_type}_{cost}")]
        ]
    )

def create_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def create_referral_keyboard(referral_code):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Скопировать ссылку", callback_data=f"copy_ref_{referral_code}")],
            [InlineKeyboardButton(text="👥 Мои рефералы", callback_data="my_refs")]
        ]
    )
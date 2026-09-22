from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def create_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Слоты")],
            [KeyboardButton(text="💰 Улучшить множитель"), KeyboardButton(text="⚡ Улучшить скорость")],
            [KeyboardButton(text="🎁 Ежедневный бонус"), KeyboardButton(text="📈 Статистика")],
            [KeyboardButton(text="👥 Реферальная система"), KeyboardButton(text="📋 Меню")]
        ],
        resize_keyboard=True
    )

def create_upgrade_keyboard(upgrade_type, cost) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🛒 Купить за {cost} баллов", callback_data=f"buy_{upgrade_type}_{cost}")]
        ]
    )

def create_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def create_referral_keyboard(referral_code) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Скопировать ссылку", callback_data=f"copy_ref_{referral_code}")],
            [InlineKeyboardButton(text="👥 Мои рефералы", callback_data="my_refs")]
        ]
    )

def create_slots_keyboard(current_bet: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➖ 10"),
                KeyboardButton(text=f"🎰 КРУТИТЬ ({current_bet})"),
                KeyboardButton(text="➕ 10")
            ],
            [
                KeyboardButton(text="💰 ALL-IN"),
                KeyboardButton(text="🔙 Назад в меню")
            ]
        ],
        resize_keyboard=True
    )
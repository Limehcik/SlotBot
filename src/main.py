import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from dotenv import load_dotenv

# Загружаем переменные из файла .env в окружение системы
load_dotenv()

from database import get_all_admins, init_db
from handlers.user_handlers import cmd_start, spin_slots, daily_bonus_handler, show_stats, show_menu
from handlers.upgrade_handlers import upgrade_speed, upgrade_multiplier, buy_upgrade
from handlers.admin_handlers import ban_user, ping_command, unban_user, give_points, take_points, message_command, process_broadcast_message, BroadcastState
from handlers.referral_handlers import show_referral_info, handle_referral_callback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Токен бота не найден! Проверьте файл .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()

init_db()

admin_commands = [
        BotCommand(command="ping", description="Проверить пинг бота"),
        BotCommand(command="ban", description="Забанить пользователя"),
        BotCommand(command="unban", description="Разбанить пользователя"),
        BotCommand(command="give", description="Выдать очки"),
        BotCommand(command="take", description="Забрать очки"),
        BotCommand(command="message", description="Отправить рассылку всем пользователям")
    ]

async def register_comand():
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(spin_slots, F.text == "🎰 КРУТИТЬ СЛОТЫ (10 баллов)")
    dp.message.register(daily_bonus_handler, F.text == "🎁 Ежедневный бонус")
    dp.message.register(upgrade_speed, F.text == "⚡ Улучшить скорость")
    dp.message.register(upgrade_multiplier, F.text == "💰 Улучшить множитель")
    dp.message.register(show_stats, F.text == "📈 Статистика")
    dp.message.register(show_referral_info, F.text == "👥 Реферальная система")
    dp.message.register(show_menu, F.text == "📋 Меню")

    dp.message.register(ping_command, Command("ping"))
    dp.message.register(ban_user, Command("ban"))
    dp.message.register(unban_user, Command("unban"))
    dp.message.register(give_points, Command("give"))
    dp.message.register(take_points, Command("take"))
    dp.message.register(message_command, Command("message"))
    dp.message.register(process_broadcast_message, BroadcastState.waiting_for_message)

    dp.callback_query.register(buy_upgrade, F.data.startswith("buy_"))
    dp.callback_query.register(handle_referral_callback, F.data.startswith("copy_ref_") | (F.data == "my_refs"))

async def setup_bot_menu(bot: Bot):
    await bot.set_my_commands(commands=[], scope=BotCommandScopeDefault())
    
    admin_ids = get_all_admins()
    
    for admin_id in admin_ids:
        try:
            await bot.set_my_commands(
                commands=admin_commands,
                scope=BotCommandScopeChat(chat_id=int(admin_id))
            )
        except Exception as e:
            pass

async def main():
    await register_comand()
    await setup_bot_menu(bot)
    logger.info("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

from database import load_user_data, repair_database
import database
from handlers.user_handlers import cmd_start, spin_slots, daily_bonus, show_stats, show_menu
from handlers.upgrade_handlers import upgrade_speed, upgrade_multiplier, buy_upgrade
from handlers.admin_handlers import (
    ban_user, unban_user, give_points, take_points, 
    message_command, process_broadcast_message,
    save_to_cloud_cmd, load_from_cloud_cmd, reload_cache_cmd
)
from keyboards import create_reply_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "токен_бота"  # Замените на ваш токен бота

if TOKEN == "токен_бота":
    print("Впишите токен бота!")
    sys.exit(1)

if database.GIST_ID == "гист_айди" or database.GITHUB_TOKEN == "гитхаб_токен":
    print("Впишите Gist ID и GitHub Token в database.py!")
    sys.exit(1)
    

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = load_user_data()
user_data = repair_database(user_data)

dp.message.register(cmd_start, Command("start"))
dp.message.register(spin_slots, F.text == "🎰 КРУТИТЬ СЛОТЫ (10 баллов)")
dp.message.register(daily_bonus, F.text == "🎁 Ежедневный бонус")
dp.message.register(upgrade_speed, F.text == "⚡ Улучшить скорость")
dp.message.register(upgrade_multiplier, F.text == "💰 Улучшить множитель")
dp.message.register(show_stats, F.text == "📈 Статистика")
dp.message.register(show_menu, F.text == "📋 Меню")

dp.callback_query.register(buy_upgrade, F.data.startswith("buy_"))

dp.message.register(ban_user, Command("ban"))
dp.message.register(unban_user, Command("unban"))
dp.message.register(give_points, Command("give"))
dp.message.register(take_points, Command("take"))
dp.message.register(message_command, Command("message"))
dp.message.register(save_to_cloud_cmd, Command("save"))
dp.message.register(load_from_cloud_cmd, Command("load")) 
dp.message.register(reload_cache_cmd, Command("reload"))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
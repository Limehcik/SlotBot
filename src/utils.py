import time
from datetime import datetime, date

def give_daily_bonus(user_id, user_data):
    today = date.today().isoformat()
    
    if user_data.get("last_daily") != today:
        user_data["balance"] += 100
        user_data["last_daily"] = today
        return True, user_data
    return False, user_data

def can_spin(user_data):
    if user_data.get("status") == "ban":
        return False
        
    current_time = time.time()
    last_spin = user_data.get("last_spin", 0)
    upgrade_level = user_data.get("upgrade_level", 0)
    cooldown = 10 - (upgrade_level * 0.25)
    
    return current_time - last_spin >= cooldown

def get_remaining_cooldown(user_data):
    current_time = time.time()
    last_spin = user_data.get("last_spin", 0)
    upgrade_level = user_data.get("upgrade_level", 0)
    cooldown = 10 - (upgrade_level * 0.25)
    
    remaining = cooldown - (current_time - last_spin)
    return max(0, remaining)

def calculate_win(dice_value: int, multiplier_level: int = 0) -> int:
    symbols = ["BAR", "🍇", "🍋", "7"]
    value = dice_value - 1
    
    reel1 = symbols[value % 4]
    reel2 = symbols[(value // 4) % 4]
    reel3 = symbols[(value // 16) % 4]
    
    base_wins = {
        ("7", "7", "7"): 3000,
        ("BAR", "BAR", "BAR"): 1000,
        ("🍇", "🍇", "🍇"): 500,
        ("🍋", "🍋", "🍋"): 250,
        "three_of_a_kind": 300,
        "two_sevens": 75,
        "two_bars": 30
    }
    
    multiplier = 1 + (multiplier_level * 0.1)  # 10% увеличение за уровень
    
    if reel1 == reel2 == reel3 == "7":
        return int(base_wins[("7", "7", "7")] * multiplier)
    elif reel1 == reel2 == reel3 == "BAR":
        return int(base_wins[("BAR", "BAR", "BAR")] * multiplier)
    elif reel1 == reel2 == reel3 == "🍇":
        return int(base_wins[("🍇", "🍇", "🍇")] * multiplier)
    elif reel1 == reel2 == reel3 == "🍋":
        return int(base_wins[("🍋", "🍋", "🍋")] * multiplier)
    elif (reel1 == reel2 == "7") or (reel2 == reel3 == "7") or (reel1 == reel3 == "7"):
        return int(base_wins["two_sevens"] * multiplier)
    elif (reel1 == reel2 == "BAR") or (reel2 == reel3 == "BAR") or (reel1 == reel3 == "BAR"):
        return int(base_wins["two_bars"] * multiplier)
    else:
        return 0

def get_win_text(win_amount: int) -> str:
    if win_amount >= 3000:
        return f"🎯 ДЖЕКПОТ! 777! Выигрыш: {win_amount} баллов! 🏆"
    elif win_amount >= 1000:
        return f"🔥 Три BAR! Выигрыш: {win_amount} баллов! 💰"
    elif win_amount >= 500:
        return f"🍇 Три винограда! Выигрыш: {win_amount} баллов! 🎉"
    elif win_amount >= 250:
        return f"🍋 Три лимона! Выигрыш: {win_amount} баллов! 👍"
    elif win_amount >= 75:
        return f"🎰 Две семерки! Выигрыш: {win_amount} баллов!"
    elif win_amount >= 30:
        return f"📊 Два BAR! Выигрыш: {win_amount} баллов!"
    else:
        return "😢 Не повезло... Выигрыша нет"

def find_user_by_username(username, user_data):
    username = username.lower().replace('@', '')
    for user_id, user_info in user_data.items():
        if user_info.get("username", "").lower() == username:
            return user_id
    return None

def convert_entities_to_html(text: str, entities: list) -> str:
    """Конвертирует Telegram entities в HTML форматирование"""
    if not entities:
        return text
    
    sorted_entities = sorted(entities, key=lambda x: x.offset, reverse=True)
    
    result = text
    for entity in sorted_entities:
        start = entity.offset
        end = entity.offset + entity.length
        
        if start >= len(result) or end > len(result):
            continue
            
        entity_text = result[start:end]
        
        if entity.type == "bold":
            formatted = f"<b>{entity_text}</b>"
        elif entity.type == "italic":
            formatted = f"<i>{entity_text}</i>"
        elif entity.type == "underline":
            formatted = f"<u>{entity_text}</u>"
        elif entity.type == "strikethrough":
            formatted = f"<s>{entity_text}</s>"
        elif entity.type == "code":
            formatted = f"<code>{entity_text}</code>"
        elif entity.type == "pre":
            formatted = f"<pre>{entity_text}</pre>"
        elif entity.type == "text_link":
            formatted = f'<a href="{entity.url}">{entity_text}</a>'
        else:
            formatted = entity_text
        
        result = result[:start] + formatted + result[end:]
    
    return result
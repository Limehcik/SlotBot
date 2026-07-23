import json
import os
import requests
from datetime import datetime, date

DATA_FILE = "user_data.json"
GIST_ID = "гист_айди"  # Замените на ваш Gist ID
GITHUB_TOKEN = "гитхаб_токен"  # Замените на ваш GitHub Token, у которого есть доступ к Gist
GIST_FILENAME = "user_data.json"

_user_data_cache = None

def load_user_data():
    """Загружает данные из локального JSON файла"""
    global _user_data_cache
    
    if _user_data_cache is not None:
        return _user_data_cache.copy()
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                _user_data_cache = user_data
                return user_data.copy()
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return {}
    return {}

def save_user_data(user_data):
    """Сохраняет данные в локальный JSON файл"""
    global _user_data_cache
    
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        _user_data_cache = user_data.copy()
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

def save_to_cloud():
    """Сохраняет локальные данные в облако"""
    if not GITHUB_TOKEN or not GIST_ID:
        return False, "Не настроен Gist"
    
    try:
        user_data = load_user_data()
        
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        json_data = json.dumps(user_data, ensure_ascii=False, indent=2)
        
        data = {
            "files": {
                GIST_FILENAME: {
                    "content": json_data
                }
            }
        }
        
        url = f"https://api.github.com/gists/{GIST_ID}"
        response = requests.patch(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, f"✅ Данные сохранены в облако! Пользователей: {len(user_data)}"
        else:
            return False, f"❌ Ошибка облака: {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Ошибка: {e}"

def load_from_cloud():
    """Загружает данные из облака в локальный файл"""
    if not GITHUB_TOKEN or not GIST_ID:
        return False, "Не настроен Gist"
    
    try:
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        url = f"https://api.github.com/gists/{GIST_ID}"
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            gist_data = response.json()
            content = gist_data['files'][GIST_FILENAME]['content']
            user_data = json.loads(content)
            
            # Сохраняем в локальный файл
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            global _user_data_cache
            _user_data_cache = user_data.copy()
            
            return True, f"✅ Данные загружены из облака! Пользователей: {len(user_data)}"
        else:
            return False, f"❌ Ошибка загрузки: {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Ошибка: {e}"

def reload_cache():
    """Просто очищает кэш (старый /reload)"""
    global _user_data_cache
    _user_data_cache = None
    
    user_data = load_user_data()
    return f"✅ Кэш очищен! Пользователей в памяти: {len(user_data)}"

# Остальные функции без изменений
def repair_database(user_data):
    for user_id, user_info in user_data.items():
        defaults = {
            "status": "norm",
            "balance": 500,
            "last_daily": "",
            "last_spin": 0,
            "upgrade_level": 0,
            "multiplier_level": 0,
            "upgrade_cost": 500,
            "multiplier_cost": 1000,
            "total_spins": 0,
            "total_wins": 0,
            "username": ""
        }
        
        for key, value in defaults.items():
            if key not in user_info:
                user_info[key] = value
    
    save_user_data(user_data)
    return user_data

def get_user(user_id, username=""):
    user_data = load_user_data()
    
    if user_id not in user_data:
        user_data[user_id] = {
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
            "username": username
        }
        save_user_data(user_data)
    else:
        if username and user_data[user_id].get("username") != username:
            user_data[user_id]["username"] = username
            save_user_data(user_data)
    
    return user_data[user_id]

def update_user(user_id, updates):
    user_data = load_user_data()
    if user_id in user_data:
        user_data[user_id].update(updates)
        save_user_data(user_data)
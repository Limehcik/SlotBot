import sqlite3
import os
from datetime import datetime, date

DB_FILE = "bot_database.db"

def init_db():
    """Инициализация базы данных SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 500,
            last_daily TEXT DEFAULT '',
            last_spin REAL DEFAULT 0.0,
            upgrade_level INTEGER DEFAULT 0,
            multiplier_level INTEGER DEFAULT 0,
            upgrade_cost INTEGER DEFAULT 500,
            multiplier_cost INTEGER DEFAULT 1000,
            total_spins INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            current_bet INTEGER DEFAULT 10,
            status TEXT DEFAULT 'norm',
            referral_code TEXT,
            referred_by TEXT,
            referral_date TEXT,
            referral_bonus INTEGER DEFAULT 0,
            referrals_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id: str, username: str = "") -> dict:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        referral_code = f"ref_{user_id}"
        cursor.execute('''
            INSERT INTO users (user_id, username, referral_code)
            VALUES (?, ?, ?)
        ''', (user_id, username, referral_code))
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
    elif username and row["username"] != username:
        cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
    user_dict = dict(row)
    conn.close()
    return user_dict

def update_user(user_id: str, updates: dict):
    if not updates:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values())
    values.append(user_id)
    
    cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
    conn.commit()
    conn.close()

def find_user_by_referral_code(referral_code: str) -> str | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE referral_code = ?", (referral_code,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_user_ids() -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_referrals(user_id: str) -> list:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE referred_by = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def find_user_by_username(username: str) -> str | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_admins() -> list:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE status = 'admin'")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]
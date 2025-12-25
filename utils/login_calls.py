import os
import sys
import sqlite3

app_folder = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(app_folder, "database.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def validate_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                   (username, password))
    user = cursor.fetchone()

    conn.close()
    return user is not None
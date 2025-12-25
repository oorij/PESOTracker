import sqlite3

conn = sqlite3.connect('database/database.db')
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
);
""")

# Insert dummy beneficiaries if table is empty
cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    dummy_users = [
        ("admin", "admin123")
    ]
    
    cursor.executemany("""
    INSERT INTO users (username, password) VALUES (?, ?)
    """, dummy_users)

conn.commit()
conn.close()

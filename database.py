import sqlite3

conn = sqlite3.connect('my_database.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    chat_id TEXT,
    name TEXT,
    avatar TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Offices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER,
    datetime DATETIME,
    location TEXT,
    office_distance INTEGER,
    office_name TEXT,
    FOREIGN KEY (id_user) REFERENCES Users(id)
)
''')

conn.commit()
conn.close()

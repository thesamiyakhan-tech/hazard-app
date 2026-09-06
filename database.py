import sqlite3

def init_db():
    conn = sqlite3.connect('sih.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, lat REAL, long REAL, description TEXT, photo_url TEXT, status TEXT, time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS risk_scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, lat REAL, long REAL, risk_level TEXT, score INTEGER, rainfall REAL, slope REAL, history INTEGER, time TEXT)''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('sih.db')
    conn.row_factory = sqlite3.Row
    return conn
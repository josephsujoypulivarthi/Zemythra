import sqlite3

def init_db():
    conn = sqlite3.connect("zemythra.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk_score INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_history(score, time):
    conn = sqlite3.connect("zemythra.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO history (risk_score, timestamp) VALUES (?, ?)",
        (score, time)
    )

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect("zemythra.db")
    cursor = conn.cursor()

    cursor.execute("SELECT risk_score, timestamp FROM history ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()

    conn.close()

    return [{"score": r[0], "time": r[1]} for r in rows]
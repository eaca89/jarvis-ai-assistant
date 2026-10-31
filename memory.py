"""Part 4 - Memory: facts about you and recent chat, saved in one SQLite file."""
import sqlite3

db = sqlite3.connect("memory.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS facts (user TEXT, fact TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS chat (user TEXT, role TEXT, text TEXT)")

def add_fact(user, fact):
    db.execute("INSERT INTO facts VALUES (?, ?)", (user, fact)); db.commit()

def facts(user):
    return [r[0] for r in db.execute("SELECT fact FROM facts WHERE user = ?", (user,))]

def save_turn(user, role, text):
    db.execute("INSERT INTO chat VALUES (?, ?, ?)", (user, role, text)); db.commit()

def recent(user, n=10):
    rows = db.execute("SELECT role, text FROM chat WHERE user = ? ORDER BY rowid DESC LIMIT ?",
                      (user, n)).fetchall()
    return rows[::-1]

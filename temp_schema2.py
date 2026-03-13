import sqlite3
db = sqlite3.connect('phonebook.db')
cur = db.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
print('All tables:', cur.fetchall())
db.close()

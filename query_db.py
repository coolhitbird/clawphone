import sqlite3
db = r"C:\Users\wang20\.openclaw\skills\clawphone\phonebook.db"
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT alias, phone_id, tags, notes FROM phones")
rows = cur.fetchall()
print("alias | phone_id | tags | notes")
print("-" * 60)
for r in rows:
    alias, phone_id, tags, notes = r
    print(f"{alias} | {phone_id} | {tags} | {notes or ''}")
conn.close()

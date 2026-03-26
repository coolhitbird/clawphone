import sqlite3
conn = sqlite3.connect('phonebook.db')
cur = conn.cursor()
cur.execute('SELECT alias, phone_id, address FROM phones')
rows = cur.fetchall()
print('alias | phone_id | address')
print('-' * 50)
for r in rows:
    alias, phone_id, address = r
    print(f'{alias} | {phone_id} | {address or "N/A"}')
conn.close()

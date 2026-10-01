import sqlite3

conn = sqlite3.connect('circuit_app.db')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR DEFAULT '';")
except sqlite3.OperationalError as e:
    print(e)
    
try:
    cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'student';")
except sqlite3.OperationalError as e:
    print(e)

try:
    cur.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;")
except sqlite3.OperationalError as e:
    print(e)

conn.commit()
cur.close()
conn.close()
print("Alter table done")

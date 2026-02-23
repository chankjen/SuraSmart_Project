import sqlite3

db = 'backend/db.sqlite3'
conn = sqlite3.connect(db)
cur = conn.cursor()
try:
    cur.execute('SELECT username,is_active_user,verification_status FROM users_user LIMIT 50')
    rows = cur.fetchall()
    print('ROWS:', len(rows))
    for r in rows:
        print(r)
except Exception as e:
    print('ERROR', e)
finally:
    conn.close()

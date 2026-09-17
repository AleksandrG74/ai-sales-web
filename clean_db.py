import sqlite3

db_path = '/opt/ai-sales-web/backend/data/database.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

spam_sources = [
    'telegram_zhfut',
    'telegram_MainCardChat',
    'telegram_strbypass',
    'telegram_rztkd_chat',
    'telegram_inter_thread',
    'telegram_onlain_biznes_rabota',
    'telegram_biznes_klient_rabota',
    'telegram_mplace_chats_help',
    'telegram_psikhiatria',
    'telegram_routerich',
    'telegram_byebyedpi_group',
    'telegram_neBlackGroup2',
]

print("До очистки:")
cur.execute("SELECT COUNT(*) FROM leads")
print(f"  leads: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM dialogs")
print(f"  dialogs: {cur.fetchone()[0]}")

placeholders = ','.join('?' * len(spam_sources))

cur.execute(f"DELETE FROM leads WHERE source IN ({placeholders})", spam_sources)
print(f"\nУдалено из leads: {cur.rowcount}")

cur.execute("DELETE FROM dialogs WHERE lead_id NOT IN (SELECT id FROM leads)")
print(f"Удалено из dialogs: {cur.rowcount}")

conn.commit()

print("\nПосле очистки:")
cur.execute("SELECT COUNT(*) FROM leads")
print(f"  leads: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM dialogs")
print(f"  dialogs: {cur.fetchone()[0]}")

print("\nОсталось каналов:")
cur.execute("SELECT source, COUNT(*) FROM leads GROUP BY source ORDER BY COUNT(*) DESC")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
print("\n✅ База очищена!")

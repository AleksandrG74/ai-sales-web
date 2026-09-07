import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "database.db")

def add_clients():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже клиенты
    cursor.execute("SELECT COUNT(*) FROM leads")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ В базе уже есть {count} клиентов")
        cursor.execute("SELECT user_id, username, intent_score FROM leads")
        for row in cursor.fetchall():
            print(f"   {row[0]} | {row[1]} | {row[2]}%")
        conn.close()
        return
    
    # Добавляем клиентов
    clients = [
        ('@user123', 'Алексей', 'Здравствуйте! Ищу холодильник, чтобы был тихий и экономичный. Бюджет до 50 000 ₽.', 'telegram', 'Москва', 'buying', 85, 'Холодильник Bosch', 'new'),
        ('@user456', 'Мария', 'Сломался старый холодильник, нужно срочно купить новый.', 'telegram', 'Санкт-Петербург', 'problem', 75, 'Холодильник Bosch', 'new'),
        ('@user789', 'Иван', 'Посоветуйте хороший холодильник для дачи.', 'telegram', 'Казань', 'seeking', 45, 'Холодильник Bosch', 'new')
    ]
    
    for client in clients:
        cursor.execute('''
            INSERT INTO leads (user_id, username, message, source, region, intent, intent_score, product, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*client, datetime.now()))
    
    conn.commit()
    
    print("✅ Добавлены клиенты:")
    cursor.execute("SELECT user_id, username, intent_score FROM leads")
    for row in cursor.fetchall():
        print(f"   {row[0]} | {row[1]} | {row[2]}%")
    
    conn.close()

if __name__ == "__main__":
    add_clients()

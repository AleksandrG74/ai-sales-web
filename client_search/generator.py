#!/usr/bin/env python
"""
Генератор тестовых клиентов для демонстрации работы системы
"""
import os
import sys
import json
import random
import logging
from datetime import datetime, timedelta
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_db, LeadDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientGenerator:
    def __init__(self):
        self.product = "холодильник"
        self.count = 10

    def generate_messages(self):
        templates = [
            "Здравствуйте! Ищу {product} для дома.",
            "Нужен {product} с большой морозильной камерой.",
            "Купить {product} недорого.",
            "Срочно нужен {product}!",
            "Какой {product} лучше взять?",
            "Ищу {product} с энергоэффективностью А++."
        ]
        
        users = ["Анна", "Михаил", "Елена", "Сергей", "Ольга", "Дмитрий", "Ирина"]
        
        messages = []
        for i in range(self.count):
            template = random.choice(templates)
            message = template.format(product=self.product)
            username = random.choice(users)
            score = random.randint(30, 95)
            
            messages.append({
                'user_id': f"web_user_{i+1:03d}",
                'username': username,
                'message': message,
                'source': random.choice(['telegram', 'web', 'referral']),
                'intent_score': score,
                'product': self.product,
                'status': random.choice(['new', 'contacted', 'in_progress', 'converted'])
            })
        
        return messages

    def save_leads(self, messages):
        db = next(get_db())
        saved = 0
        try:
            for msg in messages:
                existing = db.query(LeadDB).filter(LeadDB.user_id == msg['user_id']).first()
                if existing:
                    continue
                lead = LeadDB(
                    user_id=msg['user_id'],
                    username=msg['username'],
                    message=msg['message'],
                    source=msg['source'],
                    intent="seeking",
                    intent_score=msg['intent_score'],
                    product=msg['product'],
                    status=msg['status']
                )
                db.add(lead)
                saved += 1
            db.commit()
            logger.info(f"✅ Сохранено {saved} клиентов")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            db.rollback()
        finally:
            db.close()
        return saved

    def run(self):
        logger.info(f"📊 Генерация {self.count} клиентов для {self.product}")
        messages = self.generate_messages()
        return self.save_leads(messages)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--product', default='холодильник')
    args = parser.parse_args()
    
    init_db()
    generator = ClientGenerator()
    generator.count = args.count
    generator.product = args.product
    generator.run()

if __name__ == "__main__":
    main()

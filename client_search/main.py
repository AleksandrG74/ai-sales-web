#!/usr/bin/env python
"""
Модуль поиска клиентов в Telegram — v2.
Режимы:
  --mode search  — сканировать каналы, искать лидов
  --mode fetch   — скачать историю чатов в DialogDB
  --mode mine    — отобрать успешные диалоги
  --mode all     — search + fetch + mine
"""
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.database import init_db, get_db, LeadDB, DialogDB, SettingsDB
from client_search.goal_tokens import score_goal, classify_signal

os.makedirs(os.path.join(PROJECT_ROOT, "logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, "logs", "search.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("client_search")


def _extract_author(msg):
    author = {"author_id": None, "author_username": "", "author_name": "", "reply_to_msg_id": None}
    try:
        if msg.from_id and hasattr(msg.from_id, "user_id"):
            author["author_id"] = msg.from_id.user_id
        if msg.reply_to and hasattr(msg.reply_to, "reply_to_msg_id"):
            author["reply_to_msg_id"] = msg.reply_to.reply_to_msg_id
        if msg.sender:
            s = msg.sender
            author["author_username"] = getattr(s, "username", "") or ""
            first = getattr(s, "first_name", "") or ""
            last = getattr(s, "last_name", "") or ""
            author["author_name"] = (first + " " + last).strip()
    except Exception:
        pass
    return author


class TelegramSearcher:
    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.api_id = self.config.get("api_id")
        self.api_hash = self.config.get("api_hash")
        self.phone = self.config.get("phone")
        self.channels = self.config.get("channels", [])
        self.keywords = self.config.get("keywords", [])
        self.product = self.config.get("product", "холодильник")
        self.threshold = self.config.get("intent_threshold", 40)
        self.scan_limit = self.config.get("scan_limit", 50)
        self.client = None

    async def connect(self):
        session_path = os.path.join(PROJECT_ROOT, "sessions", "telegram_session")
        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
        try:
            await self.client.start(phone=self.phone)
            me = await self.client.get_me()
            logger.info(f"✅ Подключен как: {me.first_name} (@{me.username})")
            return True
        except SessionPasswordNeededError:
            logger.error("❌ Требуется 2FA пароль")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения: {e}")
            return False

    def calculate_intent(self, text):
        text_lower = text.lower()
        score = 0
        matched = sum(1 for kw in self.keywords if kw.lower() in text_lower)
        score += min(matched * 10, 40)
        buying = ["купить", "приобрести", "заказать", "хочу", "нужен", "ищу", "выбрать"]
        score += min(sum(5 for w in buying if w in text_lower), 30)
        urgency = ["срочно", "сегодня", "завтра", "быстро", "горящий", "скидка"]
        score += min(sum(3 for w in urgency if w in text_lower), 15)
        questions = ["как", "что", "где", "сколько", "какой", "почему", "когда"]
        if "?" in text:
            score += min(sum(3 for w in questions if w in text_lower), 15)
        goal_bonus = score_goal(text) // 5
        score += min(goal_bonus, 20)
        return min(score, 100)

    async def save_lead(self, msg, source, score):
        db = next(get_db())
        try:
            username = None
            if msg.sender:
                username = getattr(msg.sender, "username", None) or getattr(msg.sender, "first_name", None)
            elif msg.from_id:
                username = str(msg.from_id)
            existing = db.query(LeadDB).filter(LeadDB.user_id == str(msg.sender_id)).first()
            if existing:
                if existing.intent_score < score:
                    existing.intent_score = score
                    existing.message = msg.text[:500]
                    db.commit()
                return
            lead = LeadDB(
                user_id=str(msg.sender_id),
                username=username,
                message=msg.text[:500],
                source=f"telegram_{source}",
                intent="seeking",
                intent_score=score,
                product=self.product,
                status="new",
            )
            db.add(lead)
            db.commit()
            logger.info(f"💾 Лид: {msg.sender_id} (score: {score})")
        except Exception as e:
            logger.error(f"❌ save_lead: {e}")
            db.rollback()
        finally:
            db.close()

    async def save_dialog(self, msg, source):
        db = next(get_db())
        try:
            author = _extract_author(msg)
            signals = classify_signal(msg.text or "")
            tokens = (
                signals.get("strong", []) +
                signals.get("medium", []) +
                signals.get("weak", [])
            )
            lead = db.query(LeadDB).filter(
                LeadDB.user_id == str(author["author_id"])
            ).first()
            author_id = author.get("author_id")
            reply_to = author.get("reply_to_msg_id")
            sender_str = f"{author_id}@{source}" if author_id else f"unknown@{source}"
            
            dialog = DialogDB(
                lead_id=lead.id if lead else None,
                sender=sender_str,
                message=msg.text[:2000],
                timestamp=msg.date,
                strategy_used=",".join(tokens) if tokens else None,
                author_id=str(author_id) if author_id else None,
                reply_to_msg_id=reply_to,
            )
            db.add(dialog)
            db.commit()
        except Exception as e:
            logger.debug(f"save_dialog: {e}")
            db.rollback()
        finally:
            db.close()

    async def mode_search(self):
        total = 0
        for channel in self.channels:
            try:
                entity = await self.client.get_entity(channel)
                logger.info(f"📡 Сканируем: {channel}")
                async for msg in self.client.iter_messages(entity, limit=self.scan_limit):
                    if not msg.text:
                        continue
                    score = self.calculate_intent(msg.text)
                    if score >= self.threshold:
                        await self.save_lead(msg, channel, score)
                        total += 1
                logger.info(f"✅ {channel}: {total}")
            except Exception as e:
                logger.error(f"❌ {channel}: {e}")
        logger.info(f"📊 Всего лидов: {total}")
        return total

    async def mode_fetch(self, limit=1000, days_back=30):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        total = 0
        for channel in self.channels:
            try:
                entity = await self.client.get_entity(channel)
                logger.info(f"📥 Скачиваем @{channel}...")
                async for msg in self.client.iter_messages(entity, limit=limit):
                    if not msg.message or not msg.message.strip():
                        continue
                    if msg.date and msg.date < cutoff:
                        break
                    await self.save_dialog(msg, channel)
                    total += 1
                    if score_goal(msg.text) >= 50:
                        await self.save_lead(msg, channel, score_goal(msg.text))
                logger.info(f"  ✅ Сообщений: {total}")
            except Exception as e:
                logger.error(f"❌ fetch @{channel}: {e}")
        return total

    async def mode_mine(self):
        db = next(get_db())
        try:
            dialogs = db.query(DialogDB).filter(
                DialogDB.strategy_used != None,
                DialogDB.strategy_used != "",
            ).limit(100).all()
            logger.info(f"📊 Найдено диалогов: {len(dialogs)}")
            successful = []
            for d in dialogs:
                if d.lead_id:
                    lead = db.query(LeadDB).filter(LeadDB.id == d.lead_id).first()
                    if lead:
                        successful.append({
                            "dialog_id": d.id,
                            "lead_id": d.lead_id,
                            "buyer": lead.username,
                            "message": d.message[:200],
                            "tokens": d.strategy_used,
                            "timestamp": d.timestamp.isoformat() if d.timestamp else None,
                        })
            setting = db.query(SettingsDB).filter(SettingsDB.key == "successful_dialogues").first()
            if not setting:
                setting = SettingsDB(key="successful_dialogues", value="[]")
                db.add(setting)
            setting.value = json.dumps(successful, ensure_ascii=False)
            db.commit()
            logger.info(f"✅ Сохранено: {len(successful)}")
            return len(successful)
        except Exception as e:
            logger.error(f"❌ mine: {e}")
            return 0
        finally:
            db.close()

    async def run(self, mode="search"):
        # mode=mine работает только с БД — Telegram не нужен
        if mode == "mine":
            await self.mode_mine()
            return

        if not await self.connect():
            return

        if mode == "search":
            await self.mode_search()
        elif mode == "fetch":
            await self.mode_fetch()
        elif mode == "all":
            await self.mode_search()
            await self.mode_fetch()
            await self.mode_mine()

        await self.client.disconnect()
        logger.info("🔌 Отключено")


def main():
    parser = argparse.ArgumentParser(description="Telegram client search v2")
    parser.add_argument("--config", default="configs/telegram_config.json")
    parser.add_argument("--mode", choices=["search", "fetch", "mine", "all"], default="search")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()

    init_db(os.path.join(PROJECT_ROOT, "backend", "data", "database.db"))

    config_path = os.path.join(PROJECT_ROOT, args.config)
    searcher = TelegramSearcher(config_path)

    if args.loop:
        import time
        while True:
            asyncio.run(searcher.run(mode=args.mode))
            logger.info("⏳ Ожидание 1 час...")
            time.sleep(3600)
    else:
        asyncio.run(searcher.run(mode=args.mode))


if __name__ == "__main__":
    main()

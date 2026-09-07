INSERT INTO leads (user_id, username, message, source, region, intent, intent_score, product, status, created_at) 
VALUES 
('@user123', 'Алексей', 'Здравствуйте! Ищу холодильник, чтобы был тихий и экономичный. Бюджет до 50 000 ₽.', 'telegram', 'Москва', 'buying', 85, 'Холодильник Bosch', 'new', datetime('now'));

INSERT INTO leads (user_id, username, message, source, region, intent, intent_score, product, status, created_at) 
VALUES 
('@user456', 'Мария', 'Сломался старый холодильник, нужно срочно купить новый.', 'telegram', 'Санкт-Петербург', 'problem', 75, 'Холодильник Bosch', 'new', datetime('now'));

INSERT INTO leads (user_id, username, message, source, region, intent, intent_score, product, status, created_at) 
VALUES 
('@user789', 'Иван', 'Посоветуйте хороший холодильник для дачи.', 'telegram', 'Казань', 'seeking', 45, 'Холодильник Bosch', 'new', datetime('now'));

SELECT '✅ Клиенты добавлены!' as result;
SELECT * FROM leads;

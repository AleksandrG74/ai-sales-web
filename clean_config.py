import json

config_path = '/opt/ai-sales-web/configs/telegram_config.json'

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

print("Список каналов ДО очистки:")
for ch in config['channels']:
    print(f'  - {ch}')

spam = [
    'zhfut',
    'MainCardChat',
    'strbypass',
    'rztkd_chat',
    'inter_thread',
    'onlain_biznes_rabota',
    'biznes_klient_rabota',
    'mplace_chats_help',
    'psikhiatria',
    'routerich',
    'byebyedpi_group',
    'neBlackGroup2',
]

config['channels'] = [ch for ch in config['channels'] if ch not in spam]

print(f"\nОсталось каналов: {len(config['channels'])}")
for ch in config['channels']:
    print(f'  - {ch}')

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("\n✅ Конфиг обновлён!")

DELETE FROM leads WHERE source IN (
    'telegram_neBlackGroup2',
    'telegram_biznes_klient_rabota',
    'telegram_onlain_biznes_rabota',
    'telegram_mplace_chats_help',
    'telegram_zhfut',
    'telegram_MainCardChat',
    'telegram_psikhiatria',
    'telegram_strbypass',
    'telegram_byebyedpi_group',
    'telegram_routerich',
    'telegram_rztkd_chat',
    'telegram_inter_thread'
);

DELETE FROM dialogs WHERE source IN (
    'telegram_neBlackGroup2',
    'telegram_biznes_klient_rabota',
    'telegram_onlain_biznes_rabota',
    'telegram_mplace_chats_help',
    'telegram_zhfut',
    'telegram_MainCardChat',
    'telegram_psikhiatria',
    'telegram_strbypass',
    'telegram_byebyedpi_group',
    'telegram_routerich',
    'telegram_rztkd_chat',
    'telegram_inter_thread'
);

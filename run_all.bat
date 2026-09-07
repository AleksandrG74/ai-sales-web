@echo off
echo ========================================
echo  AI Sales Agent - Запуск всех сервисов
echo ========================================
echo.

echo [1/3] Запуск бэкенда (FastAPI + Оркестратор)...
start "Orchestrator" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak >nul

echo [2/3] Запуск Telegram бота...
start "Telegram Bot" cmd /k "cd telegram_bot && python main.py"

echo [3/3] Проверка статуса...
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  ✅ Все сервисы запущены!
echo  🌐 Веб-интерфейс: http://localhost:8000
echo  📚 API Docs: http://localhost:8000/docs
echo  🤖 Telegram бот: активен
echo ========================================
echo.
echo Для остановки нажмите Ctrl+C в каждом окне
echo Или выполните: taskkill /F /IM python.exe
echo.
pause

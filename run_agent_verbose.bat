@echo on
cd /d "C:\Users\52602\ai-sales-web"
echo ========================================
echo AI Sales Agent - Запуск (отладка)
echo ========================================
echo Текущая папка: %cd%
echo.
echo Проверка pythonw.exe...
if exist "venv\Scripts\pythonw.exe" (echo pythonw.exe found!) else (echo pythonw.exe NOT found!)
echo.
echo Starting application...
start /b "" "C:\Users\52602\ai-sales-web\venv\Scripts\pythonw.exe" "C:\Users\52602\ai-sales-web\window.py"
echo Application started, waiting 10 seconds...
timeout /t 10
echo Done.
pause
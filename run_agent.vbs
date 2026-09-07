Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\52602\ai-sales-web"
WshShell.Run "C:\Users\52602\ai-sales-web\venv\Scripts\pythonw.exe C:\Users\52602\ai-sales-web\window.py", 0, False

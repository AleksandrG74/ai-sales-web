Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\AI Sales Agent.lnk")
Set oLink = oWS.CreateShortcut(sLinkFile)

' Путь к программе
oLink.TargetPath = "C:\Users\52602\ai-sales-web\run_agent.bat"

' Рабочая папка
oLink.WorkingDirectory = "C:\Users\52602\ai-sales-web"

' Описание
oLink.Description = "AI Sales Agent - умный помощник для продаж"

' Иконка
oLink.IconLocation = "C:\Users\52602\ai-sales-web\images\icon.ico"

' Сохраняем
oLink.Save

WScript.Echo "✅ Ярлык создан на рабочем столе!"

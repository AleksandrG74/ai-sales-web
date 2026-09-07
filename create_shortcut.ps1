$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\OneDrive\Рабочий стол\AI Sales Agent.lnk")
$Shortcut.TargetPath = "C:\Users\52602\ai-sales-web\run_agent.bat"
$Shortcut.WorkingDirectory = "C:\Users\52602\ai-sales-web"
$Shortcut.Description = "AI Sales Agent"
$Shortcut.IconLocation = "C:\Users\52602\ai-sales-web\images\icon.ico, 0"
$Shortcut.Save()
Write-Host "Shortcut created on OneDrive Desktop!"

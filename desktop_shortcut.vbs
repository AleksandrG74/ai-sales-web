Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\AI Sales Agent.lnk")
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "C:\Users\52602\ai-sales-web\run_agent.bat"
oLink.WorkingDirectory = "C:\Users\52602\ai-sales-web"
oLink.Description = "AI Sales Agent"
oLink.IconLocation = "C:\Users\52602\ai-sales-web\icon.ico"
oLink.Save

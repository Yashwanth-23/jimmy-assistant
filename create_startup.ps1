$startup = [Environment]::GetFolderPath('Startup')
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$startup\Jimmy.lnk")
$sc.TargetPath = 'C:\Users\vasir\Downloads\assistant\start_jimmy.vbs'
$sc.WorkingDirectory = 'C:\Users\vasir\Downloads\assistant'
$sc.Description = 'Jimmy Voice Assistant'
$sc.Save()
Write-Host "Shortcut created at: $startup\Jimmy.lnk"

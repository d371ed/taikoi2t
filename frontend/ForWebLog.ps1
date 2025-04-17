$files = Get-ChildItem -Path .\* -File -Include *.png, *.jpg | ForEach-Object { $_.Name }
$command = ".\taikoi2t.exe -d .\students.csv " + ($files -join " ")
Invoke-Expression $command | Set-Clipboard

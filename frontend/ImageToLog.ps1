$app_path = [System.Environment]::GetEnvironmentVariable("APP_PATH", "Process")
$run_options = [System.Environment]::GetEnvironmentVariable("RUN_OPTIONS", "Process")
$out_file = [System.Environment]::GetEnvironmentVariable("OUT_FILE", "Process")

$files = Get-ChildItem -Path .\* -File -Include *.png, *.jpg | ForEach-Object { $_.Name }
$command = "poetry --project $($app_path) run main -d .\students.csv $($run_options) " + ($files -join " ")
$data = Invoke-Expression $command

$data | Out-File -FilePath $out_file -Encoding utf8
$data | Set-Clipboard

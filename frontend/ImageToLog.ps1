$appPath = [System.Environment]::GetEnvironmentVariable("APP_PATH", "Process")
$runOptions = [System.Environment]::GetEnvironmentVariable("RUN_OPTIONS", "Process")
$outFile = [System.Environment]::GetEnvironmentVariable("OUT_FILE", "Process")
$backupDir = [System.Environment]::GetEnvironmentVariable("BACKUP_DIR", "Process")

$files = Get-ChildItem -Path .\* -File -Include *.png, *.jpg
$filenames = $files | ForEach-Object { $_.Name }
$command = "poetry --project $($appPath) run main -d .\students.csv $($runOptions) " + ($filenames -join " ")
$result = Invoke-Expression $command

$result | Out-File -FilePath $outFile -Encoding utf8
$result | Set-Clipboard

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir
}
foreach ($file in $files) {
    Move-Item -Path $file.FullName -Destination $backupDir
}

$imageFetchDir = [System.Environment]::GetEnvironmentVariable("IMAGE_FETCH_DIR", "Process")
$targetTimeMin = [System.Environment]::GetEnvironmentVariable("TARGET_TIME_MIN", "Process")
$appDir = [System.Environment]::GetEnvironmentVariable("APP_DIR", "Process")
$dictionaryCsv = [System.Environment]::GetEnvironmentVariable("DICTIONARY_CSV", "Process")
$runOptions = [System.Environment]::GetEnvironmentVariable("RUN_OPTIONS", "Process")
$outFile = [System.Environment]::GetEnvironmentVariable("OUT_FILE", "Process")
$backupDir = [System.Environment]::GetEnvironmentVariable("BACKUP_DIR", "Process")

$timeThreshold = (Get-Date).AddMinutes(-$targetTimeMin)
$fetchTargetFiles = Get-ChildItem -Path "$($imageFetchDir)\*" -File -Include *.png, *.jpg | 
    Where-Object { $_.CreationTime -gt $timeThreshold }

$currentDir = $PWD.Path
foreach ($file in $fetchTargetFiles) {
    Move-Item -Path $file.FullName -Destination $currentDir
}

# both images in the current directory already and fetched ones
$files = Get-ChildItem -Path "$($currentDir)\*" -File -Include *.png, *.jpg | Sort-Object LastWriteTime
$filenames = $files | ForEach-Object { $_.Name }
$filenames | Write-Output

$command = "poetry --project $($appDir) run main -d $($dictionaryCsv) $($runOptions) " + ($filenames -join " ")
$result = Invoke-Expression $command

$result | Out-File -FilePath $outFile -Encoding utf8
$result | Set-Clipboard

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir
}
foreach ($file in $files) {
    Move-Item -Path $file.FullName -Destination $backupDir
}

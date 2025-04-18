@echo off

set APP_PATH=..
set RUN_OPTIONS=
set OUT_FILE=.\result.tsv
set BACKUP_DIR=.\backup

call .\user-settings.bat

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

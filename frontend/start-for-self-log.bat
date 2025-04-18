@echo off

set APP_PATH=..
set OUT_FILE=.\result.tsv
set BACKUP_DIR=.\backup

call .\user-settings.bat

set RUN_OPTIONS=--opponent
set IMAGE_FETCH_DIR=%SELF_FETCH_DIR%

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

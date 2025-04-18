@echo off

set APP_PATH=..
set RUN_OPTIONS=--opponent
set OUT_FILE=.\result.tsv
set BACKUP_DIR=.\backup

call .\user-settings.bat

set IMAGE_FETCH_DIR=%SELF_FETCH_DIR%

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

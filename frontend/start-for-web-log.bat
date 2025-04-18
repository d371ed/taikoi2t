@echo off

set APP_PATH=..
set RUN_OPTIONS=
set OUT_FILE=.\result.tsv
set BACKUP_DIR=.\backup

call .\user-settings.bat

set IMAGE_FETCH_DIR=%WEB_FETCH_DIR%

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

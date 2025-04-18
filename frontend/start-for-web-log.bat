@echo off

set APP_PATH=..
set DICTIONARY_CSV=..\students.csv
set RUN_OPTIONS=
set BACKUP_DIR=.\backup

call .\user-settings.bat

set OUT_FILE=.\result.tsv
set IMAGE_FETCH_DIR=%WEB_FETCH_DIR%

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

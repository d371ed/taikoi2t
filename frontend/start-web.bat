@echo off

set APP_DIR=..
set DICTIONARY_CSV=..\students.csv
set OUT_FILE=.\result.tsv
set BACKUP_DIR=.\backup

call .\user-settings.bat

set TARGET_TIME_MIN=10
set RUN_OPTIONS=
set IMAGE_FETCH_DIR=%WEB_FETCH_DIR%

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

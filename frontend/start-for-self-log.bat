@echo off

set APP_PATH=..
set DICTIONARY_CSV=..\students.csv
set OUT_FILE=.\result.tsv
set BACKUP_DIR=.\backup

call .\user-settings.bat

set TARGET_TIME_MIN=5
set RUN_OPTIONS=--opponent
set IMAGE_FETCH_DIR=%SELF_FETCH_DIR%

powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

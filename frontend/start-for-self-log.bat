@echo off
set APP_PATH=..
set RUN_OPTIONS=--opponent
set OUT_FILE=result.tsv
powershell -ExecutionPolicy Bypass -File ImageToLog.ps1

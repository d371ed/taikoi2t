@echo off
set BACKUP_DIR=.\backup
call .\user-settings.bat

echo Are you sure you want to delete the contents of %BACKUP_DIR%? (yes / no)
set /p CONFIRM=">> "

if "%CONFIRM%"=="yes" (
    del /Q "%BACKUP_DIR%\*"
    echo Deletion completed
) else (
    echo Deletion canceled
)

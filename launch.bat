@echo off
echo === launch Astra ===
cd /d "ВАШ ПУТЬ ДО astra-voice-assistant"
echo Folder: %CD%
echo.

:: Активируем виртуальное окружение
call venv\Scripts\activate.bat

echo.
echo Starting application...
python -m src.main
pause
@echo off
echo Move to dir
cd c:\project\parser-1c
if %errorlevel% neq 0 (
    echo Ошибка при переходе в каталог
    pause
    exit /b %errorlevel%
)

echo Install env
call env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Ошибка при активации виртуального окружения
    pause
    exit /b %errorlevel%
)

echo Start parcer
python main.py
if %errorlevel% neq 0 (
    echo Ошибка при запуске скрипта Python
    pause
    exit /b %errorlevel%
)

pause
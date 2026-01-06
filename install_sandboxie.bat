@echo off
REM Скрипт установки Sandboxie
REM Запускать от имени администратора!

echo ========================================
echo   Установка Sandboxie для Dota 5 Bots
echo ========================================

REM Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ОШИБКА: Запустите от имени администратора!
    echo Правой кнопкой -> "Запуск от имени администратора"
    pause
    exit /b 1
)

echo Проверяю установлен ли Sandboxie...
if exist "C:\Sandboxie\Start.exe" (
    echo Sandboxie уже установлен.
    goto :CONFIGURE
)

echo Устанавливаю Sandboxie...
if not exist "installers\Sandboxie-Plus-x64-v1.11.4.exe" (
    echo ОШИБКА: Установщик не найден!
    echo Скачайте Sandboxie-Plus с:
    echo https://sandboxie-plus.com/downloads/
    pause
    exit /b 1
)

REM Установка в тихом режиме
"installers\Sandboxie-Plus-x64-v1.11.4.exe" /S
if %errorLevel% neq 0 (
    echo ОШИБКА: Установка не удалась!
    pause
    exit /b 1
)

echo Sandboxie успешно установлен!

:CONFIGURE
echo Настраиваю Sandboxie для Dota 2...

REM Создаем конфигурацию для Dota 2
echo. >> "C:\Sandboxie\Sandboxie.ini"
echo [Dota2BoxSettings] >> "C:\Sandboxie\Sandboxie.ini"
echo Enabled=y >> "C:\Sandboxie\Sandboxie.ini"
echo ConfigLevel=7 >> "C:\Sandboxie\Sandboxie.ini"
echo AutoRecover=y >> "C:\Sandboxie\Sandboxie.ini"
echo. >> "C:\Sandboxie\Sandboxie.ini"
echo [ProcessGroup_Dota2] >> "C:\Sandboxie\Sandboxie.ini"
echo ImageName=steam.exe >> "C:\Sandboxie\Sandboxie.ini"
echo ImageName=dota2.exe >> "C:\Sandboxie\Sandboxie.ini"
echo ImageName=gameoverlayui.exe >> "C:\Sandboxie\Sandboxie.ini"
echo. >> "C:\Sandboxie\Sandboxie.ini"
echo [Internet_Dota2] >> "C:\Sandboxie\Sandboxie.ini"
echo Enabled=y >> "C:\Sandboxie\Sandboxie.ini"

REM Настройка брандмауэра
echo Настраиваю брандмауэр...
netsh advfirewall firewall add rule name="Sandboxie" dir=in action=allow program="C:\Sandboxie\SbieSvc.exe" enable=yes
netsh advfirewall firewall add rule name="Steam in Sandboxie" dir=in action=allow program="C:\Sandboxie\Start.exe" enable=yes

echo ========================================
echo   Установка завершена успешно!
echo ========================================
echo.
echo Дальнейшие шаги:
echo 1. Создайте 5 Steam аккаунтов для ботов
echo 2. Настройте семейный доступ или отдельные аккаунты
echo 3. Запустите setup_accounts.py для настройки аккаунтов
echo.
pause
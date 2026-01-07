# scripts/create_sandboxes_manual.py
import json
import os
from pathlib import Path


def create_sandbox_configs():
    """Создание конфигурационных файлов для ручной настройки"""
    print("=" * 60)
    print("Создание конфигов для Sandboxie-Plus")
    print("=" * 60)

    # Папка для конфигов
    config_dir = Path("config/sandbox_configs")
    config_dir.mkdir(parents=True, exist_ok=True)

    # Цвета для разных ботов
    colors = [
        "#00FF00",  # Зеленый
        "#0000FF",  # Синий
        "#00FFFF",  # Голубой
        "#FF00FF",  # Пурпурный
        "#FFFF00"  # Желтый
    ]

    # Создаем конфиги для каждого бота
    for i in range(1, 6):
        sandbox_name = f"DOTA_BOT_{i}"
        color = colors[i - 1]

        config_content = f"""; Конфигурация для DOTA 2 Bot {i}
; Имя песочницы: {sandbox_name}
; Цвет границы: {color}

[{sandbox_name}]
Enabled=y
ConfigLevel=7
BorderColor={color},ttl
BoxNameTitle=y
BorderSize=4,4,4,4
FileRootPath=%USER%\\Desktop\\Sandboxes\\{sandbox_name}

; Разрешенные пути (Steam)
OpenFilePath=%SteamPath%\\steam.exe
OpenFilePath=%SteamPath%\\steamapps\\common\\dota 2 beta
OpenFilePath=%SteamPath%\\userdata

; Графика и звук
OpenClsid={{60B0E4A0-EDCF-11CF-BC10-00AA00AC74F6}}
OpenClsid={{22D6F304-B0F6-11D0-94AB-0080C74C7E95}}
OpenWinClass=Valve001
OpenWinClass=SDL_app

; Сеть
OpenPipe=Steam*
OpenClsid={{5C6698D9-7BE4-4122-8EC5-291D84DBD4A0}}

; Восстановление
AutoRecover=y
RecoverFolder=%Desktop%\\{sandbox_name}-Recovered
LingerProcess=steam.exe
LingerProcess=dota2.exe

; Производительность
MemoryQuota=2048M
ProcessLimit=30

; Изоляция
BlockNetworkFiles=y
ClosedFilePath=*
ClosedKeyPath=*
OpenKeyPath=HKEY_CURRENT_USER\\Software\\Valve
"""

        config_file = config_dir / f"{sandbox_name}.ini"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)

        print(f"✓ Создан конфиг: {sandbox_name}.ini")

    # Создаем инструкцию
    print("\n" + "=" * 60)
    print("📋 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ SANDBOXIE-PLUS")
    print("=" * 60)
    print("\n1. Откройте Sandboxie-Plus.exe")
    print("2. Для создания песочниц выполните:")
    print("\n   ПРАВАЯ КНОПКА на 'Sandbox' -> 'Create New Sandbox'")
    print("\n3. Создайте 5 песочниц с именами:")
    print("   - DOTA_BOT_1")
    print("   - DOTA_BOT_2")
    print("   - DOTA_BOT_3")
    print("   - DOTA_BOT_4")
    print("   - DOTA_BOT_5")
    print("\n4. Для каждой песочницы:")
    print("   a. ПРАВАЯ КНОПКА на песочнице -> 'Sandbox Settings'")
    print("   b. Перейдите на вкладку 'Options'")
    print("   c. Нажмите 'Import from INI file...'")
    print("   d. Выберите соответствующий файл из config/sandbox_configs/")
    print("   e. Нажмите 'Apply' и 'OK'")
    print("\n5. Импортируйте конфиги в Sandboxie.ini:")
    print("   - Откройте 'Global Settings' -> 'Edit Configuration'")
    print("   - Добавьте в начало: Include=C:\\path\\to\\project\\config\\sandbox_configs\\DOTA_BOT_*.ini")
    print("\n6. Альтернативно, скопируйте конфиги вручную:")
    print("   - Скопируйте все *.ini файлы в:")
    print("     C:\\Program Files\\Sandboxie-Plus\\")
    print("\n7. После настройки запустите тест:")
    print("   python test_launch.py")
    print("=" * 60)

    # Создаем batch файл для быстрого копирования
    batch_content = """@echo off
echo Копирование конфигов Sandboxie...
echo.

REM Копируем конфиги в папку Sandboxie-Plus
xcopy "%~dp0config\\sandbox_configs\\*.ini" "C:\\Program Files\\Sandboxie-Plus\\" /Y

echo.
echo Конфиги скопированы!
echo Откройте Sandboxie-Plus и перезапустите его.
pause
"""

    batch_file = Path("copy_sandbox_configs.bat")
    with open(batch_file, 'w') as f:
        f.write(batch_content)

    print(f"\n✓ Создан batch файл: {batch_file}")
    print("   Запустите его от имени администратора для копирования конфигов.")

    return True


def main():
    try:
        create_sandbox_configs()
        return 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
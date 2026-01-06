#!/usr/bin/env python3
"""
Скрипт установки и настройки Sandboxie
Запускать от имени администратора!
"""

import os
import sys
import subprocess
import ctypes
import winreg
from pathlib import Path


def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def check_sandboxie_installed():
    """Проверка установлен ли Sandboxie"""
    install_paths = [
        r"C:\Program Files\Sandboxie",
        r"C:\Program Files (x86)\Sandboxie",
        r"C:\Sandboxie"
    ]

    for path in install_paths:
        if os.path.exists(os.path.join(path, "Start.exe")):
            return path
    return None


def install_sandboxie():
    """Установка Sandboxie"""
    print("[Setup] Установка Sandboxie...")

    # Путь к установщику (нужно скачать заранее)
    installer_path = "installers/Sandboxie-Plus-x64-v1.11.4.exe"

    if not os.path.exists(installer_path):
        print(f"[Setup] Установщик не найден: {installer_path}")
        print("Скачайте Sandboxie-Plus с https://sandboxie-plus.com/")
        return False

    try:
        # Запуск установщика
        subprocess.run([installer_path, "/S"], check=True)
        print("[Setup] Sandboxie установлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[Setup] Ошибка установки: {e}")
        return False


def configure_sandboxie():
    """Настройка Sandboxie для работы с Dota 2"""
    print("[Setup] Настройка Sandboxie...")

    sandboxie_path = check_sandboxie_installed()
    if not sandboxie_path:
        print("[Setup] Sandboxie не установлен!")
        return False

    # Создаем конфигурационные файлы для 5 окон
    config_dir = Path(sandboxie_path) / "Sandboxie.ini"

    if not os.path.exists(config_dir):
        print(f"[Setup] Конфиг не найден: {config_dir}")
        return False

    # Добавляем настройки для Dota 2
    dota_settings = """

[Dota2BoxSettings]
Enabled=y
ConfigLevel=7
AutoRecover=y

[ProcessGroup_Dota2]
ImageName=steam.exe
ImageName=dota2.exe
ImageName=gameoverlayui.exe

[Internet_Dota2]
Enabled=y

[FilePaths_Dota2]
C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta=-
C:\\Program Files (x86)\\Steam\\config=-
C:\\Program Files (x86)\\Steam\\userdata=-
"""

    try:
        # Добавляем настройки в конфиг
        with open(config_dir, 'a', encoding='utf-8') as f:
            f.write(dota_settings)

        print("[Setup] Настройки Sandboxie добавлены")
        return True

    except Exception as e:
        print(f"[Setup] Ошибка настройки: {e}")
        return False


def configure_windows_firewall():
    """Настройка брандмауэра Windows для Sandboxie"""
    print("[Setup] Настройка брандмауэра...")

    try:
        # Разрешаем Sandboxie в брандмауэре
        firewall_rules = [
            # Правило для Sandboxie
            'netsh advfirewall firewall add rule name="Sandboxie" '
            'dir=in action=allow program="C:\\Sandboxie\\SbieSvc.exe" enable=yes',

            # Правило для Steam в Sandboxie
            'netsh advfirewall firewall add rule name="Steam in Sandboxie" '
            'dir=in action=allow program="C:\\Sandboxie\\Start.exe" enable=yes'
        ]

        for rule in firewall_rules:
            subprocess.run(rule, shell=True, check=False)

        print("[Setup] Брандмауэр настроен")
        return True

    except Exception as e:
        print(f"[Setup] Ошибка настройки брандмауэра: {e}")
        return False


def install_prerequisites():
    """Установка необходимых компонентов"""
    print("[Setup] Проверка зависимостей...")

    prerequisites = [
        ("Microsoft Visual C++ Redistributable",
         "installers/vcredist_x64.exe", "/install", "/quiet", "/norestart"),
    ]

    for name, installer, *args in prerequisites:
        if os.path.exists(installer):
            print(f"[Setup] Устанавливаю {name}...")
            try:
                subprocess.run([installer, *args], check=True)
            except:
                print(f"[Setup] Ошибка установки {name}")

    print("[Setup] Зависимости проверены")


def main():
    """Основная функция настройки"""
    print("=" * 50)
    print("Настройка Sandboxie для Dota 5 Bot System")
    print("=" * 50)

    if not is_admin():
        print("ОШИБКА: Запустите скрипт от имени администратора!")
        print("Нажмите правой кнопкой -> Запуск от имени администратора")
        input("Нажмите Enter для выхода...")
        return False

    print("[Setup] Начинаю настройку...")

    # 1. Проверяем установлен ли Sandboxie
    sandboxie_path = check_sandboxie_installed()
    if not sandboxie_path:
        print("[Setup] Sandboxie не найден")
        choice = input("Установить Sandboxie? (y/n): ")
        if choice.lower() == 'y':
            if not install_sandboxie():
                return False
            sandboxie_path = check_sandboxie_installed()
        else:
            return False

    print(f"[Setup] Sandboxie найден: {sandboxie_path}")

    # 2. Устанавливаем зависимости
    install_prerequisites()

    # 3. Настраиваем Sandboxie
    if not configure_sandboxie():
        print("[Setup] Ошибка настройки Sandboxie")
        return False

    # 4. Настраиваем брандмауэр
    configure_windows_firewall()

    print("\n" + "=" * 50)
    print("НАСТРОЙКА ЗАВЕРШЕНА!")
    print("=" * 50)
    print("\nДополнительные шаги:")
    print("1. Создайте 5 Steam аккаунтов для ботов")
    print("2. Добавьте аккаунты в config/accounts.json")
    print("3. Запустите тестовый запуск: python test_launch.py")

    input("\nНажмите Enter для выхода...")
    return True


if __name__ == "__main__":
    main()
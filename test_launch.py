#!/usr/bin/env python3
"""
Тестовый запуск системы
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_single_instance_no_kill():
    """Тест запуска одного окна"""
    print("Тест 1: Запуск одного экземпляра Dota 2...")

    try:
        from core.game_launcher import GameLauncher
        launcher = GameLauncher()

        success = launcher.launch_single(0)

        if success:
            print("✓ Тестовое окно запущено")

            # Ждем 30 секунд для проверки
            print("\n" + "=" * 60)
            print("✅ Steam должен запуститься и остаться открытым!")
            print("Проверьте:")
            print("1. Открылось ли окно Steam?")
            print("2. Вошел ли Steam в аккаунт автоматически?")
            print("3. Запустилась ли Dota 2?")
            print("\nОжидаю 30 секунд для проверки...")

            for i in range(30, 0, -1):
                print(f"Осталось: {i} секунд", end="\r")
                time.sleep(1)
            print()

            # Не убиваем процессы автоматически
            print("\n" + "=" * 60)
            print("Тест завершен, процессы НЕ были остановлены!")
            print("\nЧто делать дальше:")
            print("1. Если все работает - отлично! Система готова.")
            print("2. Если Steam не вошел - проверьте аккаунты в config/accounts.json")
            print("3. Если нужно остановить процессы, запустите: python stop_all.py")
            print("\nДля выхода из теста нажмите Ctrl+C")

            # Ждем, пока пользователь сам не закроет
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nОстановка процессов по запросу пользователя...")
                launcher.controller.kill_all()
                print("Все процессы остановлены")

            return True
        else:
            print("✗ Ошибка запуска")
            return False

    except Exception as e:
        print(f"✗ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def quick_sandboxie_test():
    """Быстрая проверка Sandboxie без запуска Dota"""
    print("\nТест 2: Быстрая проверка Sandboxie...")

    try:
        from core.sandbox_controller import SandboxController
        controller = SandboxController()

        print(f"✓ Sandboxie найден: {controller.sandboxie_path}")

        # Проверяем песочницы
        for i in range(1, 4):
            sandbox_name = f"DOTA_BOT_{i}"
            if controller.is_sandbox_exists(sandbox_name):
                print(f"✓ {sandbox_name} найдена")
            else:
                print(f"⚠ {sandbox_name} не найдена")

        return True

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def check_accounts():
    """Проверка аккаунтов"""
    print("\nТест 3: Проверка аккаунтов...")

    try:
        import json
        with open("config/accounts.json", "r") as f:
            accounts = json.load(f)

        if accounts and len(accounts) > 0:
            print(f"✓ Найдено аккаунтов: {len(accounts)}")
            for i, acc in enumerate(accounts[:3], 1):
                print(f"  {i}. {acc.get('username', 'N/A')}")
            if len(accounts) > 3:
                print(f"  ... и еще {len(accounts) - 3}")
            return True
        else:
            print("✗ Файл аккаунтов пуст")
            return False

    except Exception as e:
        print(f"✗ Ошибка чтения аккаунтов: {e}")
        return False


def main():
    print("=" * 60)
    print("ТЕСТ ЗАПУСКА")
    print("=" * 60)
    print("\n⚠ Этот тест не будет автоматически закрывать Steam")

    # Проверка наличия конфигов
    print("\nПроверка конфигурационных файлов...")
    required_files = [
        ("config/accounts.json", True),
        ("config/sandbox_configs/DOTA_BOT_1.ini", True),
        ("core/game_launcher.py", True),
    ]

    for file_path, required in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            if required:
                print(f"✗ {file_path} - отсутствует!")
                return 1
            else:
                print(f"⚠ {file_path} - отсутствует")

    # Проверяем аккаунты
    accounts_ok = check_accounts()

    # Быстрая проверка Sandboxie
    sandboxie_ok = quick_sandboxie_test()

    print("\n" + "=" * 60)
    print("Готов к запуску теста?")
    print("-" * 60)

    response = input("Запустить тест? (y/n): ").strip().lower()
    if response != 'y':
        print("Тест отменен.")
        return 0

    # Запускаем основной тест
    test_result = test_single_instance_no_kill()

    print("\n" + "=" * 60)
    if test_result:
        print("✅ ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        print("\nСтатус системы:")
        print(f"1. Аккаунты: {'✓' if accounts_ok else '✗'}")
        print(f"2. Sandboxie: {'✓' if sandboxie_ok else '✗'}")
        print(f"3. Запуск: {'✓' if test_result else '✗'}")

        if accounts_ok and sandboxie_ok and test_result:
            print("\n🎉 СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
            return 0
        else:
            print("\n⚠ Есть проблемы, которые нужно исправить.")
            return 1
    else:
        print("❌ ТЕСТ НЕ ПРОШЕЛ")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nТест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
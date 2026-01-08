#!/usr/bin/env python3
"""
Тестовый запуск всех 5 окон системы ботов Dota 2
"""

import sys
import time
import threading
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent))


class TestAllInstances:
    """Класс для тестирования всех окон одновременно"""

    def __init__(self):
        self.launcher = None
        self.results = {}
        self.active_bots = []

    def test_all_instances_no_kill(self) -> Dict[int, bool]:
        """Тест запуска всех 5 окон одновременно"""
        print("Тест 1: Запуск всех 5 экземпляров Dota 2...")

        try:
            from core.game_launcher import GameLauncher
            self.launcher = GameLauncher()

            # Создаем пул потоков для параллельного запуска
            threads = []
            for bot_id in range(5):
                thread = threading.Thread(
                    target=self._launch_single_bot,
                    args=(bot_id,)
                )
                threads.append(thread)
                thread.start()
                # Небольшая задержка между запусками
                time.sleep(2)

            # Ждем завершения всех потоков
            for thread in threads:
                thread.join()

            print("\n" + "=" * 60)
            print("✅ Все окна должны быть запущены!")
            print("Проверьте на экране:")
            print("1. Открылись ли 5 окон Steam/Dota 2?")
            print("2. Все ли окна в разных песочницах?")
            print("3. Вошли ли все аккаунты автоматически?")
            print("\nОжидаю 45 секунд для проверки стабильности...")

            for i in range(45, 0, -1):
                print(f"Осталось: {i} секунд", end="\r")
                time.sleep(1)
            print()

            return self.results

        except Exception as e:
            print(f"✗ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _launch_single_bot(self, bot_id: int):
        """Запуск одного бота в отдельном потоке"""
        try:
            print(f"  Запуск бота {bot_id + 1}...")
            success = self.launcher.launch_single(bot_id)

            if success:
                print(f"    ✓ Бот {bot_id + 1} запущен")
                self.results[bot_id] = True
                self.active_bots.append(bot_id)
            else:
                print(f"    ✗ Ошибка запуска бота {bot_id + 1}")
                self.results[bot_id] = False

        except Exception as e:
            print(f"    ✗ Исключение при запуске бота {bot_id + 1}: {e}")
            self.results[bot_id] = False

    def stop_all(self):
        """Остановка всех процессов"""
        if self.launcher and hasattr(self.launcher, 'controller'):
            print("\nОстановка всех процессов...")
            self.launcher.controller.kill_all()
            print("Все процессы остановлены")


def test_sandboxie_all_instances():
    """Проверка всех песочниц Sandboxie"""
    print("\nТест 2: Проверка всех песочниц Sandboxie...")

    try:
        from core.sandbox_controller import SandboxController
        controller = SandboxController()

        print(f"✓ Sandboxie найден: {controller.sandboxie_path}")

        # Проверяем все 5 песочниц
        results = {}
        for i in range(1, 6):
            sandbox_name = f"DOTA_BOT_{i}"
            if controller.is_sandbox_exists(sandbox_name):
                print(f"    ✓ Песочница {sandbox_name} найдена")
                results[i] = True
            else:
                print(f"    ✗ Песочница {sandbox_name} не найдена!")
                results[i] = False

        return results

    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return {}


def check_all_accounts() -> Dict[int, bool]:
    """Проверка всех 5 аккаунтов"""
    print("\nТест 3: Проверка аккаунтов для 5 ботов...")

    try:
        import json
        with open("config/accounts.json", "r") as f:
            accounts = json.load(f)

        results = {}
        if accounts and len(accounts) >= 5:
            print(f"✓ Найдено аккаунтов: {len(accounts)} (нужно минимум 5)")

            for i in range(5):
                if i < len(accounts):
                    acc = accounts[i]
                    username = acc.get('username', 'N/A')
                    print(f"    Бот {i + 1}: {username}")

                    # Проверяем наличие обязательных полей
                    required = ['username', 'password']
                    missing = [field for field in required if field not in acc]

                    if missing:
                        print(f"      ⚠ Отсутствуют поля: {missing}")
                        results[i] = False
                    else:
                        results[i] = True
                else:
                    print(f"    ✗ Бот {i + 1}: нет аккаунта!")
                    results[i] = False

            if len(accounts) > 5:
                print(f"    ... и еще {len(accounts) - 5} аккаунтов в запасе")
        else:
            print(f"✗ Недостаточно аккаунтов! Найдено: {len(accounts)}, нужно: 5")
            for i in range(5):
                results[i] = False

        return results

    except Exception as e:
        print(f"✗ Ошибка чтения аккаунтов: {e}")
        return {i: False for i in range(5)}


def check_system_resources():
    """Проверка системных ресурсов"""
    print("\nТест 4: Проверка системных ресурсов...")

    try:
        import psutil

        # Проверка памяти
        memory = psutil.virtual_memory()
        print(f"    Общая память: {memory.total / (1024 ** 3):.1f} GB")
        print(f"    Доступно: {memory.available / (1024 ** 3):.1f} GB")

        # Проверка CPU
        cpu_count = psutil.cpu_count()
        print(f"    Ядер CPU: {cpu_count}")

        # Рекомендации
        print("\n    Рекомендации:")
        if memory.total < 16 * 1024 ** 3:  # Меньше 16GB
            print("    ⚠ Мало оперативной памяти! 5 окон Dota 2 могут не запуститься.")
        else:
            print("    ✓ Оперативной памяти достаточно")

        if cpu_count < 8:
            print("    ⚠ Меньше 8 ядер CPU, возможны лаги.")
        else:
            print("    ✓ CPU достаточно мощный")

        return True

    except ImportError:
        print("    ⚠ Библиотека psutil не установлена. Пропускаем проверку.")
        print("    Установите: pip install psutil")
        return None
    except Exception as e:
        print(f"    ⚠ Ошибка проверки ресурсов: {e}")
        return None


def print_summary(account_results, sandbox_results, launch_results):
    """Вывод сводки результатов"""
    print("\n" + "=" * 60)
    print("СВОДКА РЕЗУЛЬТАТОВ")
    print("=" * 60)

    headers = ["Бот", "Аккаунт", "Песочница", "Запуск", "Статус"]
    print(f"{headers[0]:<6} {headers[1]:<15} {headers[2]:<12} {headers[3]:<8} {headers[4]}")
    print("-" * 60)

    total_success = 0
    for i in range(5):
        account_ok = account_results.get(i, False)
        sandbox_ok = sandbox_results.get(i, False)
        launch_ok = launch_results.get(i, False)

        if account_ok and sandbox_ok and launch_ok:
            status = "✅ ГОТОВ"
            total_success += 1
        else:
            status = "❌ ОШИБКА"

        print(f"Бот {i + 1:<2} {'✓' if account_ok else '✗':<14} "
              f"{'✓' if sandbox_ok else '✗':<11} "
              f"{'✓' if launch_ok else '✗':<7} {status}")

    print("-" * 60)
    print(f"ИТОГО: {total_success}/5 успешных ботов")

    if total_success == 5:
        print("\n🎉 ВСЕ 5 БОТОВ ГОТОВЫ К РАБОТЕ!")
        return True
    elif total_success >= 3:
        print(f"\n⚠ Запущено {total_success}/5 ботов. Проверьте ошибки.")
        return False
    else:
        print(f"\n❌ Критически мало ботов запущено: {total_success}/5")
        return False


def main():
    print("=" * 60)
    print("ПОЛНЫЙ ТЕСТ ЗАПУСКА 5 ОКОН БОТОВ DOTA 2")
    print("=" * 60)
    print("\n⚠ Этот тест запустит 5 окон Dota 2 одновременно!")
    print("⚠ Убедитесь, что у вас достаточно системных ресурсов.")
    print("⚠ Процессы не будут автоматически закрыты.\n")

    # Проверка наличия конфигов
    print("Проверка конфигурационных файлов...")
    required_files = [
        ("config/accounts.json", True),
        ("config/sandbox_configs/DOTA_BOT_1.ini", True),
        ("config/sandbox_configs/DOTA_BOT_2.ini", True),
        ("config/sandbox_configs/DOTA_BOT_3.ini", True),
        ("config/sandbox_configs/DOTA_BOT_4.ini", True),
        ("config/sandbox_configs/DOTA_BOT_5.ini", True),
        ("core/game_launcher.py", True),
    ]

    all_files_ok = True
    for file_path, required in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            if required:
                print(f"✗ {file_path} - отсутствует!")
                all_files_ok = False
            else:
                print(f"⚠ {file_path} - отсутствует")

    if not all_files_ok:
        print("\n❌ Исправьте отсутствующие файлы перед запуском теста.")
        return 1

    # Проверка системных ресурсов
    check_system_resources()

    # Проверяем аккаунты
    account_results = check_all_accounts()

    # Проверяем песочницы
    sandbox_results = test_sandboxie_all_instances()

    print("\n" + "=" * 60)
    print("ВНИМАНИЕ: Запуск 5 окон Dota 2 потребляет много ресурсов!")
    print("=" * 60)

    response = input("\nПродолжить с запуском теста? (y/n): ").strip().lower()
    if response != 'y':
        print("Тест отменен.")
        return 0

    # Запускаем основной тест
    tester = TestAllInstances()

    try:
        launch_results = tester.test_all_instances_no_kill()

        # Выводим сводку
        all_success = print_summary(account_results, sandbox_results, launch_results)

        print("\n" + "=" * 60)
        print("Тест завершен, процессы НЕ были остановлены!")
        print("\nЧто делать дальше:")
        print("1. Если все работает - система готова к бою!")
        print("2. Проверьте работу в диспетчере задач (5 процессов dota2.exe)")
        print("3. Если нужно остановить процессы, нажмите Ctrl+C")
        print("\nДля выхода из теста и остановки процессов нажмите Ctrl+C")

        # Ждем, пока пользователь сам не закроет
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nЗапрос на остановку всех процессов...")
            tester.stop_all()
            print("Тест завершен пользователем.")

        return 0 if all_success else 1

    except KeyboardInterrupt:
        print("\n\nТест прерван пользователем до завершения запуска.")
        if tester.launcher:
            tester.stop_all()
        return 1
    except Exception as e:
        print(f"\n❌ Критическая ошибка во время теста: {e}")
        import traceback
        traceback.print_exc()
        if tester.launcher:
            tester.stop_all()
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
import sys
import os
from pathlib import Path
import threading
import time
import logging

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from core.game_launcher import GameLauncher
from ai.bot_ai import DotaBotAI
from utils.input_simulator import InputSimulator


def setup_logging():
    """Настройка системы логирования"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "dota_bot_system.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def main():
    logger = setup_logging()

    print("=" * 60)
    print("DOTA 2 BOT SYSTEM - Week 1")
    print("=" * 60)

    # Инициализация компонентов
    try:
        launcher = GameLauncher()
        logger.info("Система инициализирована")

        while True:
            print("\nВыберите действие:")
            print("1. Запустить тестовое окно")
            print("2. Запустить полную команду (5 окон)")
            print("3. Запустить бота AI")
            print("4. Показать статус")
            print("5. Остановить все процессы")
            print("0. Выход")

            choice = input("\nВаш выбор: ").strip()

            if choice == "1":
                logger.info("Запуск тестового окна...")
                if launcher.launch_single_instance(0, (0, 0, 1024, 768)):
                    print("✓ Тестовое окно запущено")
                else:
                    print("✗ Ошибка запуска")

            elif choice == "2":
                logger.info("Запуск полной команды...")
                result = launcher.launch_full_team(5)
                print(f"Результат: {result['status']}")

            elif choice == "3":
                # Запуск AI бота для первого окна
                print("Запуск AI бота...")
                bot = DotaBotAI(window_region=(0, 0, 1024, 768))

                # Запуск в отдельном потоке
                bot_thread = threading.Thread(
                    target=bot.run,
                    daemon=True
                )
                bot_thread.start()
                print("Бот запущен. Нажмите Ctrl+C в этом окне для остановки.")

                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nОстановка бота...")

            elif choice == "4":
                status = launcher.get_status()
                print(f"\nСтатус системы:")
                print(f"Всего процессов: {status['total_processes']}")
                print(f"Доступно аккаунтов: {status['accounts']}")

                for proc in status['process_info']:
                    print(f"  - {proc['account']}: PID={proc['pid']}, "
                          f"Статус={proc['status']}, "
                          f"Память={proc['memory']}MB")

            elif choice == "5":
                print("Остановка всех процессов...")
                launcher.sandbox_controller.kill_all()

            elif choice == "0":
                print("Выход...")
                launcher.sandbox_controller.kill_all()
                break

            else:
                print("Неверный выбор")

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"Ошибка: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
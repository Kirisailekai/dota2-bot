# main.py - главный управляющий скрипт
"""
Основной скрипт для запуска системы ботов
"""

import sys
import time
import signal
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DotaBotSystem:
    """Основной класс системы управления ботами"""

    def __init__(self):
        self.game_launcher = None
        self.process_monitor = None
        self.ai_controllers = []
        self.is_running = False

    def initialize(self):
        """Инициализация системы"""
        logger.info("Инициализация системы...")

        try:
            # Импортируем модули
            from core.game_launcher import GameLauncher
            from core.process_monitor import ProcessMonitor
            from ai.bot_ai import BotAI

            # Инициализируем компоненты
            self.game_launcher = GameLauncher()
            self.process_monitor = ProcessMonitor()

            logger.info("✓ Система инициализирована")
            return True

        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            return False

    def start_system(self, bot_count: int = 5):
        """Запуск всей системы"""
        if not self.initialize():
            logger.error("Не удалось инициализировать систему")
            return False

        logger.info(f"Запуск системы с {bot_count} ботами...")

        # 1. Запускаем игровые клиенты
        launch_result = self.game_launcher.launch_team(bot_count)

        if launch_result["status"] == "error":
            logger.error(f"Ошибка запуска: {launch_result.get('message', 'Unknown')}")
            return False

        logger.info(f"Запущено {launch_result['successful']}/{bot_count} клиентов")

        # 2. Даем время на загрузку игр
        logger.info("Ожидание загрузки игр...")
        time.sleep(60)

        # 3. Запускаем мониторинг процессов
        self.process_monitor.start_monitoring()

        # 4. Создаем контроллеры ИИ (без запуска игровой логики)
        self.create_ai_controllers(bot_count)

        self.is_running = True
        logger.info("✅ Система запущена и готова к работе")

        # Выводим статус
        self.print_status()

        return True

    def create_ai_controllers(self, count: int):
        """Создание контроллеров ИИ для каждого бота"""
        logger.info(f"Создание {count} контроллеров ИИ...")

        try:
            from ai.bot_ai import BotAI

            for i in range(count):
                bot_ai = BotAI(bot_id=i)
                self.ai_controllers.append(bot_ai)
                logger.info(f"  Создан контроллер для бота {i + 1}")

        except Exception as e:
            logger.warning(f"Не удалось создать контроллеры ИИ: {e}")
            logger.warning("Игровая логика будет недоступна")

    def stop_system(self):
        """Остановка всей системы"""
        logger.info("Остановка системы...")

        # 1. Останавливаем мониторинг
        if self.process_monitor:
            self.process_monitor.stop_monitoring()

        # 2. Останавливаем все процессы
        if self.game_launcher and hasattr(self.game_launcher, 'controller'):
            self.game_launcher.controller.kill_all()

        # 3. Очищаем контроллеры ИИ
        self.ai_controllers.clear()

        self.is_running = False
        logger.info("✅ Система остановлена")

    def print_status(self):
        """Вывод текущего статуса системы"""
        print("\n" + "=" * 60)
        print("СТАТУС СИСТЕМЫ")
        print("=" * 60)

        if self.game_launcher:
            status = self.game_launcher.get_status()
            print(f"Аккаунты: {status.get('accounts_count', 0)}")
            print(f"Запущено процессов: {status.get('running_processes', 0)}")

        print(f"Контроллеры ИИ: {len(self.ai_controllers)}")
        print(f"Система активна: {'Да' if self.is_running else 'Нет'}")
        print("=" * 60)

    def emergency_stop(self):
        """Экстренная остановка"""
        logger.warning("ЭКСТРЕННАЯ ОСТАНОВКА!")
        self.stop_system()


def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    print("\n\nПолучен сигнал завершения...")
    if 'system' in globals():
        system.stop_system()
    sys.exit(0)


def main():
    """Основная функция"""
    print("=" * 60)
    print("СИСТЕМА УПРАВЛЕНИЯ БОТАМИ DOTA 2")
    print("=" * 60)

    # Настройка обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Создаем директории
    Path("logs").mkdir(exist_ok=True)
    Path("trained_models").mkdir(exist_ok=True)

    # Создаем систему
    global system
    system = DotaBotSystem()

    # Парсим аргументы командной строки
    import argparse
    parser = argparse.ArgumentParser(description='Система управления ботами Dota 2')
    parser.add_argument('--bots', type=int, default=5, help='Количество ботов')
    parser.add_argument('--test', action='store_true', help='Тестовый режим')
    parser.add_argument('--stop', action='store_true', help='Остановить все процессы')

    args = parser.parse_args()

    # Режим остановки
    if args.stop:
        print("Режим остановки...")
        system.initialize()  # Для доступа к контроллеру
        system.stop_system()
        return

    # Тестовый режим
    if args.test:
        print("ТЕСТОВЫЙ РЕЖИМ")
        from test_launch import main as test_main
        sys.exit(test_main())

    # Нормальный запуск
    bot_count = min(args.bots, 5)  # Максимум 5 ботов

    if system.start_system(bot_count):
        print("\nСистема запущена. Для остановки нажмите Ctrl+C")

        # Основной цикл ожидания
        try:
            while system.is_running:
                # Проверяем статус процессов
                if system.process_monitor:
                    if not system.process_monitor.check_all_processes():
                        logger.warning("Обнаружены проблемы с процессами")

                time.sleep(10)

        except KeyboardInterrupt:
            print("\n\nПолучен запрос на остановку...")
            system.stop_system()

    else:
        logger.error("Не удалось запустить систему")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
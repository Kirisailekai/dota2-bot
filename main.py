# main.py - главный управляющий скрипт
"""
Основной скрипт для запуска системы ботов Dota 2
"""

import sys
import os
import time
import signal
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Исправление кодировки для Windows
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DotaBotSystem:
    """Основной класс системы управления ботами (упрощенная версия)"""

    def __init__(self):
        self.game_launcher = None
        self.process_monitor = None
        self.ai_controllers = []
        self.window_manager = None
        self.window_thread = None
        self.is_running = False
        self.accounts_data = None
        self.bot_states = {}  # Состояния каждого бота

    def initialize(self):
        """Инициализация системы"""
        logger.info("Инициализация системы...")

        try:
            # Импортируем только необходимые модули
            from core.game_launcher import GameLauncher
            from core.process_monitor import ProcessMonitor

            # Загружаем аккаунты
            self.load_accounts()

            # Инициализируем компоненты
            self.game_launcher = GameLauncher()
            self.process_monitor = ProcessMonitor()

            # Инициализируем состояния ботов
            self.bot_states = {
                i: {
                    'status': 'not_started',
                    'in_game': False,
                    'in_main_menu': False,
                    'tutorial_completed': False
                }
                for i in range(5)
            }

            logger.info("Система инициализирована")
            return True

        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            return False

    def load_accounts(self):
        """Загрузка данных аккаунтов с учетом сложной структуры"""
        accounts_path = Path("config/accounts.json")
        if accounts_path.exists():
            with open(accounts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Обрабатываем различные форматы файла
            if isinstance(data, dict):
                # Формат с ключом "accounts"
                if "accounts" in data:
                    self.accounts_data = data["accounts"]
                    logger.info(f"Загружено {len(self.accounts_data)} аккаунтов из ключа 'accounts'")

                # Формат словаря с числовыми ключами
                elif all(key.isdigit() for key in data.keys()):
                    self.accounts_data = list(data.values())
                    logger.info(f"Загружено {len(self.accounts_data)} аккаунтов из словаря")

                else:
                    logger.warning(f"Неизвестный формат словаря в accounts.json")
                    self.accounts_data = []

            # Формат прямого списка
            elif isinstance(data, list):
                self.accounts_data = data
                logger.info(f"Загружено {len(self.accounts_data)} аккаунтов из списка")

            else:
                logger.warning(f"Неизвестный формат данных в accounts.json: {type(data)}")
                self.accounts_data = []

            # Нормализуем аккаунты для единообразного доступа
            for i, acc in enumerate(self.accounts_data):
                if isinstance(acc, dict):
                    # Добавляем стандартные ключи для совместимости
                    if 'username' in acc and 'name' not in acc:
                        acc['name'] = acc['username']
                    if 'username' in acc and 'login' not in acc:
                        acc['login'] = acc['username']
                else:
                    logger.warning(f"Аккаунт {i} имеет неверный формат: {type(acc)}")
        else:
            logger.warning(f"Файл accounts.json не найден: {accounts_path}")
            self.accounts_data = []

    def start_window_monitor(self):
        """Запуск мониторинга окон в отдельном потоке"""
        if not self.window_config.get("layout", {}).get("auto_arrange_interval"):
            return

        def monitor_windows():
            interval = self.window_config["layout"]["auto_arrange_interval"]
            logger.info(f"Запущен мониторинг окон (интервал: {interval}с)")

            while self.is_running:
                try:
                    if self.window_manager:
                        windows = self.window_manager.find_dota_windows()
                        if len(windows) >= 5:
                            for hwnd in windows[:5]:
                                try:
                                    if hasattr(self.window_manager, 'is_window_minimized'):
                                        if self.window_manager.is_window_minimized(hwnd):
                                            self.window_manager.restore_all()
                                            break
                                except:
                                    pass
                    else:
                        self.setup_window_manager()
                except Exception as e:
                    logger.error(f"Ошибка в мониторинге окон: {e}")
                time.sleep(interval)

        self.window_thread = threading.Thread(target=monitor_windows, daemon=True)
        self.window_thread.start()
        logger.info("Мониторинг окон запущен")

    def create_ai_controllers(self, count: int):
        """Создание контроллеров ИИ для каждого бота"""
        logger.info(f"Создание {count} контроллеров ИИ...")

        try:
            from ai.bot_ai import BotAI
            for i in range(count):
                account_data = None
                if self.accounts_data and i < len(self.accounts_data):
                    account_data = self.accounts_data[i]

                bot_ai = BotAI(bot_id=i, account_data=account_data)
                self.ai_controllers.append(bot_ai)
                logger.info(f"Создан контроллер для бота {i + 1}")
        except ImportError:
            logger.warning("Модуль ИИ не найден, игровая логика будет недоступна")
        except Exception as e:
            logger.warning(f"Не удалось создать контроллеры ИИ: {e}")

    def start_system(self, bot_count: int = 5):
        """Запуск всей системы (только базовый запуск окон)"""
        if not self.initialize():
            logger.error("Не удалось инициализировать систему")
            return False

        logger.info(f"Запуск системы с {bot_count} ботами...")

        # 1. Запускаем игровые клиенты
        logger.info("1. Запуск игровых клиентов...")
        launch_result = self.game_launcher.launch_team(bot_count)

        if launch_result["status"] == "error":
            logger.error(f"Ошибка запуска: {launch_result.get('message', 'Unknown')}")
            return False

        logger.info(f"Запущено {launch_result['successful']}/{bot_count} клиентов")

        # 3. Даем дополнительное время на полную загрузку Dota 2
        logger.info("3. Ожидание полной загрузки Dota 2 во всех окнах...")
        time.sleep(60)

        # 4. Запускаем мониторинг процессов
        logger.info("4. Запуск мониторинга процессов...")
        self.process_monitor.start_monitoring()
        logger.info("Мониторинг процессов запущен")

        self.is_running = True
        logger.info("Система запущена и готова к работе")

        # Выводим статус
        self.print_status()

        return True

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

        if self.window_manager:
            try:
                windows = self.window_manager.find_dota_windows()
                print(f"Найдено окон Dota 2: {len(windows)}")
            except:
                print("Найдено окон Dota 2: N/A")

        print(f"Система активна: {'ДА' if self.is_running else 'НЕТ'}")
        print("=" * 60)

    def stop_system(self):
        """Остановка всей системы"""
        logger.info("Остановка системы...")
        self.is_running = False

        # Останавливаем мониторинг процессов
        if self.process_monitor:
            self.process_monitor.stop_monitoring()
            logger.info("Мониторинг процессов остановлен")

        # Останавливаем все процессы
        if self.game_launcher and hasattr(self.game_launcher, 'controller'):
            self.game_launcher.controller.kill_all()
            logger.info("Игровые процессы остановлены")

        # Очищаем контроллеры ИИ
        self.ai_controllers.clear()
        logger.info("Система остановлена")

    def launch_single_bot(self, sandbox_name="DOTA_BOT_1", account_index=0):
        """Запуск только одного бота"""
        logger.info(f"Запуск одного бота в песочнице {sandbox_name}...")

        try:
            from core.sandbox_controller import SandboxController

            # Загружаем аккаунт
            if not self.accounts_data or account_index >= len(self.accounts_data):
                logger.error(f"Нет аккаунта с индексом {account_index}")
                return False

            account = self.accounts_data[account_index]
            username = account.get('username', '')
            password = account.get('password', '')

            if not username or not password:
                logger.error(f"У аккаунта {account_index} нет логина или пароля")
                return False

            # Создаем контроллер песочниц
            controller = SandboxController()

            if not controller.check_installation():
                logger.error("Sandboxie не установлен")
                return False

            # Формируем команду
            steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
            command = f'"{steam_path}" -login {username} {password} -applaunch 570 -novid -console -windowed -w 1024 -h 768'

            logger.info(f"Запускаю команду в песочнице {sandbox_name}...")
            result = controller.run_in_sandbox(sandbox_name, command)

            if result.get("success", False):
                logger.info(f"✅ Бот запущен (PID: {result.get('pid')})")
                logger.info(f"Аккаунт: {username}")
                logger.info(f"Песочница: {sandbox_name}")

                # Ждем и проверяем окно
                import time
                time.sleep(60)

            else:
                logger.error(f"Ошибка запуска: {result.get('error', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"Ошибка запуска одного бота: {e}")
            return False

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
    print("Упрощенная версия - только базовый запуск окон")
    print("=" * 60)
    print("Функции:")
    print("  1. Запуск 5 окон Dota 2 в песочницах")
    print("  2. Автоматическое расположение окон в сетке")
    print("  3. Мониторинг процессов")
    print("  4. Запуск одного окна")
    print("=" * 60)

    # Настройка обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Создаем директории
    Path("logs").mkdir(exist_ok=True)
    Path("trained_models").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)

    # Создаем систему
    global system
    system = DotaBotSystem()

    # Парсим аргументы командной строки
    import argparse
    parser = argparse.ArgumentParser(description='Система управления ботами Dota 2')
    parser.add_argument('--bots', type=int, default=5, help='Количество ботов')
    parser.add_argument('--single', action='store_true', help='Запустить только одного бота')
    parser.add_argument('--sandbox', type=str, default='DOTA_BOT_1', help='Имя песочницы для запуска одного бота')
    parser.add_argument('--account-index', type=int, default=0, help='Индекс аккаунта из accounts.json')
    parser.add_argument('--stop', action='store_true', help='Остановить все процессы')
    parser.add_argument('--no-windows', action='store_true', help='Не управлять расположением окон')
    parser.add_argument('--arrange-windows', action='store_true', help='Расположить окна и выйти')
    parser.add_argument('--layout', type=str, default='2x3', choices=['2x3', 'custom', 'single'],
                        help='Схема расположения окон')

    args = parser.parse_args()

    # Режим остановки
    if args.stop:
        print("Режим остановки...")
        system.initialize()
        system.stop_system()
        return

    # Режим только расположения окон
    if args.arrange_windows:
        print("Режим расположения окон...")
        if system.setup_window_manager():
            system.arrange_windows(args.layout)
        return

    # Режим запуска одного бота
    if args.single:
        print(f"Запуск одного бота в песочнице {args.sandbox}...")
        if system.initialize():
            system.launch_single_bot(
                sandbox_name=args.sandbox,
                account_index=args.account_index
            )
        return

    # Нормальный запуск нескольких ботов
    bot_count = min(args.bots, 5)

    if system.start_system(bot_count):
        print("\nСистема запущена успешно!")
        print("\nОкна Dota 2 должны быть запущены.")

        # --- Расстановка окон 3 сверху + 2 снизу ---
        positions = [
            (0, 0, 640, 540),  # верхний ряд
            (640, 0, 640, 540),
            (1280, 0, 640, 540),
            (0, 540, 960, 540),  # нижний ряд
            (960, 540, 960, 540)
        ]

        # Запуск каждого клиента через SandboxController
        from core.sandbox_controller import SandboxController
        controller = SandboxController()

        for i, pos in enumerate(positions, start=1):
            # Берем аккаунт
            account_data = None
            if system.accounts_data and i - 1 < len(system.accounts_data):
                account_data = system.accounts_data[i - 1]

            username = account_data.get('username', f'login{i}') if account_data else f'login{i}'
            password = account_data.get('password', 'pass') if account_data else 'pass'

            # Запуск с правильной позицией
            controller.launch_steam(
                sandbox_name=f"DOTA_BOT_{i}",
                username=username,
                password=password,
                window_position=pos
            )

        print("Для остановки нажмите Ctrl+C")

        # Основной цикл ожидания
        try:
            last_status_time = time.time()
            while system.is_running:
                # Обновляем статус каждые 60 секунд
                current_time = time.time()
                if current_time - last_status_time > 60:
                    system.print_status()
                    last_status_time = current_time

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
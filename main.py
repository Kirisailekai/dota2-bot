# main.py - главный управляющий скрипт
"""
Основной скрипт для запуска системы ботов
"""

import sys
import time
import signal
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional
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
        self.window_manager = None
        self.lobby_manager = None
        self.game_controller = None
        self.window_thread = None
        self.hotkey_manager = None
        self.game_thread = None
        self.is_running = False
        self.window_layout_config = "config/window_layout.json"
        self.lobby_config = "config/lobby_config.json"

    def initialize(self):
        """Инициализация системы"""
        logger.info("Инициализация системы...")

        try:
            # Импортируем модули
            from core.game_launcher import GameLauncher
            from core.process_monitor import ProcessMonitor

            # Инициализируем компоненты
            self.game_launcher = GameLauncher()
            self.process_monitor = ProcessMonitor()

            logger.info("Система инициализирована")
            return True

        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            return False

    def setup_window_manager(self):
        """Настройка менеджера окон"""
        try:
            from utils.window_manager import WindowManager
            self.window_manager = WindowManager(self.window_layout_config)

            # Загружаем конфигурацию
            self.load_window_config()

            logger.info("Менеджер окон инициализирован")
            return True

        except ImportError as e:
            logger.warning(f"Модуль управления окнами не установлен: {e}")
            logger.info("Для управления окнами установите: pip install pywin32")
            return False
        except Exception as e:
            logger.error(f"Ошибка настройки менеджера окон: {e}")
            return False

    def setup_hotkey_manager(self):
        """Настройка менеджера горячих клавиш"""
        try:
            from utils.hotkey_manager import HotkeyManager
            self.hotkey_manager = HotkeyManager(self.window_layout_config)
            logger.info("Менеджер горячих клавиш инициализирован")
            return True
        except ImportError as e:
            logger.warning(f"Модуль горячих клавиш не установлен: {e}")
            logger.info("Для горячих клавиш установите: pip install keyboard")
            return False
        except Exception as e:
            logger.error(f"Ошибка настройки менеджера горячих клавиш: {e}")
            return False

    def setup_game_system(self):
        """Настройка игровой системы (лобби, пати, матчмейкинг)"""
        try:
            from core.lobby_manager import LobbyManager
            from core.game_controller import GameController

            self.lobby_manager = LobbyManager(self.lobby_config)
            self.game_controller = GameController(self.window_manager)

            if self.lobby_manager:
                self.game_controller.set_lobby_manager(self.lobby_manager)

            logger.info("Игровая система инициализирована")
            return True

        except ImportError as e:
            logger.warning(f"Модули игровой системы не найдены: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка настройки игровой системы: {e}")
            return False

    def load_window_config(self):
        """Загрузка конфигурации окон"""
        config_path = Path(self.window_layout_config)
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.window_config = json.load(f)
            logger.info(f"Загружена конфигурация окон из {config_path}")
        else:
            # Конфигурация по умолчанию
            self.window_config = {
                "layout": {
                    "grid": [2, 3],
                    "margins": {"top": 40, "right": 10, "bottom": 10, "left": 10},
                    "spacing": 5,
                    "always_on_top": False,
                    "auto_arrange_on_start": True,
                    "auto_arrange_interval": 30
                },
                "window_titles": ["Bot 1", "Bot 2", "Bot 3", "Bot 4", "Bot 5"],
                "hotkeys": {
                    "arrange_windows": "ctrl+alt+a",
                    "minimize_all": "ctrl+alt+m",
                    "restore_all": "ctrl+alt+r",
                    "toggle_auto_arrange": "ctrl+alt+t"
                }
            }
            # Сохраняем конфигурацию по умолчанию
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.window_config, f, indent=2)
            logger.info(f"Создана конфигурация окон по умолчанию: {config_path}")

    def arrange_windows(self, layout: str = "2x3"):
        """Расположить окна в сетке"""
        if not self.window_manager:
            logger.warning("Менеджер окон не инициализирован")
            return False

        try:
            logger.info(f"Располагаю окна в сетке {layout}...")
            time.sleep(2)

            windows = self.window_manager.arrange_windows_grid(layout)

            if windows:
                logger.info(f"Успешно расположено {len(windows)} окон")

                # Устанавливаем заголовки окон
                titles = self.window_config.get("window_titles",
                                                ["Bot 1", "Bot 2", "Bot 3", "Bot 4", "Bot 5"])
                self.window_manager.set_window_titles(titles[:len(windows)])

                # Выводим на передний план
                if self.window_config.get("layout", {}).get("always_on_top", False):
                    self.window_manager.bring_to_front()

                return True
            else:
                logger.warning("Не найдены окна Dota 2 для расположения")
                return False

        except Exception as e:
            logger.error(f"Ошибка при расположении окон: {e}")
            return False

    def start_window_monitor(self):
        """Запуск мониторинга окон в отдельном потоке"""
        if not self.window_config.get("layout", {}).get("auto_arrange_interval"):
            return

        def monitor_windows():
            """Функция мониторинга окон"""
            interval = self.window_config["layout"]["auto_arrange_interval"]
            logger.info(f"Запущен мониторинг окон (интервал: {interval}с)")

            while self.is_running:
                try:
                    if self.window_manager:
                        windows = self.window_manager.find_dota_windows()
                        if len(windows) >= 5:
                            # Проверяем, не свернуты ли окна
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

    def start_hotkey_monitor(self):
        """Запуск мониторинга горячих клавиш"""
        if not self.hotkey_manager:
            logger.warning("Менеджер горячих клавиш не инициализирован")
            return False

        try:
            # Запускаем в отдельном потоке
            hotkey_thread = threading.Thread(target=self.hotkey_manager.start, daemon=True)
            hotkey_thread.start()
            logger.info("Мониторинг горячих клавиш запущен")
            return True
        except Exception as e:
            logger.warning(f"Не удалось запустить мониторинг горячих клавиш: {e}")
            return False

    def start_game_automation(self):
        """Запуск автоматизации игрового процесса в отдельном потоке"""
        if not self.game_controller:
            logger.error("Игровой контроллер не инициализирован")
            return False

        def game_sequence():
            logger.info("Запуск автоматизации игрового процесса...")

            # Даем время на загрузку всех клиентов
            logger.info("Ожидание загрузки всех клиентов...")
            time.sleep(60)

            # Запускаем игровую последовательность
            try:
                success = self.game_controller.start_game_sequence()

                if success:
                    logger.info("Игровая последовательность успешно завершена")
                    # Запускаем мониторинг игры
                    self.game_controller.monitor_game_state()
                else:
                    logger.error("Ошибка в игровой последовательности")
            except Exception as e:
                logger.error(f"Ошибка при запуске игровой последовательности: {e}")

        self.game_thread = threading.Thread(target=game_sequence, daemon=True)
        self.game_thread.start()
        logger.info("Автоматизация игры запущена в отдельном потоке")
        return True

    def create_ai_controllers(self, count: int):
        """Создание контроллеров ИИ для каждого бота"""
        logger.info(f"Создание {count} контроллеров ИИ...")

        try:
            from ai.bot_ai import BotAI
            for i in range(count):
                bot_ai = BotAI(bot_id=i)
                self.ai_controllers.append(bot_ai)
                logger.info(f"Создан контроллер для бота {i + 1}")
        except ImportError:
            logger.warning("Модуль ИИ не найден, игровая логика будет недоступна")
        except Exception as e:
            logger.warning(f"Не удалось создать контроллеры ИИ: {e}")

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

        # 2. Настраиваем менеджер окон
        window_manager_ready = self.setup_window_manager()

        if window_manager_ready:
            # Ждем появления окон
            logger.info("Ожидание появления окон...")
            time.sleep(15)

            # Автоматически располагаем окна
            auto_arrange = self.window_config.get("layout", {}).get("auto_arrange_on_start", True)
            if auto_arrange:
                for attempt in range(3):
                    if self.arrange_windows("2x3"):
                        break
                    logger.info(f"Повторная попытка расположения окон ({attempt + 1}/3)...")
                    time.sleep(5)

            # Запускаем мониторинг окон
            self.start_window_monitor()

        # 3. Настраиваем менеджер горячих клавиш
        self.setup_hotkey_manager()
        if self.hotkey_manager:
            self.start_hotkey_monitor()

        # 4. Настраиваем игровую систему
        game_system_ready = self.setup_game_system()

        # 5. Запускаем автоматизацию игры (если система готова)
        if game_system_ready:
            logger.info("Запуск автоматизации игрового процесса...")
            self.start_game_automation()
        else:
            logger.warning("Игровая система не готова, автоматизация отключена")

        # 6. Даем время на загрузку игр
        logger.info("Ожидание загрузки игр...")
        time.sleep(60)

        # 7. Запускаем мониторинг процессов
        self.process_monitor.start_monitoring()

        # 8. Создаем контроллеры ИИ
        self.create_ai_controllers(bot_count)

        self.is_running = True
        logger.info("✅ Система запущена и готова к работе")

        self.print_status()
        return True

    def stop_system(self):
        """Остановка всей системы"""
        logger.info("Остановка системы...")
        self.is_running = False

        # Останавливаем менеджер горячих клавиш
        if self.hotkey_manager:
            try:
                self.hotkey_manager.stop()
                logger.info("Менеджер горячих клавиш остановлен")
            except:
                pass

        # Останавливаем игровую автоматизацию
        if self.game_controller:
            try:
                self.game_controller.stop()
                logger.info("Игровая автоматизация остановлена")
            except:
                pass

        # Останавливаем мониторинг процессов
        if self.process_monitor:
            self.process_monitor.stop_monitoring()

        # Останавливаем все процессы
        if self.game_launcher and hasattr(self.game_launcher, 'controller'):
            self.game_launcher.controller.kill_all()

        # Очищаем контроллеры ИИ
        self.ai_controllers.clear()
        logger.info("Система остановлена")

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

        if self.game_controller:
            try:
                game_status = self.game_controller.get_game_status()
                print(f"Состояние игры: {game_status.get('game_state', 'UNKNOWN')}")
            except:
                print("Состояние игры: N/A")

        print(f"Менеджер окон: {'✓' if self.window_manager else '✗'}")
        print(f"Горячие клавиши: {'✓' if self.hotkey_manager else '✗'}")
        print(f"Игровая система: {'✓' if self.game_controller else '✗'}")
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
    print("🎮 СИСТЕМА УПРАВЛЕНИЯ БОТАМИ DOTA 2")
    print("=" * 60)
    print("Функции:")
    print("  1. Запуск 5 окон Dota 2 в песочницах")
    print("  2. Автоматическое расположение окон в сетке")
    print("  3. Управление горячими клавишами")
    print("  4. Создание лобби и пати")
    print("  5. Автоматический поиск матча")
    print("  6. Автовыбор героев и начало игры")
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
    parser.add_argument('--test', action='store_true', help='Тестовый режим')
    parser.add_argument('--stop', action='store_true', help='Остановить все процессы')
    parser.add_argument('--no-windows', action='store_true', help='Не управлять расположением окон')
    parser.add_argument('--no-hotkeys', action='store_true', help='Отключить горячие клавиши')
    parser.add_argument('--no-game', action='store_true', help='Отключить игровую автоматизацию')
    parser.add_argument('--no-ai', action='store_true', help='Отключить ИИ контроллеры')
    parser.add_argument('--arrange-windows', action='store_true', help='Расположить окна и выйти')
    parser.add_argument('--start-game', action='store_true', help='Запустить только игровую автоматизацию')
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

    # Режим только запуска игры
    if args.start_game:
        print("Режим запуска игры...")
        if system.setup_game_system():
            system.start_game_automation()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nЗавершение...")
                system.stop_system()
        return

    # Тестовый режим
    if args.test:
        print("ТЕСТОВЫЙ РЕЖИМ")
        try:
            from test_launch import main as test_main
            sys.exit(test_main())
        except ImportError:
            print("Тестовый модуль не найден")
            return

    # Нормальный запуск
    bot_count = min(args.bots, 5)

    # Настройки
    if args.no_windows:
        system.window_layout_config = None

    if args.no_hotkeys:
        system.setup_hotkey_manager = lambda: False

    if args.no_game:
        system.lobby_config = None

    if args.no_ai:
        system.create_ai_controllers = lambda x: None

    if system.start_system(bot_count):
        print("\n✅ Система запущена успешно!")
        print("\n📊 Статус будет обновляться автоматически.")
        print("Для остановки нажмите Ctrl+C")

        if system.hotkey_manager and system.window_config:
            print("\n🎯 Горячие клавиши для управления окнами:")
            hotkeys = system.window_config.get("hotkeys", {})
            for action, key in hotkeys.items():
                action_name = action.replace('_', ' ').title()
                print(f"  {key}: {action_name}")

        # Основной цикл ожидания
        try:
            last_status_time = time.time()
            while system.is_running:
                # Обновляем статус каждые 30 секунд
                current_time = time.time()
                if current_time - last_status_time > 30:
                    system.print_status()
                    last_status_time = current_time

                # Проверяем статус процессов
                if system.process_monitor:
                    if not system.process_monitor.check_all_processes():
                        logger.warning("Обнаружены проблемы с процессами")

                time.sleep(10)

        except KeyboardInterrupt:
            print("\n\n🛑 Получен запрос на остановку...")
            system.stop_system()

    else:
        logger.error("Не удалось запустить систему")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
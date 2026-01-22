# main.py - главный управляющий скрипт
"""
Основной скрипт для запуска системы ботов
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
        self.window_config = {}
        self.accounts_data = None
        self.bot_states = {}  # Состояния каждого бота
        self.leader_bot_index = 0  # Индекс бота-лидера

    def initialize(self):
        """Инициализация системы"""
        logger.info("Инициализация системы...")

        try:
            # Импортируем модули
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
                    'tutorial_completed': False,
                    'in_party': False,
                    'ready': False,
                    'hero_selected': False,
                    'game_started': False
                }
                for i in range(5)
            }

            logger.info("Система инициализирована")
            return True

        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            return False

    def load_accounts(self):
        """Загрузка данных аккаунтов"""
        accounts_path = Path("config/accounts.json")
        if accounts_path.exists():
            with open(accounts_path, 'r', encoding='utf-8') as f:
                self.accounts_data = json.load(f)
            logger.info(f"Загружено {len(self.accounts_data)} аккаунтов")
        else:
            logger.warning(f"Файл accounts.json не найден: {accounts_path}")
            self.accounts_data = []

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
            return False
        except Exception as e:
            logger.error(f"Ошибка настройки менеджера горячих клавиш: {e}")
            return False

    def setup_game_system(self):
        """Настройка игровой системы"""
        try:
            from core.lobby_manager import LobbyManager
            from core.game_controller import GameController

            # Инициализируем менеджер лобби
            self.lobby_manager = LobbyManager(self.lobby_config)

            # Передаем данные аккаунтов
            if self.accounts_data:
                self.lobby_manager.accounts = self.accounts_data

            # Инициализируем игровой контроллер
            self.game_controller = GameController(self.window_manager)

            # Настраиваем связи
            if self.lobby_manager:
                self.game_controller.set_lobby_manager(self.lobby_manager)
                self.game_controller.accounts = self.accounts_data
                self.game_controller.bot_states = self.bot_states

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
            with open(config_path, 'r', encoding='utf-8') as f:
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
                    "skip_tutorial": "ctrl+alt+t",
                    "start_party": "ctrl+alt+p",
                    "start_match": "ctrl+alt+s",
                    "emergency_stop": "ctrl+alt+q"
                }
            }
            # Сохраняем конфигурацию по умолчанию
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
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
                titles = []
                if self.accounts_data and len(self.accounts_data) >= len(windows):
                    for i in range(len(windows)):
                        acc = self.accounts_data[i]
                        titles.append(f"Bot {i + 1} - {acc.get('name', 'Unknown')}")
                else:
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

    def start_hotkey_monitor(self):
        """Запуск мониторинга горячих клавиш"""
        if not self.hotkey_manager:
            logger.warning("Менеджер горячих клавиш не инициализирован")
            return False

        try:
            # Добавляем дополнительные горячие клавиши
            if hasattr(self.hotkey_manager, 'add_callback'):
                self.hotkey_manager.add_callback("ctrl+alt+t", self.skip_tutorials)
                self.hotkey_manager.add_callback("ctrl+alt+p", self.start_party_sequence)
                self.hotkey_manager.add_callback("ctrl+alt+s", self.start_match_search)
                self.hotkey_manager.add_callback("ctrl+alt+q", self.emergency_stop)

            # Запускаем в отдельном потоке
            hotkey_thread = threading.Thread(target=self.hotkey_manager.start, daemon=True)
            hotkey_thread.start()
            logger.info("Мониторинг горячих клавиш запущен")
            return True
        except Exception as e:
            logger.warning(f"Не удалось запустить мониторинг горячих клавиш: {e}")
            return False

    def skip_tutorials(self):
        """Пропуск обучающего матча для всех ботов"""
        logger.info("Пропуск обучающего матча для всех ботов...")

        def skip_for_bot(bot_index):
            try:
                if self.game_controller:
                    success = self.game_controller.skip_tutorial(bot_index)
                    if success:
                        self.bot_states[bot_index]['tutorial_completed'] = True
                        logger.info(f"Бот {bot_index + 1}: обучение пропущено")
                    return success
                return False
            except Exception as e:
                logger.error(f"Ошибка пропуска обучения для бота {bot_index + 1}: {e}")
                return False

        # Запускаем в отдельных потоках для каждого бота
        threads = []
        for i in range(5):
            thread = threading.Thread(target=skip_for_bot, args=(i,), daemon=True)
            thread.start()
            threads.append(thread)
            time.sleep(1)  # Небольшая задержка между ботами

        # Ждем завершения всех потоков
        for thread in threads:
            thread.join(timeout=30)

        logger.info("Пропуск обучения завершен")

    def wait_for_main_menu(self, timeout: int = 300):
        """Ожидание загрузки главного меню для всех ботов"""
        logger.info("Ожидание загрузки главного меню...")

        start_time = time.time()
        all_ready = False

        while time.time() - start_time < timeout and not all_ready:
            all_ready = True

            for i in range(5):
                if not self.bot_states[i]['in_main_menu']:
                    if self.game_controller:
                        in_menu = self.game_controller.check_main_menu(i)
                        if in_menu:
                            self.bot_states[i]['in_main_menu'] = True
                            self.bot_states[i]['status'] = 'in_main_menu'
                            logger.info(f"Бот {i + 1}: в главном меню")
                        else:
                            all_ready = False
                    else:
                        all_ready = False

            if not all_ready:
                time.sleep(5)
                logger.info("Ждем загрузку главного меню...")

        if all_ready:
            logger.info("Все боты в главном меню!")
            return True
        else:
            logger.warning("Не все боты загрузились в главное меню")
            return False

    def start_party_sequence(self):
        """Запуск последовательности создания пати"""
        if not self.game_controller:
            logger.error("Игровой контроллер не инициализирован")
            return False

        logger.info("=== ЗАПУСК СОЗДАНИЯ ПАТИ ===")

        def party_thread():
            try:
                # 1. Проверяем, все ли боты в главном меню
                if not self.wait_for_main_menu(timeout=60):
                    logger.error("Не все боты в главном меню")
                    return

                # 2. Создаем лобби через бота-лидера
                logger.info("1. Создание лобби...")
                lobby_created = False
                for attempt in range(3):
                    if self.game_controller.create_lobby(self.leader_bot_index):
                        lobby_created = True
                        logger.info("Лобби создано")
                        break
                    logger.warning(f"Попытка {attempt + 1} создания лобби не удалась")
                    time.sleep(10)

                if not lobby_created:
                    logger.error("Не удалось создать лобби")
                    return

                time.sleep(5)

                # 3. Приглашаем ботов в пати (если они друзья)
                logger.info("2. Приглашение ботов в пати...")
                invited_count = 0

                # Вариант 1: Через поиск по нику (для новых аккаунтов без друзей)
                for i in range(5):
                    if i != self.leader_bot_index:
                        # Получаем ник бота
                        bot_name = f"Bot_{i + 1}"
                        if self.accounts_data and i < len(self.accounts_data):
                            bot_name = self.accounts_data[i].get('name', f"Bot_{i + 1}")

                        logger.info(f"Приглашаем бота {i + 1} ({bot_name})...")

                        # Приглашаем через поиск
                        if self.game_controller.invite_by_search(self.leader_bot_index, i, bot_name):
                            invited_count += 1
                            time.sleep(3)
                        else:
                            logger.warning(f"Не удалось пригласить бота {i + 1}")

                logger.info(f"Отправлено {invited_count} приглашений")

                # 4. Ждем принятия приглашений
                logger.info("3. Ожидание принятия приглашений...")
                time.sleep(20)

                # 5. Проверяем состав пати
                party_size = self.game_controller.check_party_size(self.leader_bot_index)
                logger.info(f"В пати {party_size} ботов")

                if party_size >= 3:  # Хотя бы 3 бота вместе
                    logger.info("Пати успешно собрана!")

                    # Обновляем состояния ботов
                    for i in range(5):
                        if i == self.leader_bot_index or party_size > 1:
                            self.bot_states[i]['in_party'] = True
                            self.bot_states[i]['status'] = 'in_party'
                else:
                    logger.warning("В пати недостаточно ботов. Пробуем альтернативный метод...")

                    # Альтернатива: Публичное лобби или игра с ботами
                    self.start_bot_match_alternative()

            except Exception as e:
                logger.error(f"Ошибка при создании пати: {e}")

        threading.Thread(target=party_thread, daemon=True).start()
        return True

    def start_bot_match_alternative(self):
        """Альтернативный метод: игра против ботов (не требует пати)"""
        logger.info("Запуск альтернативного сценария: игра с ботами...")

        try:
            # Каждый бот отдельно заходит в режим игры с ботами
            for i in range(5):
                if self.game_controller:
                    self.game_controller.play_with_bots(i)
                    time.sleep(2)

            logger.info("Все боты ищут игру с ботами...")

        except Exception as e:
            logger.error(f"Ошибка в альтернативном сценарии: {e}")

    def start_match_search(self):
        """Запуск поиска матча"""
        if not self.game_controller:
            logger.error("Игровой контроллер не инициализирован")
            return False

        logger.info("=== ЗАПУСК ПОИСКА МАТЧА ===")

        def match_search_thread():
            try:
                # 1. Выбираем режим игры (All Pick - самый популярный)
                logger.info("1. Выбор режима игры...")
                if self.game_controller.select_game_mode(self.leader_bot_index, mode="all_pick"):
                    logger.info("Режим игры выбран: All Pick")
                else:
                    logger.warning("Не удалось выбрать режим игры, используем по умолчанию")

                time.sleep(3)

                # 2. Запускаем поиск матча
                logger.info("2. Запуск поиска матча...")
                if self.game_controller.start_match_search(self.leader_bot_index):
                    logger.info("Поиск матча запущен")

                    # Обновляем состояние лидера
                    self.bot_states[self.leader_bot_index]['status'] = 'searching_match'
                else:
                    logger.error("Не удалось запустить поиск")
                    return

                # 3. Мониторим статус поиска (только для лидера)
                logger.info("3. Мониторинг статуса поиска...")
                match_found = False

                for minute in range(1, 11):  # Ждем до 10 минут
                    if not self.is_running:
                        break

                    # Проверяем, найден ли матч
                    status = self.game_controller.get_matchmaking_status(self.leader_bot_index)
                    if status.get('match_found', False):
                        logger.info("Матч найден!")
                        match_found = True

                        # 4. Принимаем матч для всех ботов
                        logger.info("4. Принятие матча...")
                        accept_count = 0
                        for i in range(5):
                            if self.game_controller.accept_match(i):
                                accept_count += 1
                                self.bot_states[i]['status'] = 'match_accepted'
                                time.sleep(1)

                        logger.info(f"Матч приняли {accept_count}/5 ботов")
                        break

                    logger.info(f"Поиск... ({minute}/10 минут)")
                    time.sleep(60)  # Проверяем каждую минуту

                if not match_found:
                    logger.warning("Матч не найден за отведенное время")
                    # Отменяем поиск
                    self.game_controller.cancel_search(self.leader_bot_index)

            except Exception as e:
                logger.error(f"Ошибка при поиске матча: {e}")

        threading.Thread(target=match_search_thread, daemon=True).start()
        return True

    def start_game_automation(self):
        """Запуск полной автоматизации игрового процесса"""
        if not self.game_controller:
            logger.error("Игровой контроллер не инициализирован")
            return False

        def game_sequence():
            logger.info("=== ПОЛНАЯ АВТОМАТИЗАЦИЯ ИГРОВОГО ПРОЦЕССА ===")

            # 1. Даем время на загрузку всех клиентов
            logger.info("1. Ожидание загрузки клиентов...")
            time.sleep(90)  # Больше времени для загрузки + возможного обучения

            # 2. Пропускаем обучающий матч (если есть)
            logger.info("2. Пропуск обучающего матча...")
            self.skip_tutorials()
            time.sleep(30)

            # 3. Ждем главное меню
            logger.info("3. Ожидание главного меню...")
            if not self.wait_for_main_menu(timeout=120):
                logger.warning("Не все боты загрузились в главное меню, продолжаем...")

            # 4. Создаем пати
            logger.info("4. Создание пати...")
            self.start_party_sequence()
            time.sleep(40)  # Ждем сбор пати

            # 5. Запускаем поиск матча
            logger.info("5. Запуск поиска матча...")
            self.start_match_search()

            # 6. Мониторим состояние игры
            logger.info("6. Мониторинг игры...")
            self.monitor_game_progress()

        self.game_thread = threading.Thread(target=game_sequence, daemon=True)
        self.game_thread.start()
        logger.info("Автоматизация игры запущена")
        return True

    def monitor_game_progress(self):
        """Мониторинг прогресса игры"""

        def monitor():
            while self.is_running:
                try:
                    # Проверяем состояние каждого бота
                    active_bots = 0
                    in_game_bots = 0

                    for i in range(5):
                        if self.game_controller:
                            state = self.game_controller.get_bot_state(i)
                            if state:
                                self.bot_states[i].update(state)

                                if state.get('in_game', False):
                                    in_game_bots += 1
                                    active_bots += 1
                                elif state.get('status') not in ['not_started', 'error']:
                                    active_bots += 1

                    # Логируем статус
                    logger.info(f"Активных ботов: {active_bots}/5, в игре: {in_game_bots}")

                    # Если все боты вышли из игры, можно перезапустить
                    if in_game_bots == 0 and active_bots < 2:
                        logger.info("Игра завершена, готовимся к следующей...")
                        time.sleep(60)
                        break

                    time.sleep(30)  # Проверяем каждые 30 секунд

                except Exception as e:
                    logger.error(f"Ошибка мониторинга: {e}")
                    time.sleep(10)

        threading.Thread(target=monitor, daemon=True).start()

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
        """Запуск всей системы"""
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

        # 2. Настраиваем менеджер окон
        logger.info("2. Настройка менеджера окон...")
        window_manager_ready = self.setup_window_manager()

        if window_manager_ready:
            # Ждем появления окон
            logger.info("Ожидание появления окон...")
            time.sleep(30)

            # Автоматически располагаем окна
            auto_arrange = self.window_config.get("layout", {}).get("auto_arrange_on_start", True)
            if auto_arrange:
                for attempt in range(3):
                    if self.arrange_windows("2x3"):
                        logger.info("Окна успешно расположены в сетке")
                        break
                    logger.info(f"Повторная попытка расположения окон ({attempt + 1}/3)...")
                    time.sleep(10)

            # Запускаем мониторинг окон
            self.start_window_monitor()
        else:
            logger.warning("Управление окнами отключено")

        # 3. Настраиваем менеджер горячих клавиш
        logger.info("3. Настройка менеджера горячих клавиш...")
        self.setup_hotkey_manager()
        if self.hotkey_manager:
            self.start_hotkey_monitor()
            logger.info("Горячие клавиши настроены")
        else:
            logger.warning("Горячие клавиши отключены")

        # 4. Настраиваем игровую систему
        logger.info("4. Настройка игровой системы...")
        game_system_ready = self.setup_game_system()

        if game_system_ready:
            # Запускаем автоматизацию игры
            logger.info("5. Запуск автоматизации игрового процесса...")
            automation_started = self.start_game_automation()

            if automation_started:
                logger.info("Автоматизация игры запущена")
                logger.info("Последовательность:")
                logger.info("  1. Пропуск обучающего матча (если есть)")
                logger.info("  2. Загрузка в главное меню")
                logger.info("  3. Создание пати (если возможно)")
                logger.info("  4. Поиск матча")
                logger.info("  5. Принятие матча")
                logger.info("  6. Игра")
            else:
                logger.warning("Не удалось запустить автоматизацию игры")
        else:
            logger.warning("Игровая система не готова, автоматизация отключена")

        # 5. Запускаем мониторинг процессов
        logger.info("6. Запуск мониторинга процессов...")
        self.process_monitor.start_monitoring()
        logger.info("Мониторинг процессов запущен")

        # 6. Создаем контроллеры ИИ
        logger.info("7. Создание контроллеров ИИ...")
        self.create_ai_controllers(bot_count)

        # 7. Устанавливаем связи
        if self.game_controller and self.window_manager:
            self.game_controller.window_manager = self.window_manager
            logger.info("Менеджер окон установлен в игровой контроллер")

        self.is_running = True
        logger.info("Система запущена и готова к работе")

        # Выводим статус
        self.print_status()

        # Запускаем цикл обновления статуса
        self.start_status_updater()

        return True

    def start_status_updater(self):
        """Запуск периодического обновления статуса"""

        def update_status():
            while self.is_running:
                time.sleep(30)
                try:
                    if self.is_running:
                        self.print_status()
                except Exception as e:
                    logger.error(f"Ошибка обновления статуса: {e}")

        status_thread = threading.Thread(target=update_status, daemon=True)
        status_thread.start()
        logger.info("Мониторинг статуса запущен")

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
            logger.info("Мониторинг процессов остановлен")

        # Останавливаем все процессы
        if self.game_launcher and hasattr(self.game_launcher, 'controller'):
            self.game_launcher.controller.kill_all()
            logger.info("Игровые процессы остановлены")

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

        # Статусы ботов
        print("\nСОСТОЯНИЕ БОТОВ:")
        for i in range(5):
            state = self.bot_states.get(i, {})
            status_text = state.get('status', 'unknown')
            in_party = "В пати" if state.get('in_party', False) else "Не в пати"
            print(f"  Бот {i + 1}: {status_text} | {in_party}")

        if self.window_manager:
            try:
                windows = self.window_manager.find_dota_windows()
                print(f"\nНайдено окон Dota 2: {len(windows)}")
            except:
                print("\nНайдено окон Dota 2: N/A")

        print(f"\nМенеджер окон: {'ДА' if self.window_manager else 'НЕТ'}")
        print(f"Горячие клавиши: {'ДА' if self.hotkey_manager else 'НЕТ'}")
        print(f"Игровая система: {'ДА' if self.game_controller else 'НЕТ'}")
        print(f"Система активна: {'ДА' if self.is_running else 'НЕТ'}")
        print("=" * 60)

        # Выводим подсказки по горячим клавишам
        if self.hotkey_manager and self.window_config:
            hotkeys = self.window_config.get("hotkeys", {})
            if hotkeys:
                print("\nГОРЯЧИЕ КЛАВИШИ:")
                for action, key in hotkeys.items():
                    action_name = action.replace('_', ' ').title()
                    print(f"  {key:20} - {action_name}")

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
    print("ВНИМАНИЕ: Новые аккаунты проходят обучающий матч!")
    print("Система автоматически пропустит его при запуске.")
    print("=" * 60)
    print("Функции:")
    print("  1. Запуск 5 окон Dota 2 в песочницах")
    print("  2. Автоматический пропуск обучающего матча")
    print("  3. Автоматическое расположение окон в сетке")
    print("  4. Создание пати (если аккаунты друзья)")
    print("  5. Поиск матча или игра с ботами")
    print("  6. Автоматизация игрового процесса")
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
    parser.add_argument('--skip-tutorial', action='store_true', help='Пропустить обучающий матч')
    parser.add_argument('--start-party', action='store_true', help='Запустить только сбор пати')
    parser.add_argument('--start-match', action='store_true', help='Запустить только поиск матча')
    parser.add_argument('--layout', type=str, default='2x3', choices=['2x3', 'custom', 'single'],
                        help='Схема расположения окон')

    args = parser.parse_args()

    # Режим остановки
    if args.stop:
        print("Режим остановки...")
        system.initialize()
        system.stop_system()
        return

    # Режим только пропуска обучения
    if args.skip_tutorial:
        print("Режим пропуска обучающего матча...")
        if system.initialize():
            system.skip_tutorials()
        return

    # Режим только расположения окон
    if args.arrange_windows:
        print("Режим расположения окон...")
        if system.setup_window_manager():
            system.arrange_windows(args.layout)
        return

    # Режим только сбора пати
    if args.start_party:
        print("Режим сбора пати...")
        if system.setup_game_system():
            system.start_party_sequence()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nЗавершение...")
        return

    # Режим только поиска матча
    if args.start_match:
        print("Режим поиска матча...")
        if system.setup_game_system():
            system.start_match_search()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nЗавершение...")
        return

    # Тестовый режим
    if args.test:
        print("ТЕСТОВЫЙ РЕЖИМ")
        try:
            from test_single_bot import main as test_main
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
        print("\nСистема запущена успешно!")
        print("\nВАЖНО:")
        print("1. Новые аккаунты пройдут обучающий матч (автоматически пропускается)")
        print("2. Для создания пати аккаунты должны быть друзьями в Steam")
        print("3. Если друзей нет, система запустит игру с ботами")
        print("\nСтатус будет обновляться автоматически.")
        print("Для остановки нажмите Ctrl+C")

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
            print("\n\nПолучен запрос на остановку...")
            system.stop_system()

    else:
        logger.error("Не удалось запустить систему")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
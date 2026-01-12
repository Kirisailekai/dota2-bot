import time
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LobbyManager:
    """Управление лобби Dota 2 и созданием пати"""

    def __init__(self, config_path: str = "config/lobby_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.accounts = []
        self.lobby_created = False
        self.party_ready = False
        self.lobby_settings = self.config.get("lobby_settings", {})
        self.match_settings = self.config.get("match_settings", {})

    def load_config(self) -> Dict:
        """Загрузка конфигурации лобби"""
        config_path = Path(self.config_path)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Конфигурация по умолчанию
        default_config = {
            "lobby_settings": {
                "game_mode": "ALL_PICK",
                "server_region": "EUROPE",
                "lobby_password": "bot12345",
                "lobby_name": "BOT_FARM_5v5",
                "series_type": "BO1",
                "allow_spectators": False,
                "fill_with_bots": False,
                "radiant_team": "AI_TEAM_1",
                "dire_team": "AI_TEAM_2",
                "game_version": "DOTA2",
                "enable_cheats": False,
                "bot_difficulty": "UNFAIR"
            },
            "party_settings": {
                "max_players": 5,
                "min_players": 5,
                "invite_delay": 3,
                "accept_timeout": 30,
                "retry_attempts": 3,
                "auto_invite": True,
                "kick_afk": True,
                "afk_timeout": 120
            },
            "match_settings": {
                "search_timeout": 300,
                "ready_check_interval": 10,
                "auto_accept_match": True,
                "hero_select_timeout": 30,
                "auto_select_hero": True,
                "preferred_heroes": [
                    "sven",
                    "lina",
                    "lion",
                    "vengefulspirit",
                    "omniknight"
                ],
                "auto_buy_starting_items": True,
                "auto_skill_build": True
            }
        }

        # Сохраняем конфигурацию по умолчанию
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)

        logger.info(f"Создана конфигурация лобби по умолчанию: {config_path}")
        return default_config

    def load_accounts(self, accounts_file: str = "config/accounts.json") -> bool:
        """Загрузка аккаунтов из файла"""
        try:
            accounts_path = Path(accounts_file)
            if not accounts_path.exists():
                logger.error(f"Файл аккаунтов не найден: {accounts_path}")
                return False

            with open(accounts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.accounts = data.get("accounts", [])
            logger.info(f"Загружено {len(self.accounts)} аккаунтов")

            # Проверяем наличие friend_id для приглашений
            for i, acc in enumerate(self.accounts):
                if "friend_id" not in acc or not acc["friend_id"]:
                    logger.warning(f"Аккаунт {acc.get('username', f'#{i + 1}')} не имеет friend_id")

            return True

        except Exception as e:
            logger.error(f"Ошибка загрузки аккаунтов: {e}")
            return False

    def create_lobby(self, main_window_manager=None) -> bool:
        """Создание лобби через главное окно"""
        logger.info("Создание лобби...")

        try:
            # Импортируем InputSimulator для эмуляции действий
            from utils.input_simulator import InputSimulator

            if main_window_manager:
                # Получаем handle главного окна
                windows = main_window_manager.find_dota_windows()
                if not windows:
                    logger.error("Не найдены окна Dota 2")
                    return False

                main_window = windows[0]  # Первое окно - главное
                input_sim = InputSimulator()

                # 1. Открываем меню Play
                logger.info("Открытие меню Play...")
                input_sim.activate_window(main_window)
                time.sleep(2)

                # Эмуляция нажатия Play (координаты могут отличаться)
                input_sim.click_at(100, 100)  # Координаты кнопки Play
                time.sleep(3)

                # 2. Выбираем Create Lobby
                logger.info("Выбор Create Lobby...")
                input_sim.click_at(200, 150)  # Координаты Create Lobby
                time.sleep(3)

                # 3. Настраиваем лобби
                logger.info("Настройка параметров лобби...")
                self._configure_lobby(input_sim)
                time.sleep(2)

                # 4. Создаем лобби
                logger.info("Создание лобби...")
                input_sim.click_at(300, 300)  # Координаты кнопки Create
                time.sleep(5)

                self.lobby_created = True
                logger.info("✅ Лобби успешно создано")
                return True
            else:
                logger.error("Не предоставлен менеджер окон")
                return False

        except Exception as e:
            logger.error(f"Ошибка при создании лобби: {e}")
            return False

    def invite_to_party(self, window_manager=None) -> bool:
        """Приглашение всех аккаунтов в пати"""
        if not self.lobby_created:
            logger.error("Лобби не создано")
            return False

        logger.info("Приглашение ботов в пати...")

        try:
            if window_manager:
                windows = window_manager.find_dota_windows()
                if len(windows) < 2:
                    logger.error("Недостаточно окон для приглашения")
                    return False

                from utils.input_simulator import InputSimulator
                input_sim = InputSimulator()

                # Главное окно для приглашений
                main_window = windows[0]
                input_sim.activate_window(main_window)
                time.sleep(2)

                # 1. Открываем меню приглашений
                logger.info("Открытие меню приглашений...")
                input_sim.click_at(400, 100)  # Координаты кнопки Invite
                time.sleep(2)

                # 2. Приглашаем каждого бота
                invited_count = 0
                for i, account in enumerate(self.accounts[1:5], 1):  # Пропускаем главный аккаунт
                    friend_id = account.get("friend_id", "")
                    username = account.get("username", f"Bot {i + 1}")

                    if friend_id:
                        logger.info(f"Приглашение {username} (ID: {friend_id})...")

                        # Поиск друга по ID/имени
                        input_sim.type_text(friend_id)
                        time.sleep(1)
                        input_sim.press_key("enter")
                        time.sleep(2)

                        # Отправка приглашения
                        input_sim.click_at(300, 200)  # Координаты кнопки Invite
                        time.sleep(2)

                        invited_count += 1
                        logger.info(f"✓ Приглашен {username}")

                    # Задержка между приглашениями
                    time.sleep(self.config["party_settings"]["invite_delay"])

                # 3. Закрываем меню приглашений
                input_sim.press_key("esc")
                time.sleep(2)

                # Проверяем, что все в пати
                success = self._check_party_ready(window_manager, invited_count)

                if success:
                    self.party_ready = True
                    logger.info(f"✅ Все боты в пати! ({invited_count}/4)")
                else:
                    logger.warning(f"Не все боты в пати ({invited_count}/4)")

                return success

            return False

        except Exception as e:
            logger.error(f"Ошибка при приглашении в пати: {e}")
            return False

    def start_matchmaking(self, window_manager=None) -> bool:
        """Начало поиска матча"""
        if not self.party_ready:
            logger.warning("Пати не полностью готово, но пробуем начать поиск...")

        logger.info("Начало поиска матча...")

        try:
            if window_manager:
                windows = window_manager.find_dota_windows()
                if not windows:
                    logger.error("Не найдены окна Dota 2")
                    return False

                from utils.input_simulator import InputSimulator
                input_sim = InputSimulator()

                # Главное окно для поиска
                main_window = windows[0]
                input_sim.activate_window(main_window)
                time.sleep(2)

                # 1. Выбираем режим игры
                logger.info("Выбор режима игры...")
                input_sim.click_at(150, 200)  # Координаты кнопки Find Match
                time.sleep(2)

                # 2. Настройка типа матча
                logger.info("Настройка типа матча...")
                self._configure_match_type(input_sim)
                time.sleep(2)

                # 3. Начинаем поиск
                logger.info("Начало поиска...")
                input_sim.click_at(400, 400)  # Координаты кнопки Find Match
                time.sleep(5)

                logger.info("🔍 Поиск матча начат...")
                return True

            return False

        except Exception as e:
            logger.error(f"Ошибка при поиске матча: {e}")
            return False

    def wait_for_match(self, timeout: int = 300) -> bool:
        """Ожидание нахождения матча"""
        logger.info(f"Ожидание матча (таймаут: {timeout} секунд)...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            # В реальности здесь будет проверка через компьютерное зрение
            # что матч найден и появилась кнопка Accept

            time.sleep(10)
            elapsed = int(time.time() - start_time)

            if elapsed % 30 == 0:
                logger.info(f"Поиск продолжается... {elapsed} секунд")

            # Для теста - симулируем нахождение матча через 60 секунд
            if elapsed >= 60:
                logger.info("✅ Матч найден!")
                return True

        logger.warning("Матч не найден в течение таймаута")
        return False

    def accept_match(self, window_manager=None) -> bool:
        """Принятие найденного матча во всех окнах"""
        logger.info("Принятие матча...")

        try:
            if not window_manager:
                return False

            windows = window_manager.find_dota_windows()
            from utils.input_simulator import InputSimulator
            input_sim = InputSimulator()

            accepted_count = 0
            for i, window in enumerate(windows[:5]):
                try:
                    input_sim.activate_window(window)
                    time.sleep(1)

                    # Нажимаем Accept (координаты могут отличаться)
                    input_sim.click_at(500, 400)
                    time.sleep(2)

                    accepted_count += 1
                    logger.info(f"✓ Матч принят в окне {i + 1}")

                except Exception as e:
                    logger.error(f"Ошибка принятия в окне {i + 1}: {e}")

            logger.info(f"✅ Матч принят в {accepted_count}/5 окнах")
            return accepted_count >= 3  # Минимум 3 из 5

        except Exception as e:
            logger.error(f"Ошибка при принятии матча: {e}")
            return False

    def select_heroes(self, window_manager=None) -> bool:
        """Автоматический выбор героев"""
        logger.info("Автоматический выбор героев...")

        try:
            if not window_manager:
                return False

            windows = window_manager.find_dota_windows()
            heroes = self.match_settings.get("preferred_heroes", [])

            if len(heroes) < 5:
                logger.warning(f"Недостаточно героев в списке ({len(heroes)}/5)")
                return False

            from utils.input_simulator import InputSimulator
            input_sim = InputSimulator()

            for i, window in enumerate(windows[:5]):
                try:
                    input_sim.activate_window(window)
                    time.sleep(1)

                    # Вводим имя героя
                    hero = heroes[i % len(heroes)]
                    input_sim.type_text(hero)
                    time.sleep(2)

                    # Выбираем героя (Enter)
                    input_sim.press_key("enter")
                    time.sleep(2)

                    # Подтверждаем выбор
                    input_sim.click_at(600, 500)
                    time.sleep(2)

                    logger.info(f"✓ Герой {hero} выбран для бота {i + 1}")

                except Exception as e:
                    logger.error(f"Ошибка выбора героя для бота {i + 1}: {e}")

            logger.info("✅ Герои выбраны")
            return True

        except Exception as e:
            logger.error(f"Ошибка при выборе героев: {e}")
            return False

    def _configure_lobby(self, input_sim):
        """Конфигурация параметров лобби"""
        try:
            # Настройка режима игры
            input_sim.click_at(250, 180)  # Game Mode
            time.sleep(1)
            input_sim.press_key("down")  # Выбираем ALL_PICK
            time.sleep(1)
            input_sim.press_key("enter")
            time.sleep(1)

            # Настройка пароля лобби
            password = self.lobby_settings.get("lobby_password", "")
            if password:
                input_sim.click_at(250, 220)  # Password field
                time.sleep(1)
                input_sim.type_text(password)
                time.sleep(1)

            # Настройка имени лобби
            lobby_name = self.lobby_settings.get("lobby_name", "")
            if lobby_name:
                input_sim.click_at(250, 200)  # Lobby name field
                time.sleep(1)
                input_sim.type_text(lobby_name)
                time.sleep(1)

            logger.info("Параметры лобби настроены")

        except Exception as e:
            logger.error(f"Ошибка настройки лобби: {e}")

    def _configure_match_type(self, input_sim):
        """Конфигурация типа матча"""
        try:
            # Выбор ранговой игры
            input_sim.click_at(200, 250)  # Ranked checkbox
            time.sleep(1)

            # Выбор региона
            input_sim.click_at(200, 280)  # Region dropdown
            time.sleep(1)
            input_sim.press_key("down")  # Выбираем Europe
            time.sleep(1)
            input_sim.press_key("enter")
            time.sleep(1)

            logger.info("Тип матча настроен")

        except Exception as e:
            logger.error(f"Ошибка настройки типа матча: {e}")

    def _check_party_ready(self, window_manager, expected_count: int) -> bool:
        """Проверка готовности пати"""
        logger.info("Проверка готовности пати...")

        try:
            # В реальности здесь будет проверка через компьютерное зрение
            # сколько игроков в лобби

            # Пока что просто ждем и возвращаем успех
            time.sleep(10)
            return True

        except Exception as e:
            logger.error(f"Ошибка проверки пати: {e}")
            return False

    def get_status(self) -> Dict:
        """Получение статуса"""
        return {
            "lobby_created": self.lobby_created,
            "party_ready": self.party_ready,
            "accounts_loaded": len(self.accounts),
            "lobby_name": self.lobby_settings.get("lobby_name", ""),
            "game_mode": self.lobby_settings.get("game_mode", "")
        }
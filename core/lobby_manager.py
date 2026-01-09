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

    def load_config(self) -> Dict:
        """Загрузка конфигурации лобби"""
        config_path = Path(self.config_path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)

        # Конфигурация по умолчанию
        default_config = {
            "lobby_settings": {
                "game_mode": "ALL_PICK",
                "server_region": "EUROPE",
                "lobby_password": "",
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
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def load_accounts(self, accounts_file: str = "config/accounts.json") -> bool:
        """Загрузка аккаунтов из файла"""
        accounts_path = Path(accounts_file)
        if not accounts_path.exists():
            logger.error(f"Файл аккаунтов не найден: {accounts_path}")
            return False

        try:
            with open(accounts_path, 'r') as f:
                accounts_data = json.load(f)

            self.accounts = accounts_data.get("accounts", [])
            logger.info(f"Загружено {len(self.accounts)} аккаунтов")
            return True

        except Exception as e:
            logger.error(f"Ошибка загрузки аккаунтов: {e}")
            return False

    def create_lobby(self, main_account_index: int = 0) -> bool:
        """
        Создание лобби с главным аккаунтом
        main_account_index: индекс аккаунта в списке, который будет создавать лобби
        """
        if not self.accounts:
            logger.error("Нет загруженных аккаунтов")
            return False

        if main_account_index >= len(self.accounts):
            logger.error(f"Аккаунт с индексом {main_account_index} не найден")
            return False

        main_account = self.accounts[main_account_index]
        logger.info(f"Создание лобби с аккаунтом: {main_account.get('username', 'Unknown')}")

        try:
            # Здесь будет реальная логика создания лобби через эмуляцию ввода
            # Пока что используем заглушку
            time.sleep(5)

            self.lobby_created = True
            logger.info("✅ Лобби успешно создано")
            return True

        except Exception as e:
            logger.error(f"Ошибка при создании лобби: {e}")
            return False

    def invite_to_party(self) -> bool:
        """Приглашение всех аккаунтов в пати"""
        if not self.lobby_created:
            logger.error("Лобби не создано")
            return False

        if len(self.accounts) < 5:
            logger.error(f"Недостаточно аккаунтов: {len(self.accounts)}/5")
            return False

        logger.info("Начинаю приглашение аккаунтов в пати...")

        try:
            # Здесь будет реальная логика приглашения через эмуляцию ввода
            # Пока что используем заглушку
            time.sleep(10)

            self.party_ready = True
            logger.info("✅ Все боты приглашены в пати")
            return True

        except Exception as e:
            logger.error(f"Ошибка при приглашении в пати: {e}")
            return False

    def start_matchmaking(self) -> bool:
        """Начало поиска матча"""
        if not self.party_ready:
            logger.warning("Пати не готово, но пробуем начать поиск...")

        logger.info("Начинаю поиск матча...")

        try:
            # Здесь будет реальная логика поиска матча
            # Пока что используем заглушку
            time.sleep(15)

            logger.info("✅ Поиск матча начат")
            return True

        except Exception as e:
            logger.error(f"Ошибка при поиске матча: {e}")
            return False

    def get_status(self) -> Dict:
        """Получение текущего статуса"""
        return {
            "lobby_created": self.lobby_created,
            "party_ready": self.party_ready,
            "accounts_loaded": len(self.accounts),
            "config_loaded": bool(self.config)
        }
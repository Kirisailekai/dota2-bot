import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GameController:
    """Контроллер игрового процесса Dota 2"""

    def __init__(self, window_manager=None):
        self.window_manager = window_manager
        self.lobby_manager = None
        self.game_state = "IDLE"  # IDLE, LOBBY, MATCHMAKING, HERO_SELECT, IN_GAME, POST_GAME
        self.game_start_time = None
        self.match_id = None
        self.heroes_selected = []
        self.is_running = False

    def set_lobby_manager(self, lobby_manager):
        """Установка менеджера лобби"""
        self.lobby_manager = lobby_manager

    def start_game_sequence(self) -> bool:
        """Запуск полной последовательности игры"""
        logger.info("🚀 Запуск игровой последовательности...")
        self.is_running = True

        try:
            # 1. Загрузка аккаунтов
            logger.info("1. Загрузка аккаунтов...")
            if not self.lobby_manager or not self.lobby_manager.load_accounts():
                logger.error("Не удалось загрузить аккаунты")
                return False

            # 2. Создание лобби
            logger.info("2. Создание лобби...")
            if not self.lobby_manager.create_lobby():
                logger.error("Не удалось создать лобби")
                return False

            self.game_state = "LOBBY"
            time.sleep(5)

            # 3. Приглашение в пати
            logger.info("3. Приглашение в пати...")
            if not self.lobby_manager.invite_to_party():
                logger.warning("Проблемы с приглашением, но продолжаем...")

            time.sleep(10)

            # 4. Поиск матча
            logger.info("4. Начало поиска матча...")
            if not self.lobby_manager.start_matchmaking():
                logger.error("Не удалось начать поиск матча")
                return False

            self.game_state = "MATCHMAKING"
            time.sleep(30)

            # 5. Имитация начала игры
            logger.info("5. Игра начинается...")
            self.game_state = "IN_GAME"
            self.game_start_time = datetime.now()

            logger.info("✅ Игровая последовательность завершена!")
            return True

        except Exception as e:
            logger.error(f"Ошибка в игровой последовательности: {e}")
            return False

    def monitor_game_state(self):
        """Мониторинг состояния игры"""
        logger.info("Начало мониторинга игрового состояния...")

        try:
            while self.is_running and self.game_state == "IN_GAME":
                self._monitor_in_game()
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("Мониторинг прерван пользователем")
        except Exception as e:
            logger.error(f"Ошибка мониторинга: {e}")

    def _monitor_in_game(self):
        """Мониторинг состояния во время игры"""
        if not self.game_start_time:
            return

        game_duration = datetime.now() - self.game_start_time
        minutes = int(game_duration.total_seconds() / 60)

        # Имитация игры (30 минут)
        if minutes >= 30:
            self.game_state = "POST_GAME"
            logger.info("🎮 Игра завершена!")
            self._handle_post_game()
        elif minutes % 5 == 0:
            logger.info(f"Игра продолжается: {minutes} минут")

    def _handle_post_game(self):
        """Обработка пост-игрового экрана"""
        logger.info("Завершение игровой сессии...")
        time.sleep(10)
        self.game_state = "IDLE"
        self.game_start_time = None

    def stop(self):
        """Остановка контроллера"""
        self.is_running = False
        logger.info("Игровой контроллер остановлен")

    def get_game_status(self) -> Dict:
        """Получение статуса игры"""
        return {
            "game_state": self.game_state,
            "game_start_time": self.game_start_time,
            "match_id": self.match_id,
            "heroes_selected": self.heroes_selected,
            "game_duration": str(datetime.now() - self.game_start_time) if self.game_start_time else None
        }
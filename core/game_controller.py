# core/game_controller.py
"""
Контроллер игрового процесса
"""

import time
import logging
from typing import Dict, List, Optional
import pyautogui
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class GameController:
    def __init__(self, window_manager=None):
        self.window_manager = window_manager
        self.lobby_manager = None
        self.accounts = []
        self.bot_states = {}
        self.is_running = False

        # Координаты для разных разрешений (1024x768)
        self.coords = {
            'main_menu_play_button': (512, 384),  # Центр
            'skip_tutorial_button': (512, 600),  # Внизу
            'create_lobby_button': (200, 150),  # Примерные координаты
            'invite_friends_button': (800, 150),
            'search_box': (512, 200),
            'search_result_1': (512, 250),
            'invite_to_party_button': (700, 250),
            'start_match_button': (512, 700),
            'accept_match_button': (512, 500),
            'hero_select_grid': (512, 384),
        }

        # Шаблоны для распознавания (можно добавить скриншоты)
        self.templates = {}

    def set_lobby_manager(self, lobby_manager):
        """Установка менеджера лобби"""
        self.lobby_manager = lobby_manager

    def skip_tutorial(self, bot_index: int) -> bool:
        """Пропуск обучающего матча для бота"""
        try:
            if not self.window_manager:
                return False

            # Активируем окно бота
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Нажимаем ESC несколько раз (выйти из любых меню)
            for _ in range(3):
                pyautogui.press('esc')
                time.sleep(1)

            # Пытаемся найти кнопку "Skip Tutorial" или "Пропустить обучение"
            # Используем поиск по шаблону или просто кликаем в предполагаемое место
            screen = self.capture_screen(bot_index)

            # Простая эвристика: если в центре экрана что-то похожее на игру,
            # нажимаем ESC и пробуем найти кнопку выхода
            pyautogui.press('esc')
            time.sleep(2)

            # Еще раз ESC для выхода в главное меню
            pyautogui.press('esc')
            time.sleep(2)

            # Нажимаем Enter (иногда помогает)
            pyautogui.press('enter')
            time.sleep(2)

            logger.info(f"Бот {bot_index + 1}: попытка пропуска обучения завершена")
            return True

        except Exception as e:
            logger.error(f"Ошибка пропуска обучения для бота {bot_index + 1}: {e}")
            return False

    def check_main_menu(self, bot_index: int) -> bool:
        """Проверка, находится ли бот в главном меню"""
        try:
            if not self.window_manager:
                return False

            # Активируем окно
            self.window_manager.activate_window(bot_index)
            time.sleep(0.5)

            # Делаем скриншот
            screen = self.capture_screen(bot_index)

            # Простая проверка: ищем черные полосы по бокам (меню Dota 2)
            # Или проверяем цвет в определенных точках
            height, width = screen.shape[:2]

            # Проверяем точки, где обычно находятся элементы меню
            points_to_check = [
                (width // 2, 50),  # Верхняя часть
                (100, height // 2),  # Левая часть
                (width - 100, height // 2),  # Правая часть
                (width // 2, height - 50),  # Нижняя часть
            ]

            # Если большинство точек не черные (меню имеет цвет), то вероятно главное меню
            black_threshold = 30
            non_black_points = 0

            for x, y in points_to_check:
                if 0 <= x < width and 0 <= y < height:
                    pixel = screen[y, x]
                    if isinstance(pixel, np.ndarray):
                        # Для цветного изображения
                        brightness = np.mean(pixel)
                        if brightness > black_threshold:
                            non_black_points += 1

            in_menu = non_black_points >= 2

            if in_menu:
                logger.debug(f"Бот {bot_index + 1}: обнаружено главное меню")

            return in_menu

        except Exception as e:
            logger.error(f"Ошибка проверки главного меню для бота {bot_index + 1}: {e}")
            return False

    def capture_screen(self, bot_index: int):
        """Скриншот окна бота"""
        if not self.window_manager:
            return None

        return self.window_manager.capture_window(bot_index)

    def create_lobby(self, bot_index: int) -> bool:
        """Создание лобби ботом"""
        try:
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Нажимаем Play (обычно в центре)
            pyautogui.click(self.coords['main_menu_play_button'])
            time.sleep(2)

            # Нажимаем Create Lobby
            pyautogui.click(self.coords['create_lobby_button'])
            time.sleep(3)

            logger.info(f"Бот {bot_index + 1}: лобби создано")
            return True

        except Exception as e:
            logger.error(f"Ошибка создания лобби ботом {bot_index + 1}: {e}")
            return False

    def invite_by_search(self, leader_index: int, target_index: int, target_name: str) -> bool:
        """Приглашение бота через поиск по нику"""
        try:
            self.window_manager.activate_window(leader_index)
            time.sleep(1)

            # Нажимаем кнопку Invite Friends
            pyautogui.click(self.coords['invite_friends_button'])
            time.sleep(2)

            # Кликаем в поле поиска
            pyautogui.click(self.coords['search_box'])
            time.sleep(1)

            # Вводим ник бота
            pyautogui.write(target_name)
            time.sleep(2)

            # Кликаем на первый результат
            pyautogui.click(self.coords['search_result_1'])
            time.sleep(1)

            # Нажимаем Invite to Party
            pyautogui.click(self.coords['invite_to_party_button'])
            time.sleep(2)

            logger.info(f"Бот {leader_index + 1} пригласил {target_name}")
            return True

        except Exception as e:
            logger.error(f"Ошибка приглашения бота {target_index + 1}: {e}")
            return False

    def check_party_size(self, bot_index: int) -> int:
        """Проверка количества игроков в пати"""
        # Простая реализация - возвращаем предполагаемое значение
        # В реальной реализации нужно распознавать интерфейс
        return 1  # По умолчанию 1 (только сам бот)

    def select_game_mode(self, bot_index: int, mode: str = "all_pick") -> bool:
        """Выбор режима игры"""
        try:
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Эти действия зависят от интерфейса
            # Упрощенная версия: просто нажимаем кнопку старта
            pyautogui.click(self.coords['start_match_button'])
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Ошибка выбора режима игры для бота {bot_index + 1}: {e}")
            return False

    def start_match_search(self, bot_index: int) -> bool:
        """Запуск поиска матча"""
        try:
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Нажимаем кнопку поиска
            pyautogui.click(self.coords['start_match_button'])
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Ошибка запуска поиска для бота {bot_index + 1}: {e}")
            return False

    def get_matchmaking_status(self, bot_index: int) -> Dict:
        """Получение статуса поиска матча"""
        # Упрощенная реализация
        return {
            'match_found': False,
            'search_time': 0,
            'players_found': 0
        }

    def accept_match(self, bot_index: int) -> bool:
        """Принятие найденного матча"""
        try:
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Нажимаем Accept
            pyautogui.click(self.coords['accept_match_button'])
            time.sleep(1)

            return True

        except Exception as e:
            logger.error(f"Ошибка принятия матча ботом {bot_index + 1}: {e}")
            return False

    def cancel_search(self, bot_index: int) -> bool:
        """Отмена поиска матча"""
        try:
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Нажимаем Cancel (обычно там же где и Accept)
            pyautogui.click(self.coords['accept_match_button'])
            time.sleep(1)

            return True

        except Exception as e:
            logger.error(f"Ошибка отмены поиска для бота {bot_index + 1}: {e}")
            return False

    def play_with_bots(self, bot_index: int) -> bool:
        """Запуск игры с ботами (альтернатива пати)"""
        try:
            self.window_manager.activate_window(bot_index)
            time.sleep(1)

            # Play -> Practice with Bots
            pyautogui.click(self.coords['main_menu_play_button'])
            time.sleep(2)

            # Выбираем режим с ботами
            pyautogui.click(300, 300)  # Примерные координаты
            time.sleep(1)

            # Start
            pyautogui.click(self.coords['start_match_button'])
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Ошибка запуска игры с ботами для бота {bot_index + 1}: {e}")
            return False

    def get_bot_state(self, bot_index: int) -> Dict:
        """Получение состояния бота"""
        # Проверяем основные состояния
        in_menu = self.check_main_menu(bot_index)

        return {
            'in_main_menu': in_menu,
            'in_game': not in_menu,  # Упрощенно
            'status': 'in_menu' if in_menu else 'in_game'
        }

    def stop(self):
        """Остановка контроллера"""
        self.is_running = False
        logger.info("Игровой контроллер остановлен")
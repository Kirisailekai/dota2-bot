# ai/bot_ai.py
"""
Базовый класс ИИ бота
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
from datetime import datetime
from pathlib import Path


class BotAI(ABC):
    """Абстрактный класс ИИ бота"""

    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.is_active = False
        self.config = self.load_config()
        self.logger = self.setup_logger()

        # Состояние бота
        self.game_state = {}
        self.last_action_time = None
        self.performance_stats = {
            'actions_count': 0,
            'avg_response_time': 0,
            'errors_count': 0
        }

        self.logger.info(f"Инициализирован бот ID: {bot_id}")

    def setup_logger(self):
        """Настройка логгера для бота"""
        logger = logging.getLogger(f'BotAI_{self.bot_id}')

        if not logger.handlers:
            # Создаем директорию для логов бота
            log_dir = Path(f"logs/bot_{self.bot_id}")
            log_dir.mkdir(parents=True, exist_ok=True)

            # Файловый хендлер
            file_handler = logging.FileHandler(
                log_dir / f"bot_{self.bot_id}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.INFO)

            # Форматтер
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.setLevel(logging.INFO)

        return logger

    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации бота"""
        config_path = Path(f"config/DOTA_BOT_{self.bot_id + 1}.ini")

        if config_path.exists():
            try:
                config = {}
                with open(config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                return config
            except Exception as e:
                print(f"Ошибка загрузки конфигурации бота {self.bot_id}: {e}")

        # Конфигурация по умолчанию
        return {
            'hero_preference': 'random',
            'game_mode': 'mid',
            'aggression_level': 'medium',
            'reaction_delay': '0.5',
            'performance_mode': 'balanced'
        }

    def start(self):
        """Запуск бота"""
        self.is_active = True
        self.logger.info("Бот запущен")

    def stop(self):
        """Остановка бота"""
        self.is_active = False
        self.save_performance_stats()
        self.logger.info("Бот остановлен")

    def update_game_state(self, state_data: Dict[str, Any]):
        """Обновление состояния игры (для второго разработчика)"""
        self.game_state = state_data
        self.last_action_time = datetime.now()

    @abstractmethod
    def make_decision(self) -> Dict[str, Any]:
        """
        Принятие решения (абстрактный метод)
        Второй разработчик реализует эту логику
        """
        pass

    @abstractmethod
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Выполнение действия (абстрактный метод)
        Второй разработчик реализует эту логику
        """
        pass

    def save_performance_stats(self):
        """Сохранение статистики производительности"""
        stats_file = Path(f"logs/bot_{self.bot_id}/performance.json")

        try:
            stats_data = {
                'bot_id': self.bot_id,
                'timestamp': datetime.now().isoformat(),
                'stats': self.performance_stats,
                'config': self.config
            }

            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Ошибка сохранения статистики: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Получение текущего статуса бота"""
        return {
            'bot_id': self.bot_id,
            'is_active': self.is_active,
            'config': self.config,
            'performance': self.performance_stats,
            'game_state_keys': list(self.game_state.keys()) if self.game_state else []
        }
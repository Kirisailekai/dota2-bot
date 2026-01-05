# Конфигурация проекта
import os
from pathlib import Path


class Config:
    # Пути
    PROJECT_ROOT = Path(__file__).parent.parent
    LOGS_DIR = PROJECT_ROOT / "logs"
    SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

    # Sandboxie
    SANDBOXIE_PATH = r"C:\Sandboxie\Start.exe"
    BOX_NAMES = [f"DotaBox{i}" for i in range(1, 6)]

    # Dota 2
    STEAM_PATH = r"C:\Program Files (x86)\Steam\steam.exe"
    DOTA_APP_ID = 570
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768

    # AI Settings
    BOT_THINKING_FPS = 2  # Как часто бот принимает решения
    CONFIDENCE_THRESHOLD = 0.7  # Порог уверенности для действий

    # Network
    COORDINATOR_HOST = "192.168.1.100"  # IP первого компьютера
    COORDINATOR_PORT = 8765

    @classmethod
    def setup_directories(cls):
        """Создание необходимых директорий"""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.SCREENSHOTS_DIR.mkdir(exist_ok=True)
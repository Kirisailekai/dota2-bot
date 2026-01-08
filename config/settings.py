# config/settings.py
"""
Настройки системы
"""

import json
from pathlib import Path
from typing import Dict, Any


class Settings:
    """Управление настройками системы"""

    def __init__(self):
        self.settings_file = Path("config/settings.json")
        self.default_settings = {
            "system": {
                "max_bots": 5,
                "auto_restart": True,
                "restart_delay": 60,
                "log_level": "INFO",
                "performance_mode": "balanced"
            },
            "sandboxie": {
                "install_path": "C:/Program Files/Sandboxie-Plus",
                "config_path": "config/sandbox_configs",
                "create_sandboxes": True
            },
            "game": {
                "dota_path": "",
                "steam_path": "",
                "launch_args": "-novid -console -high -nojoy -nosteamcontroller",
                "window_width": 1024,
                "window_height": 768
            },
            "ai": {
                "decision_interval": 0.5,
                "vision_enabled": True,
                "input_enabled": True,
                "training_mode": False
            },
            "network": {
                "inter_bot_communication": True,
                "master_server": "localhost",
                "master_port": 8080,
                "sync_interval": 1.0
            }
        }

        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Загрузка настроек"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    return self.merge_settings(self.default_settings, loaded_settings)
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")

        # Сохраняем настройки по умолчанию
        self.save_settings(self.default_settings)
        return self.default_settings.copy()

    def merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """Рекурсивное слияние настроек"""
        merged = default.copy()

        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_settings(merged[key], value)
            else:
                merged[key] = value

        return merged

    def save_settings(self, settings: Dict = None):
        """Сохранение настроек"""
        if settings is None:
            settings = self.settings

        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False

    def get(self, key_path: str, default=None) -> Any:
        """Получение значения по пути"""
        keys = key_path.split('.')
        value = self.settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any):
        """Установка значения по пути"""
        keys = key_path.split('.')
        current = self.settings

        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
        self.save_settings()


# Синглтон
settings = Settings()
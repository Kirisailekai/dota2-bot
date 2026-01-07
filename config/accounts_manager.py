import json
import hashlib
from pathlib import Path
from typing import List, Dict
import logging
from cryptography.fernet import Fernet
import base64


class AccountsManager:
    def __init__(self, config_file: str = "config/accounts.json"):
        self.config_file = Path(config_file)
        self.accounts = []
        self.logger = logging.getLogger(__name__)
        self._load_accounts()

    def _load_accounts(self):
        """Загрузка аккаунтов из файла"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.accounts = json.load(f)
                self.logger.info(f"Загружено {len(self.accounts)} аккаунтов")
            else:
                self._create_default_config()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки аккаунтов: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """Создание конфигурации по умолчанию"""
        self.accounts = [
            {
                "username": "bot_account_1",
                "password": "password1",
                "steam_id": "76561198000000001",
                "sandbox": "DOTA_BOT_1",
                "enabled": True,
                "last_used": None
            },
            {
                "username": "bot_account_2",
                "password": "password2",
                "steam_id": "76561198000000002",
                "sandbox": "DOTA_BOT_2",
                "enabled": True,
                "last_used": None
            },
            {
                "username": "bot_account_3",
                "password": "password3",
                "steam_id": "76561198000000001",
                "sandbox": "DOTA_BOT_3",
                "enabled": True,
                "last_used": None
            },
            {
                "username": "bot_account_4",
                "password": "password4",
                "steam_id": "76561198000000001",
                "sandbox": "DOTA_BOT_4",
                "enabled": True,
                "last_used": None
            },
            {
                "username": "bot_account_5",
                "password": "password5",
                "steam_id": "76561198000000001",
                "sandbox": "DOTA_BOT_5",
                "enabled": True,
                "last_used": None
            },
        ]
        self.save_accounts()

    def save_accounts(self):
        """Сохранение аккаунтов в файл"""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.accounts, f, indent=2)
            self.logger.info("Аккаунты сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения аккаунтов: {e}")

    def get_accounts(self, enabled_only: bool = True) -> List[Dict]:
        """Получение списка аккаунтов"""
        if enabled_only:
            return [acc for acc in self.accounts if acc.get('enabled', True)]
        return self.accounts

    def get_account_by_sandbox(self, sandbox_name: str) -> Dict:
        """Получение аккаунта по имени песочницы"""
        for account in self.accounts:
            if account.get('sandbox') == sandbox_name:
                return account
        return None

    def rotate_accounts(self):
        """Ротация аккаунтов (например, для предотвращения блокировок)"""
        if self.accounts:
            # Перемещаем первый аккаунт в конец
            first = self.accounts.pop(0)
            self.accounts.append(first)
            self.save_accounts()
            self.logger.info("Аккаунты сротированы")

    def add_account(self, username: str, password: str, steam_id: str = None):
        """Добавление нового аккаунта"""
        new_account = {
            "username": username,
            "password": password,
            "steam_id": steam_id or f"76561198{hashlib.md5(username.encode()).hexdigest()[:8]}",
            "sandbox": f"DOTA_BOT_{len(self.accounts) + 1}",
            "enabled": True,
            "last_used": None
        }
        self.accounts.append(new_account)
        self.save_accounts()
        self.logger.info(f"Добавлен аккаунт: {username}")

    def disable_account(self, username: str):
        """Отключение аккаунта"""
        for account in self.accounts:
            if account['username'] == username:
                account['enabled'] = False
                self.save_accounts()
                self.logger.info(f"Аккаунт {username} отключен")
                return True
        return False
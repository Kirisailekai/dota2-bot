import json
import os
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import base64


@dataclass
class SteamAccount:
    id: int
    login: str
    password: str
    nickname: str
    steam_id: Optional[str] = None
    is_active: bool = True
    last_used: Optional[str] = None


class AccountsManager:
    def __init__(self, config_path: str = "config/accounts.json"):
        self.config_path = config_path
        self.accounts: List[SteamAccount] = []
        self.encryption_key = None
        self._load_encryption_key()

    def _load_encryption_key(self):
        """Загрузка или создание ключа шифрования"""
        key_path = "config/encryption.key"

        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Создаем новый ключ
            self.encryption_key = Fernet.generate_key()
            os.makedirs("config", exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(self.encryption_key)

    def _encrypt(self, text: str) -> str:
        """Шифрование текста"""
        if not self.encryption_key:
            return text

        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted_text: str) -> str:
        """Дешифрование текста"""
        if not self.encryption_key:
            return encrypted_text

        fernet = Fernet(self.encryption_key)
        decrypted = fernet.decrypt(base64.b64decode(encrypted_text))
        return decrypted.decode()

    def create_accounts_template(self):
        """Создание шаблона для 5 аккаунтов"""
        template_accounts = []

        for i in range(1, 6):
            account = SteamAccount(
                id=i,
                login=f"dota2bot{i}",
                password=f"password{i}_CHANGE_ME",  # Нужно изменить!
                nickname=f"Bot{i}_Player",
                is_active=True
            )
            template_accounts.append(asdict(account))

        # Сохраняем зашифрованные пароли
        encrypted_accounts = []
        for acc in template_accounts:
            encrypted_acc = acc.copy()
            encrypted_acc['password'] = self._encrypt(acc['password'])
            encrypted_accounts.append(encrypted_acc)

        os.makedirs("config", exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(encrypted_accounts, f, indent=2, ensure_ascii=False)

        print(f"[Accounts] Создан шаблон конфигурации в {self.config_path}")
        print("ВАЖНО: Измените логины и пароли на реальные!")

    def load_accounts(self) -> List[SteamAccount]:
        """Загрузка аккаунтов из файла"""
        if not os.path.exists(self.config_path):
            print(f"[Accounts] Файл {self.config_path} не найден. Создаю шаблон...")
            self.create_accounts_template()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                encrypted_accounts = json.load(f)

            accounts = []
            for acc_data in encrypted_accounts:
                # Дешифруем пароль
                decrypted_data = acc_data.copy()
                decrypted_data['password'] = self._decrypt(acc_data['password'])

                account = SteamAccount(**decrypted_data)
                accounts.append(account)

            self.accounts = accounts
            print(f"[Accounts] Загружено {len(accounts)} аккаунтов")
            return accounts

        except Exception as e:
            print(f"[Accounts] Ошибка загрузки аккаунтов: {e}")
            return []

    def get_account(self, account_id: int) -> Optional[SteamAccount]:
        """Получение аккаунта по ID"""
        for account in self.accounts:
            if account.id == account_id and account.is_active:
                return account
        return None

    def rotate_account(self, current_id: int) -> SteamAccount:
        """Ротация аккаунтов (следующий активный)"""
        active_accounts = [acc for acc in self.accounts if acc.is_active]
        if not active_accounts:
            raise ValueError("Нет активных аккаунтов")

        # Ищем следующий после current_id
        for account in active_accounts:
            if account.id > current_id:
                return account

        # Если не нашли, возвращаем первый
        return active_accounts[0]

    def update_last_used(self, account_id: int):
        """Обновление времени последнего использования"""
        from datetime import datetime

        for account in self.accounts:
            if account.id == account_id:
                account.last_used = datetime.now().isoformat()
                self._save_accounts()
                break

    def _save_accounts(self):
        """Сохранение аккаунтов в файл"""
        encrypted_accounts = []
        for account in self.accounts:
            acc_dict = asdict(account)
            # Шифруем пароль перед сохранением
            acc_dict['password'] = self._encrypt(acc_dict['password'])
            encrypted_accounts.append(acc_dict)

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(encrypted_accounts, f, indent=2, ensure_ascii=False)

    def get_launch_parameters(self, account_id: int) -> List[str]:
        """Получение параметров запуска Steam для аккаунта"""
        account = self.get_account(account_id)
        if not account:
            return []

        return [
            "-login", account.login, account.password,
            "-applaunch", "570"
        ]
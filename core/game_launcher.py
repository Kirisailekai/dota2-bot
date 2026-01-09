import time
import json
from typing import Dict, List, Optional
import logging
from pathlib import Path
from .sandbox_controller import SandboxController


class GameLauncher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.controller = SandboxController()
        self.accounts = self.load_accounts()

        # Проверяем наличие песочниц
        self.check_sandboxes()

    def load_accounts(self) -> List[Dict]:
        """Загрузка аккаунтов из файла"""
        try:
            accounts_path = Path("config/accounts.json")
            if not accounts_path.exists():
                self.logger.error("Файл accounts.json не найден")
                return []

            with open(accounts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Простая обработка - ищем ключ "accounts"
            if "accounts" in data:
                accounts = data["accounts"]
                # Проверяем, что каждый аккаунт имеет username и password
                valid_accounts = []
                for i, account in enumerate(accounts):
                    if isinstance(account, dict):
                        username = account.get("username", "")
                        password = account.get("password", "")
                        if username and password:
                            valid_accounts.append({
                                "username": username,
                                "password": password,
                                "friend_id": account.get("friend_id", ""),
                                "steam_id": account.get("steam_id", ""),
                                "preferred_role": account.get("preferred_role", "carry"),
                                "sandbox": f"DOTA_BOT_{i + 1}"
                            })
                        else:
                            self.logger.warning(f"Аккаунт {i + 1} не имеет username/password")
                    else:
                        self.logger.warning(f"Аккаунт {i + 1} не является словарем")

                self.logger.info(f"Загружено {len(valid_accounts)} валидных аккаунтов")
                return valid_accounts
            else:
                self.logger.error("Ключ 'accounts' не найден в файле")
                return []

        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка чтения JSON: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Ошибка загрузки аккаунтов: {e}")
            return []

    def check_sandboxes(self):
        """Проверка существования песочниц"""
        print("Проверка песочниц...")

        sandboxes_exist = True
        for i in range(1, 6):
            sandbox_name = f"DOTA_BOT_{i}"
            if not self.controller.is_sandbox_exists(sandbox_name):
                sandboxes_exist = False
                self.logger.warning(f"Песочница {sandbox_name} не найдена")
                break

        if sandboxes_exist:
            print("✓ Все песочницы найдены")
        else:
            print("⚠ Некоторые песочницы не найдены")

    def launch_single(self, account_index: int = 0, window_position: tuple = None) -> bool:
        """Запуск одного экземпляра Dota 2"""
        if not self.accounts:
            self.logger.error("Нет доступных аккаунтов")
            return False

        if account_index >= len(self.accounts):
            self.logger.error(f"Аккаунт с индексом {account_index} не найден. Доступно: {len(self.accounts)}")
            return False

        account = self.accounts[account_index]

        # Проверяем, что account - словарь
        if not isinstance(account, dict):
            self.logger.error(f"Аккаунт должен быть словарем, получен: {type(account)}")
            # Пытаемся преобразовать
            account = {
                'username': str(account),
                'password': '',
                'sandbox': f'DOTA_BOT_{account_index + 1}'
            }

        username = account.get('username', f'bot_{account_index + 1}')
        password = account.get('password', '')

        # Определяем песочницу
        sandbox_name = account.get('sandbox')
        if not sandbox_name:
            sandbox_name = f'DOTA_BOT_{account_index + 1}'

        print(f"Запуск Dota 2 для {username} в {sandbox_name}...")

        if window_position is None:
            window_position = (0, 0, 1024, 768)

        try:
            pid = self.controller.launch_steam(
                sandbox_name,
                username,
                password,
                window_position
            )

            if pid:
                self.logger.info(f"Запущен процесс с PID: {pid}")
                return True
            else:
                self.logger.error("Не удалось запустить Steam")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка запуска Steam: {e}")
            return False

    def launch_team(self, team_size: int = 5) -> Dict:
        """Запуск команды ботов"""
        print(f"Запуск команды из {team_size} ботов...")

        if not self.accounts:
            self.logger.error("Нет доступных аккаунтов")
            return {"status": "error", "message": "Нет доступных аккаунтов"}

        if len(self.accounts) < team_size:
            self.logger.error(f"Нужно {team_size} аккаунтов, но доступно {len(self.accounts)}")
            return {"status": "error", "message": "Недостаточно аккаунтов"}

        # Расположение окон
        if team_size == 5:
            positions = [
                (0, 0, 960, 540),
                (960, 0, 960, 540),
                (0, 540, 960, 540),
                (960, 540, 960, 540),
                (1920, 0, 960, 1080)
            ]
        else:
            positions = self.calculate_window_positions(team_size)

        results = []
        for i in range(team_size):
            if i >= len(self.accounts):
                self.logger.warning(f"Недостаточно аккаунтов для бота {i + 1}")
                break

            account = self.accounts[i]
            position = positions[i] if i < len(positions) else (0, 0, 1024, 768)
            sandbox_name = f"DOTA_BOT_{i + 1}"

            # Получаем имя пользователя
            if isinstance(account, dict):
                username = account.get('username', f'bot_{i + 1}')
                password = account.get('password', '')
            else:
                username = str(account)
                password = ''
                account = {'username': username, 'password': password}

            print(f"Запуск бота {i + 1}/{team_size}: {username}")

            try:
                pid = self.controller.launch_steam(
                    sandbox_name,
                    username,
                    password,
                    position
                )

                if pid:
                    results.append({
                        "account": username,
                        "sandbox": sandbox_name,
                        "pid": pid,
                        "success": True
                    })
                    print(f"  ✓ Запущен (PID: {pid})")
                else:
                    results.append({
                        "account": username,
                        "sandbox": sandbox_name,
                        "success": False,
                        "error": "Не удалось запустить процесс"
                    })
                    print(f"  ✗ Ошибка запуска")

            except Exception as e:
                self.logger.error(f"Ошибка запуска бота {i + 1}: {e}")
                results.append({
                    "account": username,
                    "sandbox": sandbox_name,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ✗ Исключение: {e}")

            # Задержка между запусками
            if i < team_size - 1:
                time.sleep(20)  # 20 секунд между запусками

        success_count = sum(1 for r in results if r['success'])

        return {
            "status": "success" if success_count == team_size else "partial",
            "total": team_size,
            "successful": success_count,
            "results": results
        }

    def calculate_window_positions(self, num_windows: int) -> List[tuple]:
        """Расчет позиций окон"""
        import math

        screen_width = 1920
        screen_height = 1080

        # Определяем сетку
        cols = math.ceil(math.sqrt(num_windows))
        rows = math.ceil(num_windows / cols)

        window_width = screen_width // cols
        window_height = screen_height // rows

        positions = []
        for i in range(num_windows):
            row = i // cols
            col = i % cols

            x = col * window_width
            y = row * window_height

            # Отступы
            padding = 5
            positions.append((
                x + padding,
                y + padding,
                window_width - padding * 2,
                window_height - padding * 2
            ))

        return positions

    def get_status(self):
        """Получение статуса"""
        return {
            "accounts_count": len(self.accounts),
            "running_processes": len(self.controller.processes),
            "sandboxie_path": str(self.controller.sandboxie_path)
        }
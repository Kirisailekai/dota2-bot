import time
from typing import Dict, List
import logging
from .sandbox_controller import SandboxController
from config.accounts_manager import AccountsManager


class GameLauncher:
    def __init__(self):
        self.controller = SandboxController()
        self.accounts_manager = AccountsManager()
        self.logger = logging.getLogger(__name__)

        # Проверяем наличие песочниц
        self.check_sandboxes()

    def check_sandboxes(self):
        """Проверка существования песочниц"""
        print("Проверка песочниц...")

        sandboxes_exist = True
        for i in range(1, 6):
            sandbox_name = f"DOTA_BOT_{i}"
            if not self.controller.is_sandbox_exists(sandbox_name):
                sandboxes_exist = False
                self.controller.create_sandbox_through_ui(sandbox_name)
                break

        if sandboxes_exist:
            print("✓ Все песочницы найдены")

    def launch_single(self, account_index: int = 0, window_position: tuple = None) -> bool:
        """Запуск одного экземпляра Dota 2"""
        accounts = self.accounts_manager.get_accounts()

        if account_index >= len(accounts):
            self.logger.error(f"Аккаунт с индексом {account_index} не найден")
            return False

        account = accounts[account_index]
        sandbox_name = account.get('sandbox', f'DOTA_BOT_{account_index + 1}')

        print(f"Запуск Dota 2 для {account['username']} в {sandbox_name}...")

        if window_position is None:
            window_position = (0, 0, 1024, 768)

        pid = self.controller.launch_steam(
            sandbox_name,
            account['username'],
            account['password'],
            window_position
        )

        return pid is not None

    def launch_team(self, team_size: int = 5) -> Dict:
        """Запуск команды ботов"""
        print(f"Запуск команды из {team_size} ботов...")

        accounts = self.accounts_manager.get_accounts()[:team_size]

        if len(accounts) < team_size:
            self.logger.error(f"Нужно {team_size} аккаунтов, но доступно {len(accounts)}")
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
        for i, (account, position) in enumerate(zip(accounts, positions)):
            sandbox_name = f"DOTA_BOT_{i + 1}"

            print(f"Запуск бота {i + 1}/{team_size}: {account['username']}")

            pid = self.controller.launch_steam(
                sandbox_name,
                account['username'],
                account['password'],
                position
            )

            if pid:
                results.append({
                    "account": account['username'],
                    "sandbox": sandbox_name,
                    "pid": pid,
                    "success": True
                })
                print(f"  ✓ Запущен (PID: {pid})")
            else:
                results.append({
                    "account": account['username'],
                    "sandbox": sandbox_name,
                    "success": False
                })
                print(f"  ✗ Ошибка запуска")

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
            "running_processes": len(self.controller.processes),
            "sandboxie_path": str(self.controller.sandboxie_path)
        }
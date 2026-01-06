import subprocess
import os
import psutil
import time
import asyncio
from pathlib import Path
import json
from typing import Dict, List


class SandboxManager:
    def __init__(self, sandboxie_path=None, config_dir="config/sandbox_configs"):
        self.sandboxie_path = sandboxie_path or r"C:\Sandboxie\Start.exe"
        self.config_dir = Path(config_dir)
        self.boxes: List[str] = []
        self.processes: Dict[str, subprocess.Popen] = {}
        self.box_configs: Dict[str, Dict] = {}

        # Создаем директории если их нет
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def check_sandboxie_installed(self) -> bool:
        """Проверка установлен ли Sandboxie"""
        if not os.path.exists(self.sandboxie_path):
            print(f"❌ Sandboxie не найден по пути: {self.sandboxie_path}")
            print("\nУстановите Sandboxie одним из способов:")
            print("1. Запустите scripts\\setup_sandboxie.py (от администратора)")
            print("2. Запустите install_sandboxie.bat (от администратора)")
            print("3. Установите вручную с https://sandboxie-plus.com/")
            return False
        return True

    async def create_sandbox_config(self, box_name: str, config_type: str = "default") -> Path:
        """Создание конфигурационного файла для Sandboxie"""

        # Базовые настройки
        base_config = {
            "box_name": box_name,
            "config_type": config_type,
            "settings": {
                "Enabled": "y",
                "ConfigLevel": "7",
                "AutoRecover": "y",
                "BlockNetworkFiles": "y",
                "DropAdminRights": "y"
            },
            "process_group": [
                "steam.exe",
                "dota2.exe",
                "gameoverlayui.exe"
            ],
            "file_paths": {
                "isolate": [
                    r"C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta",
                    r"C:\Program Files (x86)\Steam\config",
                    r"C:\Program Files (x86)\Steam\userdata"
                ],
                "share": [
                    r"%Personal%",
                    r"%Desktop%"
                ]
            },
            "network": {
                "enabled": "y",
                "block_ports": ["27015", "27016", "27017"]
            }
        }

        # Разные конфиги для разных окон
        if config_type == "low_memory":
            base_config["settings"]["MemoryQuota"] = "1024M"
        elif config_type == "high_perf":
            base_config["settings"]["MemoryQuota"] = "2048M"
            base_config["settings"]["CpuPriority"] = "Idle"

        # Сохраняем JSON конфиг
        json_config_path = self.config_dir / f"{box_name}.json"
        json_config_path.write_text(json.dumps(base_config, indent=2, ensure_ascii=False), encoding='utf-8')

        # Создаем INI файл для Sandboxie
        ini_content = self._config_to_ini(base_config)
        ini_path = Path(f"C:\\Sandboxie\\{box_name}.ini")
        ini_path.write_text(ini_content, encoding='utf-8')

        self.box_configs[box_name] = base_config
        print(f"[Sandbox] Создан конфиг для {box_name} ({config_type})")

        return ini_path

    def _config_to_ini(self, config: Dict) -> str:
        """Конвертация JSON конфига в INI формат"""
        lines = []

        # Настройки
        lines.append(f"[{config['box_name']}]")
        for key, value in config['settings'].items():
            lines.append(f"{key}={value}")
        lines.append("")

        # Process group
        lines.append("[ProcessGroup]")
        lines.append("Enabled=y")
        for process in config['process_group']:
            lines.append(f"ImageName={process}")
        lines.append("")

        # File paths
        lines.append("[FilePaths]")
        for path in config['file_paths']['isolate']:
            lines.append(f"{path}=-")
        for path in config['file_paths']['share']:
            lines.append(f"{path}=%Shared%")
        lines.append("")

        # Network
        lines.append("[Network]")
        for key, value in config['network'].items():
            if isinstance(value, list):
                for item in value:
                    lines.append(f"{key}={item}")
            else:
                lines.append(f"{key}={value}")

        return "\n".join(lines)

    async def launch_box(self, box_name: str, config_type: str = "default",
                         account_id: int = 0) -> subprocess.Popen:
        """Запуск изолированного окружения с указанным аккаунтом"""

        if not self.check_sandboxie_installed():
            raise RuntimeError("Sandboxie не установлен")

        # Создаем конфиг
        await self.create_sandbox_config(box_name, config_type)

        # Параметры запуска
        launch_cmd = [
            self.sandboxie_path,
            f"/box:{box_name}",
            "cmd.exe",
            "/c",
            "start",
            "/B",
            "steam.exe"
        ]

        # Добавляем параметры для Steam аккаунта
        if account_id > 0:
            from config.accounts_manager import AccountsManager
            accounts_mgr = AccountsManager()
            accounts_mgr.load_accounts()

            account = accounts_mgr.get_account(account_id)
            if account:
                launch_cmd.extend(["-login", account.login, account.password])
                print(f"[Sandbox] Использую аккаунт: {account.login}")

        # Запускаем Steam
        print(f"[Sandbox] Запускаю {box_name}...")
        process = subprocess.Popen(
            launch_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        self.processes[box_name] = process
        self.boxes.append(box_name)

        # Ждем запуска
        await asyncio.sleep(5)

        return process

    async def launch_boxes_with_resources(self, count=5):
        """Запуск окон с оптимизацией под ресурсы системы"""
        import psutil

        # Анализируем систему
        cpu_count = psutil.cpu_count()
        total_memory = psutil.virtual_memory().total / (1024 ** 3)  # в GB

        print(f"[System] CPU ядер: {cpu_count}, RAM: {total_memory:.1f}GB")

        # Распределяем ресурсы
        config_types = []
        for i in range(count):
            if total_memory < 16:
                config_types.append("low_memory")
            elif i == 0:  # Первое окно - высокий приоритет
                config_types.append("high_perf")
            else:
                config_types.append("default")

        # Запускаем окна
        tasks = []
        for i in range(count):
            box_name = f"DotaBox{i + 1}"
            config_type = config_types[i]
            account_id = i + 1

            task = asyncio.create_task(
                self.launch_box(box_name, config_type, account_id)
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
        print(f"[Sandbox] Запущено {count} окон с оптимизацией ресурсов")

    async def cleanup(self, force=False):
        """Очистка всех песочниц"""
        print("[Sandbox] Очищаю песочницы...")

        for box in self.boxes:
            try:
                if force:
                    cmd = f'"{self.sandboxie_path}" /box:{box} /terminate'
                else:
                    cmd = f'"{self.sandboxie_path}" /box:{box} /close'

                subprocess.run(cmd, shell=True, timeout=10)
                print(f"[Sandbox] Очищена песочница: {box}")

            except subprocess.TimeoutExpired:
                print(f"[Sandbox] Таймаут при очистке {box}")

        # Убиваем процессы
        for box_name, proc in self.processes.items():
            if proc.poll() is None:
                try:
                    proc.terminate()
                    await asyncio.sleep(2)
                    if proc.poll() is None:
                        proc.kill()
                except:
                    pass

        self.boxes.clear()
        self.processes.clear()
        print("[Sandbox] Все песочницы очищены")
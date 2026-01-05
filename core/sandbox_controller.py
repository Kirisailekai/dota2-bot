import subprocess
import os
import psutil
import time
import asyncio
from pathlib import Path


class SandboxManager:
    def __init__(self, sandboxie_path=None):
        self.sandboxie_path = sandboxie_path or r"C:\Sandboxie\Start.exe"
        self.boxes = []
        self.processes = []

    async def create_sandbox_config(self, box_name):
        """Создание конфигурационного файла для Sandboxie"""
        config_content = f"""[BoxSettings]
Enabled=y
ConfigLevel=7
AutoRecover=y

[ProcessGroup]
Enabled=y
ImageName=steam.exe
ImageName=dota2.exe

[Internet]
Enabled=y

[FilePaths]
# Изолируем доступ к файлам Dota 2
C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta=-
"""

        config_path = Path(f"C:\\Sandboxie\\{box_name}.ini")
        config_path.write_text(config_content, encoding='utf-8')
        return config_path

    async def launch_box(self, box_name):
        """Запуск изолированного окружения"""
        if not os.path.exists(self.sandboxie_path):
            raise FileNotFoundError(f"Sandboxie не найден по пути: {self.sandboxie_path}")

        # Создаем конфиг для песочницы
        await self.create_sandbox_config(box_name)

        # Команда для запуска
        cmd = f'"{self.sandboxie_path}" /box:{box_name} cmd.exe'

        # Запускаем процесс
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        self.processes.append(process)
        self.boxes.append(box_name)

        print(f"Запущена песочница: {box_name}")
        return process

    async def launch_boxes(self, count=5):
        """Запуск нескольких песочниц"""
        tasks = []
        for i in range(1, count + 1):
            box_name = f"DotaBox{i}"
            task = asyncio.create_task(self.launch_box(box_name))
            tasks.append(task)

        await asyncio.gather(*tasks)
        print(f"Запущено {count} песочниц")

    async def cleanup(self):
        """Очистка всех песочниц"""
        for box in self.boxes:
            cmd = f'"{self.sandboxie_path}" /box:{box} /terminate'
            subprocess.run(cmd, shell=True)

        for proc in self.processes:
            if proc.poll() is None:
                proc.terminate()

        print("Все песочницы очищены")
import subprocess
import asyncio
import time
import win32gui
import win32con


class DotaLauncher:
    def __init__(self):
        self.steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
        self.dota_app_id = 570
        self.window_titles = []

    async def launch_dota_in_sandbox(self, box_name, account_index=0):
        """Запуск Dota 2 в указанной песочнице"""
        # Параметры запуска для уменьшения нагрузки
        launch_params = [
            "-applaunch", str(self.dota_app_id),
            "-console",
            "-novid",  # Пропуск интро
            "-nojoy",  # Отключить джойстик
            "-windowed",
            "-noborder",  # Без рамки
            "-w", "1024",  # Ширина
            "-h", "768",  # Высота
            "+fps_max", "60",
            "-high",  # Высокий приоритет
        ]

        # Если есть отдельный аккаунт Steam
        if account_index > 0:
            launch_params.extend(["-login", f"account{account_index}"])

        cmd = [
                  r"C:\Sandboxie\Start.exe",
                  f"/box:{box_name}",
                  self.steam_path
              ] + launch_params

        # Запускаем процесс
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        print(f"Запускаю Dota 2 в {box_name}")
        return process

    async def wait_for_window(self, box_name, timeout=60):
        """Ожидание появления окна игры"""
        start_time = time.time()
        window_handle = None

        while time.time() - start_time < timeout:
            def enum_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Dota 2" in title and box_name in title:
                        results.append(hwnd)

            results = []
            win32gui.EnumWindows(enum_callback, results)

            if results:
                window_handle = results[0]
                # Приводим окно к нужному размеру и позиции
                win32gui.MoveWindow(window_handle, 0, 0, 1024, 768, True)
                win32gui.ShowWindow(window_handle, win32con.SW_SHOWNORMAL)
                break

            await asyncio.sleep(1)

        return window_handle

    async def launch_dota_in_boxes(self, count=5):
        """Запуск Dota 2 во всех песочницах"""
        tasks = []
        for i in range(1, count + 1):
            box_name = f"DotaBox{i}"
            # Запускаем игру
            task1 = asyncio.create_task(
                self.launch_dota_in_sandbox(box_name, i)
            )
            # Ждем окно
            task2 = asyncio.create_task(
                self.wait_for_window(box_name)
            )
            tasks.extend([task1, task2])

        results = await asyncio.gather(*tasks)
        print("Все окна Dota 2 запущены")
        return results
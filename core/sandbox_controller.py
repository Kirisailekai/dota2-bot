import subprocess
import psutil
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import logging

import win32con
import win32gui


class SandboxController:
    def __init__(self):
        self.sandboxie_path = Path(r"C:\Program Files\Sandboxie-Plus")
        self.processes = []
        self.logger = self.setup_logger()

        if not self.sandboxie_path.exists():
            self.logger.error("Sandboxie-Plus не найден!")

    def setup_logger(self):
        logger = logging.getLogger("SandboxController")
        logger.setLevel(logging.INFO)

        # Создаем папку для логов если ее нет
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        handler = logging.FileHandler(log_dir / "sandbox_controller.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Также выводим в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def start_process(self, sandbox_name: str, command: str) -> Optional[int]:
        """Запуск процесса в песочнице"""
        try:
            start_exe = self.sandboxie_path / "Start.exe"
            if not start_exe.exists():
                self.logger.error("Start.exe не найден!")
                return None

            # Формируем команду
            full_cmd = f'"{start_exe}" /box:{sandbox_name} {command}'
            self.logger.info(f"Выполняю команду: {full_cmd}")

            # Запускаем процесс
            process = subprocess.Popen(
                full_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Ждем немного чтобы процесс запустился
            time.sleep(3)

            # Получаем PID (не всегда точно, но работает для отслеживания)
            pid = process.pid

            self.processes.append({
                'sandbox': sandbox_name,
                'command': command,
                'process': process,
                'pid': pid,
                'start_time': time.time()
            })

            self.logger.info(f"Процесс запущен в песочнице {sandbox_name} (PID: {pid})")
            return pid

        except Exception as e:
            self.logger.error(f"Ошибка запуска процесса: {e}")
            return None

    def wait_for_dota_window(self, timeout=30):
        """Ждёт появления окна Dota 2 и возвращает hwnd"""
        end_time = time.time() + timeout

        while time.time() < end_time:
            hwnds = []

            def enum_handler(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Dota 2" in title:
                        hwnds.append(hwnd)

            win32gui.EnumWindows(enum_handler, None)

            if hwnds:
                return hwnds[0]

            time.sleep(0.5)

        return None

    def apply_window_position(self, hwnd, x, y, width, height):
        """Применяет позицию, размер и РЕАЛЬНУЮ рамку Windows"""
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.WS_CAPTION | win32con.WS_THICKFRAME

        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        win32gui.SetWindowPos(
            hwnd,
            None,
            x, y, width, height,
            win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED
        )

    def launch_steam(self, sandbox_name: str, username: str, password: str,
                     window_position: tuple = None) -> Optional[int]:
        """Запуск Steam в песочнице"""
        steam_path = r"C:\Program Files (x86)\Steam\steam.exe"

        if not Path(steam_path).exists():
            self.logger.error("Steam не найден!")
            return None

        # Параметры запуска Dota 2
        dota_args = [
            f"-login {username} {password}",
            "-applaunch 570",  # Dota 2
            "-novid",
            "-console",
            "-windowed",
            "-w 640", # ширина под сетку 3 окна
            "-h 540", # высота под половину экрана
            "-disablehangwatchdog"
        ]

        if window_position:
            x, y, width, height = window_position
            dota_args.extend([
                f"-x {x}",
                f"-y {y}",
                f"-w {width}",
                f"-h {height}"
            ])

        command = f'"{steam_path}" {" ".join(dota_args)}'
        pid = self.start_process(sandbox_name, command)

        if pid and window_position:
            hwnd = self.wait_for_dota_window()
            if hwnd:
                x, y, w, h = window_position
                self.apply_window_position(hwnd, x, y, w, h)
            else:
                self.logger.warning("Окно Dota 2 не найдено для позиционирования")

        return pid

    def launch_dota_direct(self, sandbox_name: str, username: str, password: str) -> Optional[int]:
        """Прямой запуск Dota 2 (альтернативный метод)"""
        # Если Steam уже запущен, можно использовать этот метод
        command = (
            f'cmd /c start /wait "" "{self.sandboxie_path}\\Start.exe" '
            f'/box:{sandbox_name} '
            '"C:\\Program Files (x86)\\Steam\\steam.exe" '
            f'-login {username} {password} -applaunch 570 -windowed -novid'
        )

        return self.start_process(sandbox_name, command)

    def kill_all_in_sandbox(self, sandbox_name: str):
        """Завершение всех процессов в песочнице"""
        try:
            # Используем taskkill для завершения процессов
            cmd = f'taskkill /FI "WINDOWTITLE eq *{sandbox_name}*" /F'
            subprocess.run(cmd, shell=True, capture_output=True)

            # Также завершаем процессы через Sandboxie
            start_exe = self.sandboxie_path / "Start.exe"
            if start_exe.exists():
                cmd = f'"{start_exe}" /box:{sandbox_name} /terminate'
                subprocess.run(cmd, shell=True, capture_output=True)

            self.logger.info(f"Процессы в песочнице {sandbox_name} завершены")

        except Exception as e:
            self.logger.error(f"Ошибка завершения процессов: {e}")

    def kill_all(self):
        """Остановка всех процессов"""
        self.logger.info("Остановка всех процессов...")

        for proc_info in self.processes:
            try:
                if 'process' in proc_info and proc_info['process']:
                    proc_info['process'].terminate()

                # Также завершаем по PID
                pid = proc_info.get('pid')
                if pid:
                    try:
                        os.kill(pid, 9)
                    except:
                        pass

            except Exception as e:
                self.logger.error(f"Ошибка остановки процесса: {e}")

        # Завершаем все песочницы
        for i in range(1, 6):
            self.kill_all_in_sandbox(f"DOTA_BOT_{i}")

        self.processes.clear()
        self.logger.info("Все процессы остановлены")

    def monitor_processes(self, interval: int = 30):
        """Мониторинг процессов (упрощенный)"""
        self.logger.info(f"Запуск мониторинга с интервалом {interval} секунд...")

        try:
            while True:
                # Проверяем статус каждого процесса
                for proc_info in self.processes[:]:
                    pid = proc_info.get('pid')
                    sandbox = proc_info.get('sandbox', 'unknown')

                    if pid:
                        try:
                            process = psutil.Process(pid)
                            status = process.status()
                            self.logger.debug(f"Процесс {pid} ({sandbox}): {status}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            self.logger.warning(f"Процесс {pid} ({sandbox}) завершен")
                            self.processes.remove(proc_info)

                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("Мониторинг остановлен пользователем")
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга: {e}")

    def is_sandbox_exists(self, sandbox_name: str) -> bool:
        """Проверка существования песочницы"""
        config_paths = [
            self.sandboxie_path / f"{sandbox_name}.ini",
            Path.home() / "AppData" / "Roaming" / "Sandboxie-Plus" / f"{sandbox_name}.ini"
        ]

        for path in config_paths:
            if path.exists():
                return True

        self.logger.warning(f"Песочница {sandbox_name} не найдена. Создайте ее через Sandboxie-Plus UI.")
        return False

    def create_sandbox_through_ui(self, sandbox_name: str):
        """Создание песочницы через UI (инструкция)"""
        print(f"\n📋 Создайте песочницу {sandbox_name} через Sandboxie-Plus UI:")
        print("1. Откройте Sandboxie-Plus.exe")
        print("2. Нажмите правой кнопкой в списке песочниц → 'Create New Sandbox'")
        print("3. Введите имя: " + sandbox_name)
        print("4. Нажмите OK")
        print("5. Настройте по желанию (границы, изоляция и т.д.)")
        print("\nПосле создания песочницы можно запускать ботов.\n")

        input("Нажмите Enter после создания песочницы...")
import psutil
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import win32process
import win32gui
import win32con
import win32api


@dataclass
class ProcessInfo:
    box_name: str
    pid: int
    window_handle: Optional[int]
    start_time: float
    status: str  # 'running', 'stopped', 'hung'
    restart_count: int = 0


class ProcessMonitor:
    def __init__(self, sandbox_manager):
        self.sandbox_manager = sandbox_manager
        self.processes: Dict[str, ProcessInfo] = {}
        self.monitoring = False
        self.max_restarts = 3

    async def add_process(self, box_name: str, process: psutil.Process, window_handle: int = None):
        """Добавление процесса для мониторинга"""
        proc_info = ProcessInfo(
            box_name=box_name,
            pid=process.pid,
            window_handle=window_handle,
            start_time=time.time(),
            status='running'
        )
        self.processes[box_name] = proc_info
        print(f"[Monitor] Добавлен процесс для {box_name} (PID: {process.pid})")

    async def is_process_alive(self, process_info: ProcessInfo) -> bool:
        """Проверка жив ли процесс"""
        try:
            proc = psutil.Process(process_info.pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    async def is_window_responding(self, hwnd: int) -> bool:
        """Проверка отвечает ли окно"""
        if not hwnd:
            return False

        try:
            # Пробуем послать сообщение WM_NULL (0x0000)
            result = win32gui.SendMessageTimeout(
                hwnd,
                win32con.WM_NULL,
                0, 0,
                win32con.SMTO_ABORTIFHUNG,
                1000  # таймаут 1 секунда
            )
            return result is not None
        except:
            return False

    async def check_process(self, box_name: str) -> str:
        """Проверка состояния конкретного процесса"""
        if box_name not in self.processes:
            return "not_found"

        proc_info = self.processes[box_name]

        # Проверяем жив ли процесс
        if not await self.is_process_alive(proc_info):
            proc_info.status = 'stopped'
            return 'stopped'

        # Проверяем отвечает ли окно
        if proc_info.window_handle:
            if not await self.is_window_responding(proc_info.window_handle):
                proc_info.status = 'hung'
                return 'hung'

        proc_info.status = 'running'
        return 'running'

    async def restart_process(self, box_name: str):
        """Перезапуск процесса"""
        if box_name not in self.processes:
            return False

        proc_info = self.processes[box_name]

        if proc_info.restart_count >= self.max_restarts:
            print(f"[Monitor] Достигнут лимит перезапусков для {box_name}")
            return False

        print(f"[Monitor] Перезапускаю {box_name}...")

        # Убиваем старый процесс если он еще жив
        try:
            proc = psutil.Process(proc_info.pid)
            proc.terminate()
            await asyncio.sleep(2)
            if proc.is_running():
                proc.kill()
        except:
            pass

        # Перезапускаем через sandbox_manager
        try:
            from core.game_launcher import DotaLauncher
            launcher = DotaLauncher()

            # Запускаем новое окно
            new_process = await launcher.launch_dota_in_sandbox(
                box_name,
                account_index=int(box_name[-1])  # извлекаем номер из имени
            )

            # Ждем окно
            await asyncio.sleep(10)
            new_window = await launcher.wait_for_window(box_name, timeout=30)

            # Обновляем информацию
            proc_info.pid = new_process.pid
            proc_info.window_handle = new_window
            proc_info.start_time = time.time()
            proc_info.status = 'running'
            proc_info.restart_count += 1

            print(f"[Monitor] {box_name} перезапущен (PID: {new_process.pid})")
            return True

        except Exception as e:
            print(f"[Monitor] Ошибка при перезапуске {box_name}: {e}")
            return False

    async def monitor_loop(self, interval: float = 10.0):
        """Основной цикл мониторинга"""
        self.monitoring = True

        while self.monitoring:
            try:
                for box_name in list(self.processes.keys()):
                    status = await self.check_process(box_name)

                    if status in ['stopped', 'hung']:
                        print(f"[Monitor] {box_name} в состоянии {status}")

                        if status == 'hung':
                            # Пытаемся восстановить окно
                            try:
                                if self.processes[box_name].window_handle:
                                    win32gui.ShowWindow(
                                        self.processes[box_name].window_handle,
                                        win32con.SW_RESTORE
                                    )
                                    win32gui.SetForegroundWindow(
                                        self.processes[box_name].window_handle
                                    )
                                    print(f"[Monitor] Попытка восстановить окно {box_name}")
                            except:
                                pass

                        # Перезапускаем если нужно
                        await self.restart_process(box_name)

                await asyncio.sleep(interval)

            except Exception as e:
                print(f"[Monitor] Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(interval)

    async def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring = False

    async def get_stats(self) -> Dict:
        """Статистика по процессам"""
        stats = {
            'total': len(self.processes),
            'running': 0,
            'stopped': 0,
            'hung': 0,
            'restarts': {}
        }

        for box_name, proc_info in self.processes.items():
            stats[proc_info.status] += 1
            stats['restarts'][box_name] = proc_info.restart_count

        return stats
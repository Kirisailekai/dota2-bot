# core/process_monitor.py
"""
Мониторинг процессов ботов
"""

import psutil
import time
import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime


class ProcessMonitor:
    """Мониторинг состояния процессов ботов"""

    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.bot_processes = {}
        self.logger = logging.getLogger(__name__)

        # Настройки мониторинга
        self.check_interval = 30  # секунды
        self.max_restart_attempts = 3

    def start_monitoring(self):
        """Запуск мониторинга"""
        if self.monitoring:
            self.logger.warning("Мониторинг уже запущен")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.logger.info("Мониторинг процессов запущен")

    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info("Мониторинг процессов остановлен")

    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                self.check_all_processes()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")

    def check_all_processes(self) -> bool:
        """Проверка всех процессов ботов"""
        try:
            # Ищем процессы Dota 2
            dota_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'dota2.exe' in proc.info['name'].lower():
                        dota_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self.logger.info(f"Найдено процессов Dota 2: {len(dota_processes)}")

            # Обновляем информацию о процессах
            for i, proc in enumerate(dota_processes[:5]):  # Максимум 5 ботов
                bot_id = i
                self.bot_processes[bot_id] = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': 'running',
                    'cpu_percent': proc.cpu_percent(),
                    'memory_mb': proc.memory_info().rss / 1024 / 1024,
                    'last_check': datetime.now()
                }

            return len(dota_processes) > 0

        except Exception as e:
            self.logger.error(f"Ошибка проверки процессов: {e}")
            return False

    def get_process_info(self, bot_id: int) -> Optional[Dict]:
        """Получение информации о процессе бота"""
        return self.bot_processes.get(bot_id)

    def get_all_processes_info(self) -> Dict[int, Dict]:
        """Получение информации о всех процессах"""
        return self.bot_processes.copy()

    def log_system_stats(self):
        """Логирование системной статистики"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            stats = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / 1024 ** 3,
                'disk_free_gb': disk.free / 1024 ** 3,
                'active_bots': len(self.bot_processes)
            }

            self.logger.info(f"Системная статистика: {stats}")
            return stats

        except Exception as e:
            self.logger.error(f"Ошибка сбора статистики: {e}")
            return None
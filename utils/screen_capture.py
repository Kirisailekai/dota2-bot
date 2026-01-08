# utils/screen_capture.py
"""
Захват экрана окон ботов
"""

import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
from typing import Optional, Tuple
import logging
import time


class ScreenCapture:
    """Захват экрана окон"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_timeout = 2.0  # секунды

    def capture_window(self, hwnd: int) -> Optional[np.ndarray]:
        """Захват окна по его handle"""
        try:
            # Получаем размеры окна
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # Проверяем кэш
            cache_key = f"{hwnd}_{width}_{height}"
            if cache_key in self.cache:
                cached_time, cached_img = self.cache[cache_key]
                if time.time() - cached_time < self.cache_timeout:
                    return cached_img.copy()

            # Создаем контекст устройства
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # Создаем битмап
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)

            # Копируем содержимое окна
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

            # Конвертируем в numpy массив
            bmp_info = bitmap.GetInfo()
            bmp_str = bitmap.GetBitmapBits(True)

            img = np.frombuffer(bmp_str, dtype='uint8')
            img.shape = (height, width, 4)

            # Конвертируем BGR в RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

            # Очистка
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            # Обновляем кэш
            self.cache[cache_key] = (time.time(), img.copy())

            return img

        except Exception as e:
            self.logger.error(f"Ошибка захвата окна: {e}")
            return None

    def find_and_capture_dota_window(self, bot_id: int) -> Optional[np.ndarray]:
        """Поиск и захват окна Dota 2 для бота"""
        # Пробуем разные варианты заголовков
        search_patterns = [
            f"Dota 2",
            f"dota2",
            f"Sandboxie",
            f"Steam"
        ]

        for pattern in search_patterns:
            hwnd = self.find_dota_window_by_pattern(pattern, bot_id)
            if hwnd:
                screenshot = self.capture_window(hwnd)
                if screenshot is not None:
                    return screenshot

        return None

    def find_dota_window_by_pattern(self, pattern: str, bot_id: int) -> Optional[int]:
        """Поиск окна Dota 2 по паттерну"""

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if pattern.lower() in window_title.lower():
                    # Проверяем, что окно подходящего размера
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width = right - left
                    height = bottom - top

                    if width > 800 and height > 600:  # Минимальные размеры
                        windows.append((hwnd, window_title))
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        if windows:
            # Возвращаем первое подходящее окно или по bot_id
            if bot_id < len(windows):
                return windows[bot_id][0]
            return windows[0][0]

        return None

    def save_screenshot(self, image: np.ndarray, bot_id: int, prefix: str = ""):
        """Сохранение скриншота"""
        try:
            from datetime import datetime
            import os

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshots/bot_{bot_id}/{prefix}_{timestamp}.png"

            # Создаем директорию
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Сохраняем изображение
            cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

            return filename

        except Exception as e:
            self.logger.error(f"Ошибка сохранения скриншота: {e}")
            return None
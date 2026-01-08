# utils/input_simulator.py (расширенная версия)
"""
Симуляция ввода для ботов
"""

import win32api
import win32con
import win32gui
import time
import random
from typing import Tuple, Optional
import logging


class InputSimulator:
    """Симулятор ввода для окон в Sandboxie"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.key_delay = 0.05  # Задержка между нажатиями
        self.mouse_delay = 0.1  # Задержка между движениями мыши

    def find_window_by_title(self, title_substring: str) -> Optional[int]:
        """Поиск окна по части заголовка"""

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title_substring.lower() in window_title.lower():
                    windows.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)

        return windows[0] if windows else None

    def activate_window(self, hwnd: int) -> bool:
        """Активация окна"""
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка активации окна: {e}")
            return False

    def send_key(self, hwnd: int, key_code: int, key_down: bool = True,
                 modifiers: list = None) -> bool:
        """Отправка нажатия клавиши"""
        try:
            if modifiers:
                for mod_key in modifiers:
                    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, mod_key, 0)
                    time.sleep(self.key_delay)

            if key_down:
                win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key_code, 0)
                time.sleep(self.key_delay)
                win32api.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)
            else:
                win32api.PostMessage(hwnd, win32con.WM_KEYUP, key_code, 0)

            if modifiers:
                for mod_key in reversed(modifiers):
                    win32api.PostMessage(hwnd, win32con.WM_KEYUP, mod_key, 0)
                    time.sleep(self.key_delay)

            return True

        except Exception as e:
            self.logger.error(f"Ошибка отправки клавиши: {e}")
            return False

    def mouse_click(self, hwnd: int, x: int, y: int,
                    button: str = 'left', double_click: bool = False) -> bool:
        """Клик мыши"""
        try:
            # Конвертируем координаты в lParam
            lparam = win32api.MAKELONG(x, y)

            if button == 'left':
                down_msg = win32con.WM_LBUTTONDOWN
                up_msg = win32con.WM_LBUTTONUP
            elif button == 'right':
                down_msg = win32con.WM_RBUTTONDOWN
                up_msg = win32con.WM_RBUTTONUP
            else:
                down_msg = win32con.WM_MBUTTONDOWN
                up_msg = win32con.WM_MBUTTONUP

            # Отправляем сообщения
            win32api.PostMessage(hwnd, down_msg, 0, lparam)
            time.sleep(0.05)
            win32api.PostMessage(hwnd, up_msg, 0, lparam)

            if double_click:
                time.sleep(0.1)
                win32api.PostMessage(hwnd, down_msg, 0, lparam)
                time.sleep(0.05)
                win32api.PostMessage(hwnd, up_msg, 0, lparam)

            return True

        except Exception as e:
            self.logger.error(f"Ошибка клика мыши: {e}")
            return False

    def mouse_move(self, hwnd: int, x: int, y: int) -> bool:
        """Перемещение мыши"""
        try:
            lparam = win32api.MAKELONG(x, y)
            win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка перемещения мыши: {e}")
            return False

    def send_hotkey(self, hwnd: int, main_key: int,
                    modifier_keys: list = None) -> bool:
        """Отправка хоткея"""
        if not modifier_keys:
            modifier_keys = []

        # Нажимаем модификаторы
        for mod_key in modifier_keys:
            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, mod_key, 0)
            time.sleep(self.key_delay)

        # Нажимаем основную клавишу
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, main_key, 0)
        time.sleep(self.key_delay)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, main_key, 0)

        # Отпускаем модификаторы
        for mod_key in reversed(modifier_keys):
            win32api.PostMessage(hwnd, win32con.WM_KEYUP, mod_key, 0)
            time.sleep(self.key_delay)

        return True

    def type_text(self, hwnd: int, text: str) -> bool:
        """Ввод текста"""
        try:
            for char in text:
                # Конвертируем символ в виртуальный код
                vk_code = win32api.VkKeyScan(char)

                if vk_code != -1:
                    win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
                    time.sleep(0.01)

            return True

        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return False
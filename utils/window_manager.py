import win32gui
import win32con
import win32api
import json
import time
import os
from typing import List, Tuple, Optional


class WindowManager:
    def __init__(self, config_path: str = "config/window_layout.json"):
        self.window_handles = []
        self.config_path = config_path
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)

    def find_dota_windows(self) -> List[int]:
        """Находит все окна Dota 2"""
        windows = []

        def callback(hwnd, _):
            window_title = win32gui.GetWindowText(hwnd)
            if "dota" in window_title.lower() or "dota 2" in window_title.lower():
                if win32gui.IsWindowVisible(hwnd):
                    windows.append(hwnd)
            return True

        win32gui.EnumWindows(callback, None)
        return windows

    def arrange_windows_grid(self, layout: str = "2x3") -> List[int]:
        """Располагает окна в сетке"""
        windows = self.find_dota_windows()

        if layout == "2x3":
            return self._arrange_2x3_grid(windows)

        return windows

    def _arrange_2x3_grid(self, windows: List[int]) -> List[int]:
        """Сетка 2 строки, 3 столбца"""
        if len(windows) == 0:
            return []

        cols = 3
        rows = 2
        window_width = self.screen_width // cols
        window_height = self.screen_height // rows

        positions = [
            (0, 0), (window_width, 0), (window_width * 2, 0),
            (window_width // 2, window_height),
            (window_width // 2 + window_width, window_height)
        ]

        for i, hwnd in enumerate(windows[:5]):
            if i < len(positions):
                x, y = positions[i]
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOP,
                    x, y,
                    window_width, window_height,
                    win32con.SWP_SHOWWINDOW
                )
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        return windows[:5]

    def set_window_titles(self, titles: List[str]):
        """Устанавливает заголовки окон"""
        windows = self.find_dota_windows()
        for i, hwnd in enumerate(windows[:5]):
            if i < len(titles):
                try:
                    current_title = win32gui.GetWindowText(hwnd)
                    new_title = f"{current_title} - {titles[i]}"
                    win32gui.SetWindowText(hwnd, new_title)
                except:
                    pass

    def bring_to_front(self):
        """Выводит все окна на передний план"""
        for hwnd in self.window_handles:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)

    def restore_all(self):
        """Восстанавливает все окна"""
        windows = self.find_dota_windows()
        for hwnd in windows:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    def minimize_all(self):
        """Сворачивает все окна"""
        windows = self.find_dota_windows()
        for hwnd in windows:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
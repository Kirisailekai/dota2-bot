# core/window_click.py
from typing import Tuple
import win32gui
import win32con

from core.input_win import mouse_click_abs

Rect = Tuple[int, int, int, int]  # x, y, w, h (в координатах КАДРА, который ты захватываешь)

def _client_origin_screen(hwnd: int) -> Tuple[int, int]:
    # (0,0) client-area -> screen coords
    return win32gui.ClientToScreen(hwnd, (0, 0))

def click_rect_center(hwnd: int, rect_xywh: Rect) -> None:
    x, y, w, h = rect_xywh
    cx = x + w // 2
    cy = y + h // 2

    ox, oy = _client_origin_screen(hwnd)
    mouse_click_abs(ox + cx, oy + cy)

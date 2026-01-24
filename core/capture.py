import numpy as np
import cv2
from mss import mss
from typing import Tuple
import win32gui

_sct = mss()

def grab_rect(rect: Tuple[int, int, int, int]) -> np.ndarray:
    l, t, r, b = rect
    w = max(1, r - l)
    h = max(1, b - t)
    img = np.array(_sct.grab({"left": l, "top": t, "width": w, "height": h}))
    # mss -> BGRA
    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return frame

def crop(frame: np.ndarray, roi: Tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = roi
    return frame[y:y+h, x:x+w]

def get_client_rect_screen(hwnd: int):
    (l, t) = win32gui.ClientToScreen(hwnd, (0, 0))
    (r, b) = win32gui.ClientToScreen(hwnd, win32gui.GetClientRect(hwnd)[2:])
    return (l, t, r, b)

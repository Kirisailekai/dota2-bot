# core/window_manager.py
import win32gui
import win32con
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class WinInfo:
    hwnd: int
    title: str
    rect: Tuple[int, int, int, int]  # (l, t, r, b)


def list_windows(title_contains: str) -> List[WinInfo]:
    res: List[WinInfo] = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if title and title_contains.lower() in title.lower():
            rect = win32gui.GetWindowRect(hwnd)
            res.append(WinInfo(hwnd=hwnd, title=title, rect=rect))

    win32gui.EnumWindows(enum_handler, None)
    # стабильный порядок: сверху-вниз, слева-направо
    res.sort(key=lambda w: (w.rect[1], w.rect[0], w.title))
    return res


def activate_window(hwnd: int) -> None:
    """
    Разворачиваем и пытаемся вывести на передний план.
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass


def set_window_pos(hwnd: int, x: int, y: int, w: Optional[int] = None, h: Optional[int] = None) -> None:
    """
    Более стабильная альтернатива MoveWindow.
    Если w/h не заданы — меняем только позицию.
    """
    flags = win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW
    if w is None or h is None:
        flags |= win32con.SWP_NOSIZE
        w = 0
        h = 0

    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, w, h, flags)


def move_only(hwnd: int, x: int, y: int) -> None:
    """
    ДВИГАЕМ окно без изменения размера (рекомендую для Dota, чтобы не съезжала мышь/hover).
    """
    set_window_pos(hwnd, x, y, None, None)


def move_resize(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    """
    Если всё же ресайзить — делай это ТОЛЬКО в те же размеры, что заданы -w/-h при запуске Dota.
    """
    set_window_pos(hwnd, x, y, w, h)


def compute_grid_cells(screen_w: int, screen_h: int, cols: int, rows: int, padding: int):
    """
    Старый вариант: авто-ячейки по экрану с padding.
    Оставлен, но для Dota лучше fixed, чтобы размеры были ровными (например 640x540).
    """
    cell_w = (screen_w - padding * (cols + 1)) // cols
    cell_h = (screen_h - padding * (rows + 1)) // rows

    cells = []
    idx = 0
    for r in range(rows):
        for c in range(cols):
            x = padding + c * (cell_w + padding)
            y = padding + r * (cell_h + padding)
            cells.append((idx, x, y, cell_w, cell_h))
            idx += 1
    return cells


def compute_grid_cells_fixed(cols: int, rows: int, cell_w: int, cell_h: int, padding: int = 0):
    """
    Новый рекомендуемый вариант: фиксированные размеры ячеек.
    Для 1920x1080 идеально: cols=3 rows=2 cell_w=640 cell_h=540 padding=0
    """
    cells = []
    idx = 0
    for r in range(rows):
        for c in range(cols):
            x = padding + c * (cell_w + padding)
            y = padding + r * (cell_h + padding)
            cells.append((idx, x, y, cell_w, cell_h))
            idx += 1
    return cells

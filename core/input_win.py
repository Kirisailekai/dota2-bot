import ctypes
import time
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

KEYEVENTF_KEYUP = 0x0002

MOUSEEVENTF_VIRTUALDESK = 0x4000
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

# --- FIX ULONG_PTR ---
if hasattr(wintypes, "ULONG_PTR"):
    ULONG_PTR = wintypes.ULONG_PTR
else:
    ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

    _anonymous_ = ("_input",)
    _fields_ = [("type", wintypes.DWORD), ("_input", _INPUT)]


def _send_input(inp: INPUT):
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def _to_absolute_virtual(x, y):
    vx = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    vy = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    vw = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    vh = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

    # нормируем в [0..65535] по виртуальному экрану
    ax = int((x - vx) * 65535 / max(1, vw - 1))
    ay = int((y - vy) * 65535 / max(1, vh - 1))
    return ax, ay


def mouse_move_abs(x, y):
    ax, ay = _to_absolute_virtual(x, y)
    inp = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(ax, ay, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, 0, 0),
    )
    _send_input(inp)


def mouse_click_abs(x, y, delay=0.03):
    mouse_move_abs(x, y)
    time.sleep(0.01)

    down = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, 0),
    )
    up = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, 0),
    )

    _send_input(down)
    time.sleep(delay)
    _send_input(up)

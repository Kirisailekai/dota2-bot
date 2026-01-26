import os
import time
import subprocess
from typing import List, Tuple, Set, Optional
import json
import socket
import threading

import win32con
import win32gui
import win32process
import win32api

REMOTE_IP = "176.123.242.7"
REMOTE_PORT = 50505
REMOTE_TOKEN = "qwertyuiopasdfghjklzxcvbnm"

SANDBOXIE_START = r"C:\Program Files\Sandboxie-Plus\Start.exe"
STEAM_PATH = r"C:\Program Files (x86)\Steam\Steam.exe"

APP_ID = "570"
BOXES = [f"Box{i}" for i in range(1, 6)]

TARGET_EXE_BASENAME = "dota2.exe"

DELAY_BETWEEN_LAUNCHES_SEC = 6
STABLE_TIMEOUT_SEC = 240
STABLE_FOR_SEC = 3

POSITIONS: List[Tuple[int, int, int, int]] = [
    (0, 0, 640, 540),
    (640, 0, 640, 540),
    (1280, 0, 640, 540),
    (0, 540, 960, 540),
    (960, 540, 960, 540),
]


def signal_remote_launch():
    def _send():
        try:
            msg = {"token": REMOTE_TOKEN, "cmd": "launch_5"}
            data = json.dumps(msg).encode("utf-8")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                s.connect((REMOTE_IP, REMOTE_PORT))
                s.sendall(data)
                resp = s.recv(65535)
            print("Remote:", resp.decode("utf-8", errors="replace"))
        except Exception as e:
            print(f"Remote launch failed: {e}")

    threading.Thread(target=_send, daemon=True).start()


def launch_dota_in_box(box_name: str) -> None:
    cmd = [
        SANDBOXIE_START,
        f"/box:{box_name}",
        STEAM_PATH,
        "-applaunch",
        APP_ID,
        "-windowed",
        "-noborder",
        "-novid",
    ]
    print(f"Launch: {box_name}")
    subprocess.Popen(cmd)


def get_process_exe_basename(hwnd: int) -> Optional[str]:
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return None

        access = win32con.PROCESS_QUERY_LIMITED_INFORMATION
        try:
            hproc = win32api.OpenProcess(access, False, pid)
        except Exception:
            access = win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ
            hproc = win32api.OpenProcess(access, False, pid)

        try:
            exe_path = win32process.GetModuleFileNameEx(hproc, 0)
        finally:
            win32api.CloseHandle(hproc)

        if not exe_path:
            return None

        return os.path.basename(exe_path).lower()

    except Exception:
        return None


def _is_candidate_window(hwnd: int) -> bool:
    if not win32gui.IsWindowVisible(hwnd):
        return False
    if win32gui.GetParent(hwnd) != 0:
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    if w < 300 or h < 200:
        return False

    exe = get_process_exe_basename(hwnd)
    if exe != TARGET_EXE_BASENAME:
        return False

    return True


def list_game_windows() -> List[int]:
    hwnds: List[int] = []

    def enum_cb(hwnd, _):
        if _is_candidate_window(hwnd):
            hwnds.append(hwnd)

    win32gui.EnumWindows(enum_cb, None)
    return hwnds


def wait_for_stable_windows(count: int, timeout_sec: int, stable_for_sec: int) -> List[int]:

    start = time.time()
    last_set: Set[int] = set()
    stable_since = None

    while time.time() - start < timeout_sec:
        current = set(list_game_windows())

        if len(current) >= count:
            if current == last_set:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since >= stable_for_sec:
                    return list(current)[:count]
            else:
                last_set = current
                stable_since = None
        else:
            last_set = current
            stable_since = None

        time.sleep(1)

    return list(last_set)[:count]


def move_window(hwnd: int, x: int, y: int, w: int, h: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(
        hwnd,
        None,
        x, y, w, h,
        win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW
    )


def arrange_windows() -> None:
    hwnds = wait_for_stable_windows(
        count=5,
        timeout_sec=STABLE_TIMEOUT_SEC,
        stable_for_sec=STABLE_FOR_SEC
    )

    if not hwnds:
        return

    for i, hwnd in enumerate(hwnds[:5]):
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)

    for i, hwnd in enumerate(hwnds[:5]):
        x, y, w, h = POSITIONS[i]
        move_window(hwnd, x, y, w, h)



def main():
    signal_remote_launch()
    if not os.path.exists(SANDBOXIE_START):
        print(f"Не найден Sandboxie Start.exe: {SANDBOXIE_START}")
        return
    if not os.path.exists(STEAM_PATH):
        print(f"Не найден Steam.exe: {STEAM_PATH}")
        return

    for box in BOXES:
        launch_dota_in_box(box)
        time.sleep(DELAY_BETWEEN_LAUNCHES_SEC)

    arrange_windows()


if __name__ == "__main__":
    main()

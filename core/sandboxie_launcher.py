# core/sandboxie_launcher.py
import subprocess
import time
from typing import List

SANDBOXIE_START = r"C:\Program Files\Sandboxie-Plus\Start.exe"
STEAM_EXE = r"C:\Program Files (x86)\Steam\steam.exe"

DOTA_ARGS = [
    "-applaunch", "570",
    "-novid",
    "-windowed",
    "-noborder",
    "-w", "640",
    "-h", "540",
    "-high",
]

def launch_box(box_name: str):
    cmd = [SANDBOXIE_START, f"/box:{box_name}", STEAM_EXE, *DOTA_ARGS]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def launch_multiple(boxes: List[str], delay_sec: float = 3.0):
    for box in boxes:
        launch_box(box)
        time.sleep(delay_sec)

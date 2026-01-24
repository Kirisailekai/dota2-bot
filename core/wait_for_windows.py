import time
from core.window_manager import list_windows

def wait_for_dota_windows(expected: int, timeout_sec: int = 120):
    start = time.time()
    while time.time() - start < timeout_sec:
        wins = list_windows("Dota 2")
        if len(wins) >= expected:
            print(f"[OK] Found {len(wins)} Dota windows")
            return wins
        time.sleep(2)
    raise TimeoutError("Dota windows did not appear in time")

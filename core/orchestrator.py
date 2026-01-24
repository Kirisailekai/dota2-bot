# core/orchestrator.py
import time
import json
from typing import List

from core.window_manager import (
    list_windows,
    move_only,
    compute_grid_cells_fixed,
)
from core.bot_worker import Bot
from core.sandboxie_launcher import launch_multiple
from core.wait_for_windows import wait_for_dota_windows


def load_config(path: str = "config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _sleep_until_windows_stable(title_contains: str, expected: int, stable_sec: float = 3.0, timeout_sec: float = 40.0):
    """
    Ждём, пока список окон перестанет "скакать" (Steam/Dota иногда пересоздают окно/меняют заголовок).
    """
    t0 = time.time()
    last_sig = None
    last_change = time.time()

    while time.time() - t0 < timeout_sec:
        wins = list_windows(title_contains)
        # сигнатура: hwnd + rect
        sig = [(w.hwnd, w.rect) for w in wins]
        if sig != last_sig:
            last_sig = sig
            last_change = time.time()

        if len(wins) >= expected and (time.time() - last_change) >= stable_sec:
            return wins

        time.sleep(0.5)

    # если не дождались стабильности — вернем что есть, но это лучше, чем падать
    return list_windows(title_contains)


def build_bots(cfg) -> List[Bot]:
    title = cfg["game_window_title_contains"]

    wins = list_windows(title)
    if len(wins) < 5:
        raise RuntimeError(f"Нашел только {len(wins)} окон Dota 2. Нужно минимум 5.")

    layout = cfg["layout"]
    cols = layout["cols"]
    rows = layout["rows"]
    padding = layout.get("padding", 0)

    # Рекомендуемый режим: фиксированные размеры (например 640x540 для 1920x1080 при 3x2)
    cell_w = layout.get("cell_w")
    cell_h = layout.get("cell_h")
    if cell_w is None or cell_h is None:
        # fallback (если в конфиге не задали) — всё равно считаем, но лучше задать фикс
        screen_w = layout["screen_w"]
        screen_h = layout["screen_h"]
        cell_w = (screen_w - padding * (cols + 1)) // cols
        cell_h = (screen_h - padding * (rows + 1)) // rows

    cells = compute_grid_cells_fixed(cols, rows, int(cell_w), int(cell_h), int(padding))

    bots: List[Bot] = []
    for i, bot_cfg in enumerate(cfg["bots"]):
        win = wins[i]
        grid_index = bot_cfg["grid_index"]

        _, x, y, w, h = cells[grid_index]

        # ВАЖНО: не ресайзим (чтобы не ломать mouse mapping). Только перемещаем.
        move_only(win.hwnd, x, y)

        bots.append(Bot(name=bot_cfg["name"], hwnd=win.hwnd))

    return bots


def run():
    cfg = load_config()

    # 1) Запуск 5 песочниц
    boxes = ["Box1", "Box2", "Box3", "Box4", "Box5"]
    launch_multiple(boxes)

    # 2) Ждём появления окон
    wait_for_dota_windows(5)

    # 3) Ждём, пока окна стабилизируются (важно для корректного списка/порядка)
    _sleep_until_windows_stable(cfg["game_window_title_contains"], expected=5)

    # 4) Собираем ботов и раскладываем окна
    bots = build_bots(cfg)

    # 5) Главный цикл
    tick_hz = cfg["loop"]["tick_hz"]
    dt = 1.0 / float(tick_hz)

    while True:
        t0 = time.time()

        for b in bots:
            try:
                b.tick()
            except Exception as e:
                print(f"[{b.name}] ERROR: {e}")

        spent = time.time() - t0
        time.sleep(max(0.0, dt - spent))

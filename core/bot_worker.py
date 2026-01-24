# core/bot_worker.py
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional, Tuple

import win32gui

from core.capture import grab_rect
from core.fsm import State
from core.window_manager import activate_window
from core.window_click import click_rect_center
from vision.hud import is_in_game
from vision.menu_detector import (
    find_accept_button,
    find_ready_button,
    find_ok_or_confirm,
    find_reconnect,
)

RectWin = Tuple[int, int, int, int]

def _mono() -> float:
    return time.monotonic()

def _safe_rect(hwnd: int) -> Optional[RectWin]:
    try:
        if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
            return None
        return win32gui.GetWindowRect(hwnd)
    except Exception:
        return None

@dataclass
class Bot:
    name: str
    hwnd: int

    state: State = State.BOOT
    state_since: float = field(default_factory=_mono)

    # анти-спам
    next_action_at: float = 0.0
    action_cd: float = 0.35

    # “прогресс” для таймаутов
    last_progress_at: float = field(default_factory=_mono)

    # game presence
    last_seen_in_game: float = 0.0

    # loading deadline после ACCEPT
    loading_deadline: float = 0.0

    def _set_state(self, st: State):
        if self.state != st:
            old = self.state
            self.state = st
            self.state_since = _mono()
            self._progress()
            print(f"[{self.name}] {old.name} -> {st.name}")

    def _progress(self):
        self.last_progress_at = _mono()

    def _can_act(self) -> bool:
        return _mono() >= self.next_action_at

    def _bump_cd(self, extra: float = 0.0):
        self.next_action_at = _mono() + self.action_cd + extra

    def _try_click(self, rect) -> bool:
        if rect is None:
            return False
        click_rect_center(self.hwnd, rect)
        self._bump_cd(0.25)
        self._progress()
        return True

    def tick(self):
        rect = _safe_rect(self.hwnd)
        if rect is None:
            self._set_state(State.RECOVERY)
            return

        # окно на передний план (для стабильности кликов/рендера)
        try:
            activate_window(self.hwnd)
        except Exception:
            pass

        from core.capture import get_client_rect_screen
        rect = get_client_rect_screen(self.hwnd)
        frame = grab_rect(rect)
        DEBUG = True
        DEBUG_EVERY = 5.0
        # в dataclass добавь:
        # last_debug: float = 0.0

        if DEBUG and (_mono() - self.last_debug) > DEBUG_EVERY:
            from vision.menu_detector import debug_masks
            from vision.debug_tools import save_dump

            rects = {
                "accept": find_accept_button(frame),
                "ready": find_ready_button(frame),
                "reconnect": find_reconnect(frame),
                "ok": find_ok_or_confirm(frame),
            }
            masks = debug_masks(frame)
            save_dump("debug_dumps", self.name, frame, rects, masks)
            self.last_debug = _mono()

        ingame = is_in_game(frame)
        if ingame:
            self.last_seen_in_game = _mono()

        # --- Глобальные быстрые реакции на попапы ---
        # Reconnect / OK часто перекрывают всё, поэтому обрабатываем в начале (если можно действовать)
        if not ingame and self._can_act():
            if self._try_click(find_reconnect(frame)):
                return
            if self._try_click(find_ok_or_confirm(frame)):
                return

        # --- Глобальный переход в игру ---
        if ingame:
            self._set_state(State.IN_GAME)

        # --- FSM ---
        if self.state == State.BOOT:
            self._set_state(State.MAIN_MENU)
            return

        if self.state == State.IN_GAME:
            # если HUD пропал надолго — вернуться в меню
            if not ingame and (_mono() - self.last_seen_in_game) > 8:
                self._set_state(State.MAIN_MENU)
            return

        # Ниже — только “менюшные” состояния
        accept_rect = find_accept_button(frame) if not ingame else None
        ready_rect = find_ready_button(frame) if not ingame else None

        # MAIN_MENU: пытаемся определить куда попали
        if self.state == State.MAIN_MENU:
            if ready_rect is not None:
                self._set_state(State.LOBBY)
                return
            if accept_rect is not None:
                self._set_state(State.MATCH_FOUND)
                return

            # Таймаут: если долго стоим, уходим в RECOVERY
            if (_mono() - self.last_progress_at) > 45:
                self._set_state(State.RECOVERY)
            return

        # LOBBY: жмём READY, следим за ACCEPT
        if self.state == State.LOBBY:
            if accept_rect is not None:
                self._set_state(State.MATCH_FOUND)
                return

            if self._can_act():
                if self._try_click(ready_rect):
                    # после READY обычно ждём accept/загрузку
                    self._bump_cd(0.4)
                    return

            # если READY не видим долго — возможно ушли из лобби
            if ready_rect is None and (_mono() - self.last_progress_at) > 20:
                self._set_state(State.MAIN_MENU)
            return

        # MATCH_FOUND: жмём ACCEPT, переходим в LOADING
        if self.state == State.MATCH_FOUND:
            if self._can_act():
                if self._try_click(accept_rect):
                    self._set_state(State.LOADING)
                    # ждём вход в игру (настрой под себя)
                    self.loading_deadline = _mono() + 70
                    return

            # если ACCEPT исчез и мы не в игре — возможно окно не успело отрисоваться/попап закрыли
            if accept_rect is None and not ingame and (_mono() - self.last_progress_at) > 10:
                # попробуем вернуться в лобби/меню по признакам
                if ready_rect is not None:
                    self._set_state(State.LOBBY)
                else:
                    self._set_state(State.MAIN_MENU)
            return

        # LOADING: ничего не кликаем (кроме OK/Reconnect выше), просто ждём ingame
        if self.state == State.LOADING:
            if ingame:
                self._set_state(State.IN_GAME)
                return

            if self.loading_deadline and _mono() > self.loading_deadline:
                # загрузка не дошла до игры — recovery
                self._set_state(State.RECOVERY)
            return

        # RECOVERY: пробуем “расшевелить” (OK/Reconnect уже обработаны сверху)
        if self.state == State.RECOVERY:
            # если видим READY/ACCEPT — возвращаемся в нормальные ветки
            if ready_rect is not None:
                self._set_state(State.LOBBY)
                return
            if accept_rect is not None:
                self._set_state(State.MATCH_FOUND)
                return

            # если долго без прогресса — обратно в MAIN_MENU (мягко)
            if (_mono() - self.last_progress_at) > 30:
                self._set_state(State.MAIN_MENU)
            return

# vision/menu_detector.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

import cv2
import numpy as np

Rect = Tuple[int, int, int, int]  # x,y,w,h


@dataclass
class DetectorConfig:
    # Минимальная площадь "кнопки" (в пикселях) в координатах кадра окна
    min_area: int = 2500
    # Минимальная ширина/высота
    min_w: int = 90
    min_h: int = 28
    # Примерное соотношение сторон кнопки
    min_aspect: float = 2.0
    max_aspect: float = 10.0

    # Порог "насколько прямоугольник" (0..1), ближе к 1 = почти прямоугольник
    rect_score_min: float = 0.75


CFG = DetectorConfig()


def _roi(frame: np.ndarray, rel: Tuple[float, float, float, float]) -> Tuple[np.ndarray, int, int]:
    """ROI по относительным координатам: (x0,y0,x1,y1) в долях."""
    h, w = frame.shape[:2]
    x0 = int(w * rel[0]); y0 = int(h * rel[1])
    x1 = int(w * rel[2]); y1 = int(h * rel[3])
    x0 = max(0, min(w - 1, x0))
    y0 = max(0, min(h - 1, y0))
    x1 = max(x0 + 1, min(w, x1))
    y1 = max(y0 + 1, min(h, y1))
    return frame[y0:y1, x0:x1], x0, y0


def _mask_hsv(frame_bgr: np.ndarray, ranges: List[Tuple[Tuple[int, int, int], Tuple[int, int, int]]]) -> np.ndarray:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    mask = None
    for lo, hi in ranges:
        m = cv2.inRange(hsv, np.array(lo, dtype=np.uint8), np.array(hi, dtype=np.uint8))
        mask = m if mask is None else cv2.bitwise_or(mask, m)

    # чистим шум
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask


def _rect_score(cnt) -> float:
    """Насколько контур похож на прямоугольник (по заполнению bounding box)."""
    x, y, w, h = cv2.boundingRect(cnt)
    area = cv2.contourArea(cnt)
    if w <= 0 or h <= 0:
        return 0.0
    return float(area) / float(w * h)


def _candidates_from_mask(mask: np.ndarray) -> List[Rect]:
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out: List[Rect] = []

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area < CFG.min_area:
            continue
        if w < CFG.min_w or h < CFG.min_h:
            continue
        aspect = w / float(h)
        if not (CFG.min_aspect <= aspect <= CFG.max_aspect):
            continue
        if _rect_score(c) < CFG.rect_score_min:
            continue
        out.append((x, y, w, h))

    out.sort(key=lambda r: r[2] * r[3], reverse=True)
    return out


def _pick_best(rects: List[Rect]) -> Optional[Rect]:
    return rects[0] if rects else None


# --- Цветовые диапазоны ---
GREEN_RANGES = [((35, 70, 70), (85, 255, 255))]          # ACCEPT/READY часто зеленые
BLUE_RANGES = [((90, 70, 70), (135, 255, 255))]          # RECONNECT часто синий
ORANGE_RANGES = [((10, 80, 90), (25, 255, 255)),
                 ((25, 80, 90), (35, 255, 255))]         # OK/Confirm иногда оранж/желтый


# --- ROI зоны (под FSM) ---
# ACCEPT: чаще всего большая зелёная кнопка в центре-низу попапа
ROI_ACCEPT = (0.30, 0.55, 0.70, 0.92)

# READY: чаще всего кнопка в правом нижнем углу (лобби)
ROI_READY = (0.62, 0.70, 0.98, 0.98)

# Центр экрана: OK/CONFIRM/RECONNECT диалоги
ROI_CENTER = (0.25, 0.30, 0.75, 0.80)

# Оставим старую зону (на всякий) — “крупные кнопки внизу/центре”
ROI_CENTER_BOTTOM = ROI_ACCEPT


def _find_by_color_in_roi(frame_bgr: np.ndarray,
                          roi_rel: Tuple[float, float, float, float],
                          color_ranges) -> Optional[Rect]:
    roi, ox, oy = _roi(frame_bgr, roi_rel)
    mask = _mask_hsv(roi, color_ranges)
    rects = _candidates_from_mask(mask)
    best = _pick_best(rects)
    if best is None:
        return None
    x, y, w, h = best
    return (x + ox, y + oy, w, h)


# --- Новые функции для FSM ---
def find_accept_button(frame_bgr: np.ndarray) -> Optional[Rect]:
    return _find_by_color_in_roi(frame_bgr, ROI_ACCEPT, GREEN_RANGES)


def find_ready_button(frame_bgr: np.ndarray) -> Optional[Rect]:
    return _find_by_color_in_roi(frame_bgr, ROI_READY, GREEN_RANGES)


def find_reconnect(frame_bgr: np.ndarray) -> Optional[Rect]:
    return _find_by_color_in_roi(frame_bgr, ROI_CENTER, BLUE_RANGES)


def find_ok_or_confirm(frame_bgr: np.ndarray) -> Optional[Rect]:
    # может быть оранжевый/зелёный/синий — соберём всё
    roi, ox, oy = _roi(frame_bgr, ROI_CENTER)

    mask_orange = _mask_hsv(roi, ORANGE_RANGES)
    mask_green = _mask_hsv(roi, GREEN_RANGES)
    mask_blue = _mask_hsv(roi, BLUE_RANGES)
    mask = cv2.bitwise_or(mask_orange, cv2.bitwise_or(mask_green, mask_blue))

    rects = _candidates_from_mask(mask)
    best = _pick_best(rects)
    if best is None:
        return None
    x, y, w, h = best
    return (x + ox, y + oy, w, h)


# --- Совместимость: старое имя (можешь удалить, если не нужно) ---
def find_accept_or_ready(frame_bgr: np.ndarray) -> Optional[Rect]:
    # раньше это было “зелёная в центре-низу”
    return find_accept_button(frame_bgr)


def debug_masks(frame_bgr: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Маски для отладки (сами маски в координатах ROI, а не всего окна).
    """
    roi_acc, _, _ = _roi(frame_bgr, ROI_ACCEPT)
    roi_ready, _, _ = _roi(frame_bgr, ROI_READY)
    roi_c, _, _ = _roi(frame_bgr, ROI_CENTER)

    return {
        "green_accept_roi": _mask_hsv(roi_acc, GREEN_RANGES),
        "green_ready_roi": _mask_hsv(roi_ready, GREEN_RANGES),
        "blue_center_roi": _mask_hsv(roi_c, BLUE_RANGES),
        "orange_center_roi": _mask_hsv(roi_c, ORANGE_RANGES),
    }

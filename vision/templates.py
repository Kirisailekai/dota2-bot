import cv2
import numpy as np
from typing import Optional, Tuple


def find_template(
    frame_bgr: np.ndarray,
    template_bgr: np.ndarray,
    threshold: float = 0.85,
) -> Optional[Tuple[int, int, int, int]]:
    """
    Возвращает (x, y, w, h) центра совпадения
    """
    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(frame_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if max_val < threshold:
        return None

    h, w = tpl_gray.shape[:2]
    x, y = max_loc
    return x, y, w, h

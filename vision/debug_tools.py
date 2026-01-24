import os, time
import cv2
import numpy as np
from typing import Dict, Optional, Tuple

Rect = Tuple[int, int, int, int]

def _ensure(p: str):
    os.makedirs(p, exist_ok=True)

def _draw(img, rect: Rect, label: str):
    x,y,w,h = rect
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.putText(img, label, (x, max(0, y-6)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

def save_dump(out_dir: str, bot: str, frame_bgr: np.ndarray,
              rects: Dict[str, Optional[Rect]],
              masks: Dict[str, np.ndarray]):
    _ensure(out_dir)
    ts = time.strftime("%Y%m%d_%H%M%S")

    vis = frame_bgr.copy()
    for k,r in rects.items():
        if r is not None:
            _draw(vis, r, k)

    cv2.imwrite(os.path.join(out_dir, f"{bot}_{ts}_frame.png"), frame_bgr)
    cv2.imwrite(os.path.join(out_dir, f"{bot}_{ts}_vis.png"), vis)
    for k,m in masks.items():
        cv2.imwrite(os.path.join(out_dir, f"{bot}_{ts}_mask_{k}.png"), m)

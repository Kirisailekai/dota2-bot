import cv2
import numpy as np

def is_in_game(frame_bgr) -> bool:
    h, w = frame_bgr.shape[:2]
    # нижняя полоска интерфейса (примерная зона)
    roi = frame_bgr[int(h*0.78):h, int(w*0.15):int(w*0.85)]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    # если интерфейс есть, обычно больше контраста/деталей
    edges = cv2.Canny(gray, 60, 140)
    score = float(np.mean(edges > 0))
    return score > 0.02

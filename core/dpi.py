# core/dpi.py
import ctypes

def set_dpi_aware():
    """
    Делает процесс DPI-aware, чтобы координаты и размеры окон были в "реальных" пикселях,
    иначе при scaling 125/150% будет смещение кликов.
    """
    try:
        shcore = ctypes.WinDLL("Shcore")
        # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass

    try:
        user32 = ctypes.WinDLL("user32")
        user32.SetProcessDPIAware()
    except Exception:
        pass

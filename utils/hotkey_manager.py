import keyboard
import threading
from window_manager import WindowManager
import json
import os


class HotkeyManager:
    def __init__(self, config_path: str = "config/window_layout.json"):
        self.wm = WindowManager()
        self.config_path = config_path
        self.load_config()
        self.running = False

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "hotkeys": {
                    "arrange_windows": "ctrl+alt+a",
                    "minimize_all": "ctrl+alt+m",
                    "restore_all": "ctrl+alt+r"
                }
            }

    def start(self):
        """Запускает отслеживание горячих клавиш"""
        self.running = True

        # Регистрируем горячие клавиши
        hotkeys = self.config.get("hotkeys", {})

        keyboard.add_hotkey(hotkeys.get("arrange_windows", "ctrl+alt+a"),
                            self.arrange_windows)
        keyboard.add_hotkey(hotkeys.get("minimize_all", "ctrl+alt+m"),
                            self.minimize_all)
        keyboard.add_hotkey(hotkeys.get("restore_all", "ctrl+alt+r"),
                            self.restore_all)

        print(f"Горячие клавиши активированы:")
        print(f"  {hotkeys.get('arrange_windows')} - Расположить окна")
        print(f"  {hotkeys.get('minimize_all')} - Свернуть все")
        print(f"  {hotkeys.get('restore_all')} - Восстановить все")
        print("Нажмите Ctrl+C для выхода")

        try:
            keyboard.wait()  # Ожидаем нажатия клавиш
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Останавливает отслеживание горячих клавиш"""
        self.running = False
        keyboard.unhook_all()

    def arrange_windows(self):
        print("Горячая клавиша: располагаю окна...")
        self.wm.arrange_windows_grid()

    def minimize_all(self):
        print("Горячая клавиша: сворачиваю все окна...")
        self.wm.minimize_all()

    def restore_all(self):
        print("Горячая клавиша: восстанавливаю все окна...")
        self.wm.restore_all()
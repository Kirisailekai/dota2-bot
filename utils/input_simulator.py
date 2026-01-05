import win32api
import win32con
import win32gui
import asyncio


class InputSimulator:
    def __init__(self, window_handle=None):
        self.window_handle = window_handle

    async def activate_window(self):
        """Активация окна для ввода"""
        if self.window_handle:
            win32gui.SetForegroundWindow(self.window_handle)
            await asyncio.sleep(0.1)

    async def click_position(self, x, y, button='left'):
        """Клик по позиции"""
        await self.activate_window()

        # Получаем координаты окна
        rect = win32gui.GetWindowRect(self.window_handle)
        window_x, window_y = rect[0], rect[1]

        # Абсолютные координаты
        absolute_x = window_x + x
        absolute_y = window_y + y

        # Устанавливаем позицию курсора
        win32api.SetCursorPos((absolute_x, absolute_y))

        # Эмулируем клик
        if button == 'left':
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            await asyncio.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
            await asyncio.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

    async def right_click(self, x, y):
        """Правый клик"""
        await self.click_position(x, y, 'right')

    async def press_key(self, key, modifiers=None):
        """Нажатие клавиши"""
        await self.activate_window()

        # Простой словарь для преобразования клавиш
        key_map = {
            'q': 0x51, 'w': 0x57, 'e': 0x45, 'r': 0x52,
            'a': 0x41, 's': 0x53, 'd': 0x44, 'f': 0x46,
            '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            'space': 0x20, 'tab': 0x09, 'shift': 0x10,
        }

        key_code = key_map.get(key.lower(), 0)
        if key_code:
            win32api.keybd_event(key_code, 0, 0, 0)  # Key down
            await asyncio.sleep(0.05)
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
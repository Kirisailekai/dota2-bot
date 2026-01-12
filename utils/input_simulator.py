import pyautogui
import win32gui
import win32con
import win32api
import time
import logging

logger = logging.getLogger(__name__)


class InputSimulator:
    """Эмулятор ввода для управления окнами Dota 2"""

    def __init__(self):
        # Настройки безопасности
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

    def activate_window(self, hwnd):
        """Активация окна по handle"""
        try:
            # Восстанавливаем окно если свернуто
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            # Активируем окно
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)

            # Фокусируем окно
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetActiveWindow(hwnd)

            return True
        except Exception as e:
            logger.error(f"Ошибка активации окна: {e}")
            return False

    def click_at(self, x: int, y: int, button='left', clicks=1):
        """Клик в указанных координатах"""
        try:
            # Получаем текущую позицию мыши
            current_x, current_y = pyautogui.position()

            # Перемещаем мышь и кликаем
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(0.1)
            pyautogui.click(button=button, clicks=clicks)
            time.sleep(0.1)

            # Возвращаем мышь на место (опционально)
            # pyautogui.moveTo(current_x, current_y, duration=0.1)

            return True
        except Exception as e:
            logger.error(f"Ошибка клика: {e}")
            return False

    def double_click_at(self, x: int, y: int, button='left'):
        """Двойной клик"""
        return self.click_at(x, y, button, clicks=2)

    def right_click_at(self, x: int, y: int):
        """Правый клик"""
        return self.click_at(x, y, button='right')

    def press_key(self, key: str, presses=1, interval=0.1):
        """Нажатие клавиши"""
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Ошибка нажатия клавиши {key}: {e}")
            return False

    def hotkey(self, *keys):
        """Комбинация клавиш"""
        try:
            pyautogui.hotkey(*keys)
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Ошибка комбинации клавиш {keys}: {e}")
            return False

    def type_text(self, text: str, interval=0.01):
        """Ввод текста"""
        try:
            pyautogui.write(text, interval=interval)
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Ошибка ввода текста: {e}")
            return False

    def drag_to(self, start_x: int, start_y: int, end_x: int, end_y: int, duration=0.5):
        """Перетаскивание мышью"""
        try:
            pyautogui.moveTo(start_x, start_y, duration=0.1)
            time.sleep(0.1)
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            return True
        except Exception as e:
            logger.error(f"Ошибка перетаскивания: {e}")
            return False

    def scroll(self, clicks: int):
        """Прокрутка колесика мыши"""
        try:
            pyautogui.scroll(clicks)
            time.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Ошибка прокрутки: {e}")
            return False

    def get_screen_size(self):
        """Получение размера экрана"""
        return pyautogui.size()

    def get_cursor_position(self):
        """Получение текущей позиции курсора"""
        return pyautogui.position()

    def screenshot(self, region=None):
        """Скриншот области экрана"""
        try:
            if region:
                return pyautogui.screenshot(region=region)
            else:
                return pyautogui.screenshot()
        except Exception as e:
            logger.error(f"Ошибка скриншота: {e}")
            return None

    def locate_on_screen(self, image_path, confidence=0.8):
        """Поиск изображения на экране"""
        try:
            return pyautogui.locateOnScreen(image_path, confidence=confidence)
        except Exception as e:
            logger.error(f"Ошибка поиска изображения: {e}")
            return None
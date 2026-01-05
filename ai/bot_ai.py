import cv2
import numpy as np
import asyncio
from PIL import ImageGrab
import win32gui
import win32con


class BotController:
    def __init__(self, bot_id, window_handle=None):
        self.bot_id = bot_id
        self.window_handle = window_handle
        self.hero_state = {}
        self.game_state = {}
        self.is_running = False

    async def initialize(self):
        """Инициализация бота"""
        print(f"Инициализирую бота {self.bot_id}")
        if self.window_handle:
            # Активируем окно
            win32gui.SetForegroundWindow(self.window_handle)
            await asyncio.sleep(0.5)

    async def capture_screen(self):
        """Захват экрана окна игры"""
        if not self.window_handle:
            return None

        # Получаем размеры окна
        rect = win32gui.GetWindowRect(self.window_handle)
        x, y, x2, y2 = rect
        width = x2 - x
        height = y2 - y

        # Делаем скриншот
        screenshot = ImageGrab.grab(bbox=(x, y, x2, y2))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    async def analyze_game_state(self, image):
        """Анализ состояния игры из изображения"""
        if image is None:
            return

        # Здесь будет логика анализа изображения
        # Например, поиск здоровья, маны, позиции героя и т.д.

        # Пример: поиск красного цвета (здоровье)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Маска для здоровья (красный)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask_health = cv2.inRange(hsv, lower_red, upper_red)

        # Анализ результатов
        health_percentage = np.sum(mask_health > 0) / mask_health.size

        self.hero_state['health_percent'] = health_percentage

    async def make_decision(self):
        """Принятие решения на основе состояния"""
        health = self.hero_state.get('health_percent', 1.0)

        if health < 0.3:
            return 'retreat'
        elif health < 0.6:
            return 'farm_safe'
        else:
            return 'attack'

    async def execute_action(self, action):
        """Выполнение действия"""
        from utils.input_simulator import InputSimulator

        simulator = InputSimulator(self.window_handle)

        if action == 'retreat':
            # Отступление к фонтану
            await simulator.click_position(100, 100)  # Клик на мини-карте
            await simulator.press_key('q')  # Использование способности

        elif action == 'farm_safe':
            # Фарм крипов
            await simulator.right_click(500, 300)  # Атака крипа

        elif action == 'attack':
            # Атака врага
            await simulator.right_click(600, 300)  # Атака героя
            await simulator.press_key('w')  # Использование способности

    async def run(self):
        """Основной цикл бота"""
        self.is_running = True

        while self.is_running:
            try:
                # 1. Захват экрана
                image = await self.capture_screen()

                # 2. Анализ состояния
                await self.analyze_game_state(image)

                # 3. Принятие решения
                decision = await self.make_decision()

                # 4. Выполнение действия
                await self.execute_action(decision)

                # 5. Пауза между итерациями
                await asyncio.sleep(0.5)  # 2 FPS для бота

            except Exception as e:
                print(f"Ошибка в боте {self.bot_id}: {e}")
                await asyncio.sleep(1)

    async def shutdown(self):
        """Остановка бота"""
        self.is_running = False
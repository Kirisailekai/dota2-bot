import asyncio
import cv2
import numpy as np
from PIL import ImageGrab
import win32gui

from ai.bot_ai import BotAI
from ai.roles import Role
from ai.types import HeroState, GameState
from utils.input_simulator import InputSimulator


class BotController:
    def __init__(self, bot_id, window_handle):
        self.bot_id = bot_id
        self.window_handle = window_handle

        self.hero_state = None
        self.game_state = None

        self.ai = BotAI(bot_id, Role.CARRY)
        self.is_running = False

    async def capture_screen(self):
        rect = win32gui.GetWindowRect(self.window_handle)
        x1, y1, x2, y2 = rect
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    async def analyze_game_state(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        hp_percent = np.sum(mask > 0) / mask.size

        self.hero_state = HeroState(
            hp=int(hp_percent * 1000),
            max_hp=1000,
            mana=500,
            level=1,
            position=(3000, 3000),
            abilities_ready={"q": True, "w": True},
            items_ready={},
            is_alive=hp_percent > 0
        )

        self.game_state = GameState(
            time=0.0,
            visible_units=[],
            creeps_enemy=[],
            creeps_ally=[],
            heroes_enemy=[]
        )

    async def run(self):
        self.is_running = True

        while self.is_running:
            image = await self.capture_screen()
            await self.analyze_game_state(image)

            if self.hero_state and self.game_state:
                sim = InputSimulator(self.window_handle)
                self.ai.tick(self.hero_state, self.game_state, sim)

            await asyncio.sleep(0.5)

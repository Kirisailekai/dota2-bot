from typing import Dict, Any
import time

from ai.bot_ai import BotAI


class MyBotAI(BotAI):
    """
    Конкретная реализация логики бота Dota 2
    Наследуется от абстрактного BotAI
    """

    def __init__(self, bot_id: int):
        super().__init__(bot_id)

        # Внутреннее состояние логики
        self.current_mode = "idle"   # idle / farm / fight / retreat

    def make_decision(self) -> Dict[str, Any]:
        """
        Принятие решения на основе текущего состояния игры
        Ожидается, что self.game_state уже обновлён извне
        """

        # Защита от пустого состояния
        if not self.game_state:
            return {"action": "idle"}

        hero_hp = self.game_state.get("hero_hp", 1.0)
        enemies_visible = self.game_state.get("enemies_visible", 0)
        creeps_visible = self.game_state.get("creeps_visible", 0)

        # 1. Критическое ХП — отступаем
        if hero_hp < 0.3:
            self.current_mode = "retreat"
            return {
                "action": "retreat",
                "target": "fountain"
            }

        # 2. Есть враги — дерёмся
        if enemies_visible > 0:
            self.current_mode = "fight"
            return {
                "action": "attack",
                "target": "enemy_hero"
            }

        # 3. Есть крипы — фарм
        if creeps_visible > 0:
            self.current_mode = "farm"
            return {
                "action": "farm",
                "target": "creep"
            }

        # 4. Иначе — движение по линии
        self.current_mode = "idle"
        return {
            "action": "move",
            "target_x": 3000,
            "target_y": 3000
        }

    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Выполнение действия.
        Здесь пока заглушка — реальный ввод делает Controller / InputSimulator.
        """

        try:
            self.logger.info(
                f"Действие: {action.get('action')} | режим: {self.current_mode}"
            )

            # Учет статистики
            self.performance_stats["actions_count"] += 1
            self.last_action_time = time.time()

            # Реальное выполнение происходит вне AI
            return True

        except Exception as e:
            self.performance_stats["errors_count"] += 1
            self.logger.error(f"Ошибка execute_action: {e}")
            return False

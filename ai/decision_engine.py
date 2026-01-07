from enum import Enum, auto


class Action(Enum):
    IDLE = auto()
    MOVE = auto()
    ATTACK = auto()
    RETREAT = auto()
    FARM = auto()


class DecisionEngine:
    def decide(self, hero, game):
        if not hero.is_alive:
            return Action.IDLE, None

        hp_ratio = hero.hp / hero.max_hp

        # 1. Критическое ХП — отступаем
        if hp_ratio < 0.3:
            return Action.RETREAT, self.safe_position(hero)

        # 2. Есть враг — атакуем
        if game.heroes_enemy:
            enemy = game.heroes_enemy[0]
            return Action.ATTACK, enemy.position

        # 3. Есть крипы — фармим
        if game.creeps_enemy:
            creep = game.creeps_enemy[0]
            return Action.FARM, creep.position

        # 4. Иначе — стоим на лайне
        return Action.MOVE, self.lane_position()

    def safe_position(self, hero):
        x, y = hero.position
        return (x - 400, y)

    def lane_position(self):
        return (3000, 3000)

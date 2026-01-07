from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Unit:
    name: str
    hp: int
    max_hp: int
    position: Tuple[int, int]
    is_enemy: bool
    is_hero: bool


@dataclass
class HeroState:
    hp: int
    max_hp: int
    mana: int
    level: int
    position: Tuple[int, int]
    abilities_ready: Dict[str, bool]
    items_ready: Dict[str, bool]
    is_alive: bool


@dataclass
class GameState:
    time: float
    visible_units: List[Unit]
    creeps_enemy: List[Unit]
    creeps_ally: List[Unit]
    heroes_enemy: List[Unit]

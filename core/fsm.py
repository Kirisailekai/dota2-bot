# core/fsm.py
from enum import Enum, auto

class State(Enum):
    BOOT = auto()

    MAIN_MENU = auto()     # главное меню / любой экран до лобби
    LOBBY = auto()         # в лобби (видим READY)
    MATCH_FOUND = auto()   # найден матч (видим ACCEPT)
    LOADING = auto()       # после ACCEPT, ждём вход в игру

    IN_GAME = auto()

    RECOVERY = auto()

from enum import Enum


class TankType(Enum):
    BASIC = 1
    TWIN = 2
    SNIPER = 3
    MACHINE_GUN = 4
    FLANK_GUARD = 5

class EnemyType(Enum):
    SQUARE_TURRET = 1
    TRIANGLE_BLADE = 2
    PENTAGON_GUNNER = 3

class BarrierType(Enum):
    WALL = "wall"
    CORRUPTION = "corruption"
    FIREWALL = "firewall"

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETE = 4
    GAME_OVER = 5
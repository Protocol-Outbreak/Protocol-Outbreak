from enum import Enum


class TankType(Enum):
    BASIC = 1
    TWIN = 2
    TRIPLET = 3
    QUAD = 4
    OCTO = 5
    PENTA_SHOT = 6
    SNIPER = 7
    MACHINE_GUN = 8
    FLANK_GUARD = 9

class EnemyType(Enum):
    SQUARE_TURRET = 1
    TRIANGLE_BLADE = 2
    PENTAGON_GUNNER = 3
    #SNIPER = 4
    #BOSS = 5

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
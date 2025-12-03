from enum import Enum

class TankType(Enum):
    BASIC = 1
    
    # === GUNNER PATH ===
    TWIN = 2
    TRIPLET = 3
    PENTA_SHOT = 6
    
    # === SNIPER PATH ===
    SNIPER = 7
    MARKSMAN = 10      # ← NEW
    RAILGUN = 11       # ← NEW
    
    # === SPRAYER PATH ===
    MACHINE_GUN = 8
    GATLING = 12       # ← NEW
    MINIGUN = 13       # ← NEW
    
    # === OTHER (kept for compatibility, not in paths) ===
    QUAD = 4
    OCTO = 5
    FLANK_GUARD = 9

class EnemyType(Enum):
    SQUARE_TURRET = 1
    TRIANGLE_BLADE = 2
    PENTAGON_GUNNER = 3
    BOSS = 4

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

# === NEW: Tank Path System ===
class TankPath(Enum):
    """The 3 tank progression paths"""
    NONE = 0        # No path chosen yet
    GUNNER = 1      # TWIN → TRIPLET → PENTA_SHOT
    SNIPER = 2      # SNIPER → MARKSMAN → RAILGUN
    SPRAYER = 3     # MACHINE_GUN → GATLING → MINIGUN
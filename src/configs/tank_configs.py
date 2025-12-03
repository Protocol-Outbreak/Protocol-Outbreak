"""
All tank configurations in one place.
Tank progression paths implemented.
"""

TANK_CONFIGS = {
    # ========================================
    # STARTER TANK
    # ========================================
    "BASIC": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 1.0,
        "reload_speed": 1.0,
        "description": "Basic single cannon"
    },
    
    # ========================================
    # GUNNER PATH: Area Control
    # TWIN → TRIPLET → PENTA_SHOT
    # ========================================
    "TWIN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, -8)},
            {"angle_offset": 0, "position_offset": (0, 8)}
        ],
        "damage_multiplier": 0.85,  # Slightly better than before
        "reload_speed": 1.0,
        "description": "Two parallel cannons - Tier 1 Gunner"
    },
    
    "TRIPLET": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, -10)},
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 0, "position_offset": (0, 10)}
        ],
        "damage_multiplier": 0.65,  # NERFED from 0.7
        "reload_speed": 0.95,  # Slightly slower reload
        "description": "Three parallel cannons - Tier 2 Gunner"
    },
    
    "PENTA_SHOT": {
        "cannons": [
            {"angle_offset": -8, "position_offset": (0, -12)},   # TIGHTER SPREAD
            {"angle_offset": -4, "position_offset": (0, -6)},    # TIGHTER SPREAD
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 4, "position_offset": (0, 6)},      # TIGHTER SPREAD
            {"angle_offset": 8, "position_offset": (0, 12)}      # TIGHTER SPREAD
        ],
        "damage_multiplier": 0.7,  # Buffed from 0.65
        "reload_speed": 0.9,
        "description": "Five tight-spread cannons - Tier 3 Gunner"
    },
    
    # ========================================
    # SNIPER PATH: Long-Range Precision
    # SNIPER → MARKSMAN → RAILGUN
    # ========================================
    "SNIPER": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 1.8,  # Reduced from 2.25 for progression
        "reload_speed": 0.5,  # Faster than before
        "bullet_speed_bonus": 1.5,
        "description": "High damage, long range - Tier 1 Sniper"
    },
    
    "MARKSMAN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 2.2,  # Higher damage
        "reload_speed": 0.55,
        "bullet_speed_bonus": 1.8,  # Faster bullets
        "penetration_bonus": 1,  # +1 base penetration
        "description": "Faster bullets, penetration - Tier 2 Sniper"
    },
    
    "RAILGUN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 2.5,  # Maximum single-target damage
        "reload_speed": 0.6,
        "bullet_speed_bonus": 2.0,  # Fastest bullets
        "penetration_bonus": 3,  # +3 base penetration (pierces 3 enemies minimum)
        "description": "Pierce multiple enemies - Tier 3 Sniper"
    },
    
    # ========================================
    # SPRAYER PATH: Suppressive Fire
    # MACHINE_GUN → GATLING → MINIGUN
    # ========================================
    "MACHINE_GUN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.6,
        "reload_speed": 1.8,  # Reduced from 2.0
        "spread": 0.12,  # Reduced from 0.15 (tighter)
        "description": "Fast fire, slight spread - Tier 1 Sprayer"
    },
    
    "GATLING": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.65,  # Slightly more damage
        "reload_speed": 2.2,  # Even faster
        "spread": 0.1,  # Tighter spread
        "description": "Very fast fire - Tier 2 Sprayer"
    },
    
    "MINIGUN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.7,  # Best sprayer damage
        "reload_speed": 2.5,  # Maximum fire rate
        "spread": 0.08,  # Tightest spread
        "description": "Maximum fire rate - Tier 3 Sprayer"
    },
    
    # ========================================
    # LEGACY TANKS (not in paths, kept for compatibility)
    # ========================================
    "QUAD": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 90, "position_offset": (0, 0)},
            {"angle_offset": 180, "position_offset": (0, 0)},
            {"angle_offset": 270, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.6,
        "reload_speed": 1.0,
        "description": "Four directional cannons"
    },
    
    "OCTO": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 45, "position_offset": (0, 0)},
            {"angle_offset": 90, "position_offset": (0, 0)},
            {"angle_offset": 135, "position_offset": (0, 0)},
            {"angle_offset": 180, "position_offset": (0, 0)},
            {"angle_offset": 225, "position_offset": (0, 0)},
            {"angle_offset": 270, "position_offset": (0, 0)},
            {"angle_offset": 315, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.5,
        "reload_speed": 1.2,
        "description": "Eight directional cannons"
    },
    
    "FLANK_GUARD": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 180, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.8,
        "reload_speed": 1.0,
        "description": "Front and back cannons"
    },
}

# ========================================
# PATH PROGRESSION MAPS
# ========================================
PATH_PROGRESSIONS = {
    "GUNNER": {
        5: "TWIN",
        15: "TRIPLET", # should be 15
        25: "PENTA_SHOT" # should be 25
    },
    "SNIPER": {
        5: "SNIPER",
        15: "MARKSMAN", # should be 15
        25: "RAILGUN" # should be 25
    },
    "SPRAYER": {
        5: "MACHINE_GUN",
        15: "GATLING",
        25: "MINIGUN"
    }
}

# Helper function to get tank for a path at a specific level
def get_tank_for_path_level(path_name, level):
    """
    Get the appropriate tank type for a path at a given level
    Returns tank name string or None
    """
    if path_name not in PATH_PROGRESSIONS:
        return None
    
    progression = PATH_PROGRESSIONS[path_name]
    
    # Find the highest level threshold that's <= current level
    available_levels = [lvl for lvl in progression.keys() if lvl <= level]
    if not available_levels:
        return None
    
    highest_available = max(available_levels)
    return progression[highest_available]
"""
All tank configurations in one place.
Add new tanks by just adding to this dictionary!
"""

TANK_CONFIGS = {
    "BASIC": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 1.0,
        "reload_speed": 1.0,
        "description": "Basic single cannon"
    },
    
    "TWIN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, -10)},
            {"angle_offset": 0, "position_offset": (0, 10)}
        ],
        "damage_multiplier": 0.8,
        "reload_speed": 1.0,
        "description": "Two parallel cannons"
    },
    
    "TRIPLET": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, -12)},
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 0, "position_offset": (0, 12)}
        ],
        "damage_multiplier": 0.7,
        "reload_speed": 1.0,
        "description": "Three parallel cannons"
    },
    
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
    
    "PENTA_SHOT": {
        "cannons": [
            {"angle_offset": -30, "position_offset": (0, -15)},
            {"angle_offset": -15, "position_offset": (0, -8)},
            {"angle_offset": 0, "position_offset": (0, 0)},
            {"angle_offset": 15, "position_offset": (0, 8)},
            {"angle_offset": 30, "position_offset": (0, 15)}
        ],
        "damage_multiplier": 0.65,
        "reload_speed": 0.9,
        "description": "Five spread cannons"
    },
    
    "SNIPER": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 2.25,
        "reload_speed": 0.35,  # Slower reload
        "bullet_speed_bonus": 2.0,
        "description": "High damage, slow fire"
    },
    
    "MACHINE_GUN": {
        "cannons": [
            {"angle_offset": 0, "position_offset": (0, 0)}
        ],
        "damage_multiplier": 0.6,
        "reload_speed": 2.0,  # Super fast reload
        "spread": 0.15,  # Bullets spread out
        "description": "Fast fire, low accuracy"
    },
}
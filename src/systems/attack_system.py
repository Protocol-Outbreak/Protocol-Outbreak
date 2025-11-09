import math
import random
from src.configs.tank_configs import TANK_CONFIGS
from src.entities.bullet import Bullet

class ShootingSystem:
    """Handles shooting for all tank types from configuration"""
    
    @staticmethod
    def shoot(tank, bullets):
        """Create bullets for any tank type based on configuration"""
        if tank.shoot_cooldown > 0:
            return
        
        # Get tank config
        config = TANK_CONFIGS.get(tank.tank_type.name, TANK_CONFIGS["BASIC"])
        
        # Calculate bullet properties
        bullet_speed = 10 + (tank.stats['bullet_speed'] * 1.5)
        bullet_damage = (10 + (tank.stats['bullet_damage'] * 3)) * (1 + config["damage_multiplier"])
        bullet_pen = 1 + tank.stats['bullet_penetration']
        
        # Apply config bonuses
        if "bullet_speed_bonus" in config:
            bullet_speed *= config["bullet_speed_bonus"]
        
        offset = 30
        
        # Create bullet for each cannon
        for cannon in config["cannons"]:
            # Calculate cannon angle
            angle_offset = math.radians(cannon["angle_offset"])
            cannon_angle = tank.angle + angle_offset
            
            # Calculate spawn position
            pos_offset_x, pos_offset_y = cannon["position_offset"]
            perp_angle = tank.angle + math.pi / 2
            
            bullet_x = tank.x + math.cos(tank.angle) * offset
            bullet_y = tank.y + math.sin(tank.angle) * offset
            bullet_x += math.cos(perp_angle) * pos_offset_y
            bullet_y += math.sin(perp_angle) * pos_offset_y
            
            # Apply spread if configured (like machine gun)
            final_angle = cannon_angle
            if "spread" in config:
                spread = config["spread"]
                final_angle += random.uniform(-spread, spread)
            
            # Create bullet
            bullets.append(Bullet(
                bullet_x, bullet_y, final_angle,
                bullet_speed, bullet_damage, bullet_pen, "player"
            ))
        
        # Set cooldown
        tank.shoot_cooldown = tank.get_reload_speed() / config["reload_speed"]
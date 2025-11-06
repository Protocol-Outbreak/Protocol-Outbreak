import pygame
import math
from src.configs.tank_configs import TANK_CONFIGS
from src.utils.constants import *

class TankRenderer:
    """Handles drawing all tank types from configuration"""
    
    @staticmethod
    def draw_tank(screen, tank, camera_x, camera_y):
        """Draw any tank type based on its configuration"""
        screen_x = int(tank.x - camera_x)
        screen_y = int(tank.y - camera_y)
        
        # Get tank config
        config = TANK_CONFIGS.get(tank.tank_type.name, TANK_CONFIGS["BASIC"])
        
        cannon_length = 40
        cannon_width = 12
        cannon_color = GREY
        
        # Draw all cannons (behind body)
        for cannon in config["cannons"]:
            TankRenderer._draw_cannon(
                screen, screen_x, screen_y, 
                tank.angle, cannon, 
                cannon_length, cannon_width, cannon_color
            )
        
        # Draw body (on top)
        pygame.draw.circle(screen, CLEAN_BLUE, (screen_x, screen_y), tank.size - 8)
        #pygame.draw.circle(screen, CLEAN_BLUE, (screen_x, screen_y), tank.size, 3)
    
    @staticmethod
    def _draw_cannon(screen, screen_x, screen_y, base_angle, cannon_config, 
                     cannon_length, cannon_width, cannon_color):
        """Draw a single cannon"""
        # Calculate cannon angle
        angle_offset = math.radians(cannon_config["angle_offset"])
        cannon_angle = base_angle + angle_offset
        
        # Calculate cannon position offset (perpendicular to aim direction)
        pos_offset_x, pos_offset_y = cannon_config["position_offset"]
        perp_angle = base_angle + math.pi / 2
        
        offset_x = screen_x + math.cos(perp_angle) * pos_offset_y
        offset_y = screen_y + math.sin(perp_angle) * pos_offset_y
        
        # Calculate cannon end position
        end_x = offset_x + math.cos(cannon_angle) * cannon_length
        end_y = offset_y + math.sin(cannon_angle) * cannon_length
        
        # Draw cannon rectangle
        perp_cannon_angle = cannon_angle + math.pi / 2
        points = [
            (offset_x + math.cos(perp_cannon_angle) * cannon_width/2,
             offset_y + math.sin(perp_cannon_angle) * cannon_width/2),
            (offset_x - math.cos(perp_cannon_angle) * cannon_width/2,
             offset_y - math.sin(perp_cannon_angle) * cannon_width/2),
            (end_x - math.cos(perp_cannon_angle) * cannon_width/2,
             end_y - math.sin(perp_cannon_angle) * cannon_width/2),
            (end_x + math.cos(perp_cannon_angle) * cannon_width/2,
             end_y + math.sin(perp_cannon_angle) * cannon_width/2)
        ]
        pygame.draw.polygon(screen, cannon_color, points)
        pygame.draw.polygon(screen, CLEAN_BLUE, points, 2)
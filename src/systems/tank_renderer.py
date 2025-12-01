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
        
        # Draw movement trails (behind everything)
        if hasattr(tank, 'position_trail'):
            current_time = pygame.time.get_ticks()
            for i, trail_pos in enumerate(tank.position_trail):
                trail_age = current_time - trail_pos['time']
                if trail_age < 300:  # Trail fades over 300ms
                    alpha = max(0, 255 - (trail_age * 0.85))  # Fade out
                    trail_x = int(trail_pos['x'] - camera_x)
                    trail_y = int(trail_pos['y'] - camera_y)
                    
                    # Create transparent surface for trail
                    trail_surface = pygame.Surface((tank.size * 2, tank.size * 2), pygame.SRCALPHA)
                    trail_color = (*CLEAN_BLUE[:3], int(alpha * 0.3))  # Faint trail
                    pygame.draw.circle(trail_surface, trail_color, 
                                     (tank.size, tank.size), tank.size - 10)
                    screen.blit(trail_surface, (trail_x - tank.size, trail_y - tank.size))
        
        # Draw all cannons (behind body)
        for cannon in config["cannons"]:
            TankRenderer._draw_cannon(
                screen, screen_x, screen_y, 
                tank.angle, cannon, 
                cannon_length, cannon_width, cannon_color
            )
        
        # === LAYERED DRONE CONSTRUCTION ===
        
        # Check for damage flash
        damage_flash = False
        if hasattr(tank, 'damage_flash_time'):
            flash_duration = pygame.time.get_ticks() - tank.damage_flash_time
            if flash_duration < 200:  # Flash for 200ms
                damage_flash = True
        
        # Outer ring - pulses with movement
        if hasattr(tank, 'outer_ring_pulse'):
            pulse_scale = 1 + (math.sin(tank.outer_ring_pulse) * 0.05)  # 95-105% size
        else:
            pulse_scale = 1
        outer_radius = int((tank.size - 5) * pulse_scale)
        
        # Low health: outer ring flickers
        health_ratio = tank.hp / tank.max_hp if tank.max_hp > 0 else 1
        if health_ratio < 0.3:
            # Flickering effect at low health
            flicker_alpha = 128 + int(math.sin(pygame.time.get_ticks() * 0.01) * 127)
            outer_color = (*CLEAN_BLUE[:3], flicker_alpha)
        else:
            outer_color = CLEAN_BLUE
        
        # Damage flash: red outer ring
        if damage_flash:
            outer_color = (255, 50, 50)
        
        # Draw outer ring (3px thick)
        pygame.draw.circle(screen, outer_color, (screen_x, screen_y), outer_radius, 3)
        
        # Middle ring - rotates slowly
        if hasattr(tank, 'rotation_angle'):
            middle_radius = tank.size - 12
            # Draw 6 small nodes around the middle ring
            for i in range(6):
                node_angle = math.radians(tank.rotation_angle + (i * 60))
                node_x = screen_x + math.cos(node_angle) * middle_radius
                node_y = screen_y + math.sin(node_angle) * middle_radius
                pygame.draw.circle(screen, CLEAN_BLUE, (int(node_x), int(node_y)), 3)
        
        # Inner core - solid circle
        core_radius = tank.size - 18
        pygame.draw.circle(screen, CLEAN_BLUE, (screen_x, screen_y), core_radius)
        
        # Directional chevron/indicator pointing at cursor
        chevron_size = 15
        chevron_distance = tank.size - 8
        chevron_tip_x = screen_x + math.cos(tank.angle) * chevron_distance
        chevron_tip_y = screen_y + math.sin(tank.angle) * chevron_distance
        
        # Triangle points
        tip_point = (chevron_tip_x, chevron_tip_y)
        left_angle = tank.angle + math.radians(150)
        right_angle = tank.angle + math.radians(-150)
        left_point = (
            chevron_tip_x + math.cos(left_angle) * chevron_size,
            chevron_tip_y + math.sin(left_angle) * chevron_size
        )
        right_point = (
            chevron_tip_x + math.cos(right_angle) * chevron_size,
            chevron_tip_y + math.sin(right_angle) * chevron_size
        )
        
        # Draw directional indicator
        pygame.draw.polygon(screen, WHITE, [tip_point, left_point, right_point])
        pygame.draw.polygon(screen, CLEAN_BLUE, [tip_point, left_point, right_point], 2)
    
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
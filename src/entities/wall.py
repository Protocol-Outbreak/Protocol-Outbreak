import pygame
from src.utils.constants import *

class Wall:
    """Basic wall/barrier that blocks entities"""
    
    def __init__(self, x, y, width, height, wall_type="solid"):
        self.rect = pygame.Rect(x, y, width, height)
        self.wall_type = wall_type  # "solid", "border", "destructible"
        self.color = (100, 100, 100)  # Gray
        
        if wall_type == "border":
            self.color = (50, 50, 50)
        elif wall_type == "destructible":
            self.color = (150, 100, 50)
            self.hp = 100
        elif wall_type == "enemy_barrier":
            self.color = (200, 50, 50)  # Red for enemy barriers
            self.base_color = (200, 50, 50)
            self.glow_color = (255, 80, 80)
            self.glow_time = 0
        else:  # solid
            self.color = (100, 100, 100)  # Gray for solid walls

    def update(self, dt=1):
        if self.wall_type == "enemy_barrier":
            # Pulsing glow effect
            self.glow_time += dt * 0.1
            glow_intensity = (pygame.math.Vector2(1, 0).rotate(self.glow_time * 100).x + 1) / 2
            self.color = tuple(
                int(self.base_color[i] + (self.glow_color[i] - self.base_color[i]) * glow_intensity)
                for i in range(3)
            )
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the wall"""
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Special effects for enemy barriers

        pygame.draw.rect(screen, self.color, 
                    (draw_x, draw_y, self.rect.width, self.rect.height))
                    
        if self.wall_type == "enemy_barrier":
            # Glowing border
            pygame.draw.rect(screen, (255, 100, 100), 
                           (draw_x, draw_y, self.rect.width, self.rect.height), 3)
            
            # Warning stripes
            stripe_spacing = 20
            for i in range(0, self.rect.width + self.rect.height, stripe_spacing * 2):
                stripe_start_x = draw_x + i
                stripe_start_y = draw_y
                stripe_end_x = draw_x + i - self.rect.height
                stripe_end_y = draw_y + self.rect.height
                
                pygame.draw.line(screen, (255, 200, 0), 
                               (stripe_start_x, stripe_start_y), 
                               (stripe_end_x, stripe_end_y), 2)
        else:
                        # Normal border for other walls
            border_color = (80, 80, 80) if self.wall_type != "border" else (30, 30, 30)
            pygame.draw.rect(screen, border_color, 
                           (draw_x, draw_y, self.rect.width, self.rect.height), 2)
        
        # Health bar for destructible walls
        if self.wall_type == "enemy_barrier" and hasattr(self, 'hp') and self.hp < self.max_hp: # was self.wall_type == "destructible"
            bar_width = self.rect.width - 4
            bar_height = 4
            bar_x = draw_x + 2
            bar_y = draw_y + 2
            
            # Background
            pygame.draw.rect(screen, (60, 60, 60), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Health fill
            health_width = int((self.hp / self.max_hp) * bar_width)
            health_color = (100, 200, 100) if self.hp > 50 else (200, 100, 100)
            pygame.draw.rect(screen, health_color, 
                           (bar_x, bar_y, health_width, bar_height))
            # Main wall
            pygame.draw.rect(screen, self.color, 
                            (draw_x, draw_y, self.rect.width, self.rect.height))
            
            # Border for depth
            pygame.draw.rect(screen, (80, 80, 80), 
                            (draw_x, draw_y, self.rect.width, self.rect.height), 2)

    
    def collides_with(self, rect):
        """Check if a rect collides with this wall"""
        return self.rect.colliderect(rect)
    
    def take_damage(self, damage):
        """
        Deal damage to wall (only for destructible walls)
        
        Args:
            damage: Amount of damage to deal
        
        Returns:
            True if wall is destroyed, False otherwise
        """
        if self.wall_type == "destructible":
            self.hp -= damage
            return self.hp <= 0
        return False
import pygame
from src.utils.constants import *
from src.utils.enums import BarrierType


class Barrier:
    def __init__(self, x, y, width, height, barrier_type="wall"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = barrier_type
        self.z_index = 45
        
        self.rect = pygame.Rect(x, y, width, height)
        
        # Visual properties
        if barrier_type == "wall":
            self.color = WALL_COLOR
            self.outline_color = WALL_OUTLINE
            self.outline_width = 3
        elif barrier_type == "corruption":
            self.color = CORRUPTION_PURPLE
            self.outline_color = CORRUPTION_PINK
            self.outline_width = 2
        elif barrier_type == "firewall":
            self.color = CLEAN_BLUE
            self.outline_color = WHITE
            self.outline_width = 2
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        pygame.draw.rect(screen, self.color, 
                        (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(screen, self.outline_color, 
                        (screen_x, screen_y, self.width, self.height), 
                        self.outline_width)
    
    def collides_with_circle(self, circle_x, circle_y, radius):
        closest_x = max(self.x, min(circle_x, self.x + self.width))
        closest_y = max(self.y, min(circle_y, self.y + self.height))
        
        distance_x = circle_x - closest_x
        distance_y = circle_y - closest_y
        distance_squared = distance_x**2 + distance_y**2
        
        return distance_squared < (radius ** 2)

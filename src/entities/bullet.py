
import pygame
import math
from src.utils.constants import *

class Bullet:
    def __init__(self, x, y, angle, speed, damage, penetration, owner_type="player"):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.health = penetration * 10  # Penetration determines bullet health
        self.max_health = self.health
        self.owner_type = owner_type
        self.radius = 5
        self.z_index = 25  # Layer: Bullets drawn below enemies and player
        
        # Calculate velocity
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw bullet with health-based transparency
        health_percent = self.health / self.max_health
        color = CLEAN_BLUE if self.owner_type == "player" else CORRUPTION_ORANGE
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)
        
    def is_off_screen(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        return (screen_x < -100 or screen_x > SCREEN_WIDTH + 100 or 
                screen_y < -100 or screen_y > SCREEN_HEIGHT + 100)

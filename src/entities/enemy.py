import pygame
import math
from src.utils.constants import *
from src.utils.enums import EnemyType
from src.entities.bullet import Bullet

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.angle = 0
        self.health = 50
        self.max_health = 50
        self.size = 30
        self.speed = 1
        self.shoot_cooldown = 0
        self.shoot_delay = 60  # frames
        self.xp_value = 10
        self.z_index = 50  # Layer: Enemies drawn above bullets, below player
        
        # Set stats based on type
        if enemy_type == EnemyType.SQUARE_TURRET:
            self.health = 80
            self.max_health = 80
            self.speed = 0.5
            self.shoot_delay = 90
            self.xp_value = 15
        elif enemy_type == EnemyType.TRIANGLE_BLADE:
            self.health = 30
            self.max_health = 30
            self.speed = 3
            self.shoot_delay = 0  # Melee only
            self.xp_value = 25
        elif enemy_type == EnemyType.PENTAGON_GUNNER:
            self.health = 100
            self.max_health = 100
            self.speed = 1.5
            self.shoot_delay = 45
            self.xp_value = 50
    
    def update(self, player_x, player_y, bullets):
        # AI behavior
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.angle = math.atan2(dy, dx)
            
            # Movement based on type
            if self.type == EnemyType.TRIANGLE_BLADE:
                # Charge at player
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            elif self.type == EnemyType.SQUARE_TURRET:
                # Stay mostly stationary
                if distance > 400:
                    self.x += (dx / distance) * self.speed * 0.3
                    self.y += (dy / distance) * self.speed * 0.3
            elif self.type == EnemyType.PENTAGON_GUNNER:
                # Keep medium distance
                if distance < 300:
                    self.x -= (dx / distance) * self.speed
                    self.y -= (dy / distance) * self.speed
                elif distance > 400:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed
        
        # Shooting
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and self.shoot_delay > 0 and distance < 500:
            self.shoot(bullets)
            self.shoot_cooldown = self.shoot_delay
    
    def shoot(self, bullets):
        if self.type == EnemyType.SQUARE_TURRET:
            bullets.append(Bullet(self.x, self.y, self.angle, 8, 10, 3, "enemy"))
        elif self.type == EnemyType.PENTAGON_GUNNER:
            # 5-way shot
            for i in range(5):
                angle_offset = (i - 2) * 0.3
                bullets.append(Bullet(self.x, self.y, self.angle + angle_offset, 7, 8, 2, "enemy"))
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw based on type
        if self.type == EnemyType.SQUARE_TURRET:
            pygame.draw.rect(screen, CLEAN_BLUE, 
                           (screen_x - self.size//2, screen_y - self.size//2, self.size, self.size), 2)
        elif self.type == EnemyType.TRIANGLE_BLADE:
            points = [
                (screen_x + math.cos(self.angle) * self.size, 
                 screen_y + math.sin(self.angle) * self.size),
                (screen_x + math.cos(self.angle + 2.4) * self.size, 
                 screen_y + math.sin(self.angle + 2.4) * self.size),
                (screen_x + math.cos(self.angle - 2.4) * self.size, 
                 screen_y + math.sin(self.angle - 2.4) * self.size)
            ]
            pygame.draw.polygon(screen, CORRUPTION_PINK, points, 2)
        elif self.type == EnemyType.PENTAGON_GUNNER:
            points = []
            for i in range(5):
                angle = self.angle + (i * math.pi * 2 / 5)
                points.append((screen_x + math.cos(angle) * self.size,
                             screen_y + math.sin(angle) * self.size))
            pygame.draw.polygon(screen, CORRUPTION_ORANGE, points, 2)
        
        # Health bar
        bar_width = 40
        bar_height = 4
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, UI_GRAY, 
                        (screen_x - bar_width//2, screen_y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(screen, CORRUPTION_PINK, 
                        (screen_x - bar_width//2, screen_y - self.size - 10, 
                         int(bar_width * health_percent), bar_height))

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
        
        # Aggro system
        self.is_aggroed = False
        self.aggro_range = 300  # Distance at which enemy notices player
        self.deaggro_range = 500  # Distance at which enemy loses interest
        
        # Set stats based on type
        if enemy_type == EnemyType.SQUARE_TURRET:
            self.health = 80
            self.max_health = 80
            self.speed = 0.5
            self.shoot_delay = 90
            self.xp_value = 15
            self.aggro_range = 350  # Turrets have longer sight
        elif enemy_type == EnemyType.TRIANGLE_BLADE:
            self.health = 30
            self.max_health = 30
            self.speed = 3
            self.shoot_delay = 0  # Melee only
            self.xp_value = 25
            self.aggro_range = 250  # Blades have shorter sight
        elif enemy_type == EnemyType.PENTAGON_GUNNER:
            self.health = 100
            self.max_health = 100
            self.speed = 1.5
            self.shoot_delay = 45
            self.xp_value = 50
            self.aggro_range = 400  # Gunners have good sight
    
    def take_damage(self, damage):
        """Handle taking damage and trigger aggro"""
        self.health -= damage
        self.is_aggroed = True  # Getting hit always aggros
    
    def update(self, player_x, player_y, bullets):
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check aggro status
        if not self.is_aggroed:
            # Check if player enters aggro range
            if distance <= self.aggro_range:
                self.is_aggroed = True
        else:
            # Check if player is too far (deaggro)
            if distance > self.deaggro_range:
                self.is_aggroed = False
        
        # Only act if aggroed
        if self.is_aggroed and distance > 0:
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
        else:
            # Idle behavior - slowly rotate or do nothing
            self.angle += 0.02  # Slow idle rotation
    
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
        
        # Choose color based on aggro state
        if self.type == EnemyType.SQUARE_TURRET:
            color = CORRUPTION_PINK if self.is_aggroed else CLEAN_BLUE
            pygame.draw.rect(screen, color, 
                           (screen_x - self.size//2, screen_y - self.size//2, self.size, self.size), 2)
        elif self.type == EnemyType.TRIANGLE_BLADE:
            color = CORRUPTION_ORANGE if self.is_aggroed else CORRUPTION_PINK
            points = [
                (screen_x + math.cos(self.angle) * self.size, 
                 screen_y + math.sin(self.angle) * self.size),
                (screen_x + math.cos(self.angle + 2.4) * self.size, 
                 screen_y + math.sin(self.angle + 2.4) * self.size),
                (screen_x + math.cos(self.angle - 2.4) * self.size, 
                 screen_y + math.sin(self.angle - 2.4) * self.size)
            ]
            pygame.draw.polygon(screen, color, points, 2)
        elif self.type == EnemyType.PENTAGON_GUNNER:
            color = (255, 100, 100) if self.is_aggroed else CORRUPTION_ORANGE
            points = []
            for i in range(5):
                angle = self.angle + (i * math.pi * 2 / 5)
                points.append((screen_x + math.cos(angle) * self.size,
                             screen_y + math.sin(angle) * self.size))
            pygame.draw.polygon(screen, color, points, 2)
        
        # Optional: Draw aggro range indicator (for debugging)
        if not self.is_aggroed:
            pygame.draw.circle(screen, (100, 100, 100), (screen_x, screen_y), self.aggro_range, 1)
        
        # Health bar
        bar_width = 40
        bar_height = 4
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, UI_GRAY, 
                        (screen_x - bar_width//2, screen_y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(screen, CORRUPTION_PINK, 
                        (screen_x - bar_width//2, screen_y - self.size - 10, 
                         int(bar_width * health_percent), bar_height))
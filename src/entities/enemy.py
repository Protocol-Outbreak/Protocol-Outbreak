import pygame
import math
import random
from src.utils.constants import *
from src.utils.enums import EnemyType
from src.entities.bullet import Bullet

class Enemy:
    def __init__(self, x, y, enemy_type, lvl):
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
        self.game_level = lvl
        
        # Aggro system
        self.is_aggroed = False
        self.aggro_range = 300  # Distance at which enemy notices player
        self.deaggro_range = 500  # Distance at which enemy loses interest

        # Boss-specific attributes
        self.is_boss = False
        self.shield_active = False
        self.shield_cooldown = 0
        self.shield_duration = 0
        self.spawn_cooldown = 0
        self.spawn_timer = 0
        self.can_spawn_enemies = False

        # Multi for health based on level
        diff_multi = 1 + (self.game_level * 0.1)
        
        # Set stats based on type
        if enemy_type == EnemyType.SQUARE_TURRET:
            self.health = 80 * diff_multi
            self.max_health = 80 * diff_multi
            self.speed = 0.5
            self.shoot_delay = 90
            self.xp_value = 15
            self.aggro_range = 350
        elif enemy_type == EnemyType.TRIANGLE_BLADE:
            self.health = 30 * diff_multi
            self.max_health = 30 * diff_multi
            self.speed = 3
            self.shoot_delay = 0  # Melee only
            self.xp_value = 25
            self.aggro_range = 250
        elif enemy_type == EnemyType.PENTAGON_GUNNER:
            self.health = 100 * diff_multi
            self.max_health = 100 * diff_multi
            self.speed = 1.5
            self.shoot_delay = 45
            self.xp_value = 50
            self.aggro_range = 400
            '''
        elif enemy_type == EnemyType.SNIPER:
            self.health = 60 * diff_multi
            self.max_health = 60 * diff_multi
            self.speed = 0  # Stationary
            self.shoot_delay = 120  # Slow fire rate
            self.xp_value = 30
            self.aggro_range = 700  # Very long sight range
            self.deaggro_range = 800
            self.size = 25
        elif enemy_type == EnemyType.BOSS:
            self.is_boss = True
            self.health = 500 * diff_multi
            self.max_health = 500 * diff_multi
            self.size = 90  # 3x bigger
            self.speed = 0.8  # Slower but still moves
            self.shoot_delay = 30  # Faster shooting
            self.xp_value = 200
            self.aggro_range = 600
            self.can_spawn_enemies = True
            self.spawn_cooldown = 600  # 10 seconds at 60fps
            self.spawn_timer = self.spawn_cooldown
            self.shield_cooldown = 420  # 7 seconds
            self.z_index = 100  # Draw boss on top
        '''
    
    def take_damage(self, damage):
        """Handle taking damage and trigger aggro"""
        # If shield is active, reduce damage
        if self.shield_active:
            damage *= 0.1  # Shield blocks 90% damage
        
        self.health -= damage
        self.is_aggroed = True  # Getting hit always aggros
    
    def update(self, player_x, player_y, bullets):
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check aggro status
        if not self.is_aggroed:
            if distance <= self.aggro_range:
                self.is_aggroed = True
        else:
            if distance > self.deaggro_range:
                self.is_aggroed = False
        
        # Boss shield mechanics
        if self.is_boss:
            self._update_boss_shield()
        
        # Only act if aggroed
        if self.is_aggroed and distance > 0:
            self.angle = math.atan2(dy, dx)
            
            # Movement based on type
            if self.type == EnemyType.TRIANGLE_BLADE:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            elif self.type == EnemyType.SQUARE_TURRET:
                if distance > 400:
                    self.x += (dx / distance) * self.speed * 0.3
                    self.y += (dy / distance) * self.speed * 0.3
            elif self.type == EnemyType.PENTAGON_GUNNER:
                if distance < 300:
                    self.x -= (dx / distance) * self.speed
                    self.y -= (dy / distance) * self.speed
                elif distance > 400:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed

            '''
            elif self.type == EnemyType.SNIPER:
                # Completely stationary - just aim
                pass
            elif self.type == EnemyType.BOSS:
                # Boss keeps medium distance
                if distance < 250:
                    self.x -= (dx / distance) * self.speed
                    self.y -= (dy / distance) * self.speed
                elif distance > 350:
                    self.x += (dx / distance) * self.speed
                    self.y += (dy / distance) * self.speed
            
            '''
            # Shooting
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0 and self.shoot_delay > 0:
                # Check range for shooting
                shoot_range = 800 #if self.type == EnemyType.SNIPER else 500
                if distance < shoot_range:
                    self.shoot(bullets)
                    self.shoot_cooldown = self.shoot_delay
        else:
            # Idle behavior
            self.angle += 0.02
    
    def _update_boss_shield(self):
        """Update boss shield mechanics"""
        # Update shield duration
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False
                self.shield_cooldown = 420  # 7 seconds cooldown
        
        # Update shield cooldown
        if not self.shield_active and self.shield_cooldown > 0:
            self.shield_cooldown -= 1
            if self.shield_cooldown <= 0:
                # Activate shield
                self.shield_active = True
                self.shield_duration = 180  # 3 seconds of shield
    
    def update_boss_spawning(self):
        """Check if boss should spawn enemies - called from game.py"""
        if not self.can_spawn_enemies or not self.is_aggroed:
            return None
        
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_cooldown
            # Return spawn positions around the boss
            spawn_positions = []
            for i in range(3):  # Spawn 3 enemies
                angle = random.random() * math.pi * 2
                distance = 100 + random.random() * 50
                spawn_x = self.x + math.cos(angle) * distance
                spawn_y = self.y + math.sin(angle) * distance
                spawn_positions.append((spawn_x, spawn_y))
            return spawn_positions
        return None
    
    def shoot(self, bullets):
        dmg_multi = 1 + (self.game_level * 0.1)
        
        if self.type == EnemyType.SQUARE_TURRET:
            bullets.append(Bullet(self.x, self.y, self.angle, 8, 10 * dmg_multi, 3, "enemy"))
        elif self.type == EnemyType.PENTAGON_GUNNER:
            # 5-way shot
            for i in range(5):
                angle_offset = (i - 2) * 0.3
                bullets.append(Bullet(self.x, self.y, self.angle + angle_offset, 7, 8 * dmg_multi, 2, "enemy"))
        '''
        elif self.type == EnemyType.SNIPER:
            # High damage, fast bullet
            bullets.append(Bullet(self.x, self.y, self.angle, 15, 25 * dmg_multi, 5, "enemy"))
        elif self.type == EnemyType.BOSS:
            # 5-way shot with bigger bullets
            for i in range(5):
                angle_offset = (i - 2) * 0.25
                bullet = Bullet(self.x, self.y, self.angle + angle_offset, 9, 15 * dmg_multi, 4, "enemy")
                bullet.radius = 10  # Bigger bullets
                bullets.append(bullet)
        '''
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw shield effect for boss
        if self.shield_active:
            pygame.draw.circle(screen, (100, 200, 255), (screen_x, screen_y), self.size + 10, 2)
            pygame.draw.circle(screen, (100, 200, 255, 50), (screen_x, screen_y), self.size + 8, 1)
        
        # Choose color based on aggro state and type
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
        elif self.type == EnemyType.PENTAGON_GUNNER or self.type == EnemyType.BOSS:
            if self.is_boss:
                color = (255, 50, 50) if self.is_aggroed else (200, 100, 0)
                thickness = 4
            else:
                color = (255, 100, 100) if self.is_aggroed else CORRUPTION_ORANGE
                thickness = 2
            
            points = []
            for i in range(5):
                angle = self.angle + (i * math.pi * 2 / 5)
                points.append((screen_x + math.cos(angle) * self.size,
                             screen_y + math.sin(angle) * self.size))
            pygame.draw.polygon(screen, color, points, thickness)
        '''
        elif self.type == EnemyType.SNIPER:
            color = (150, 0, 200) if self.is_aggroed else (100, 0, 150)
            # Draw octagon for sniper
            points = []
            for i in range(8):
                angle = self.angle + (i * math.pi * 2 / 8)
                points.append((screen_x + math.cos(angle) * self.size,
                             screen_y + math.sin(angle) * self.size))
            pygame.draw.polygon(screen, color, points, 2)
            
            # Draw sniper barrel
            barrel_length = self.size * 1.5
            barrel_end_x = screen_x + math.cos(self.angle) * barrel_length
            barrel_end_y = screen_y + math.sin(self.angle) * barrel_length
            pygame.draw.line(screen, color, (screen_x, screen_y), 
                           (barrel_end_x, barrel_end_y), 3)
        '''
        
        # Optional: Draw aggro range indicator (for debugging)
        if not self.is_aggroed:
            pygame.draw.circle(screen, (100, 100, 100), (screen_x, screen_y), self.aggro_range, 1)
        
        # Health bar
        bar_width = 40 if not self.is_boss else 80
        bar_height = 4 if not self.is_boss else 8
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, UI_GRAY, 
                        (screen_x - bar_width//2, screen_y - self.size - 15, bar_width, bar_height))
        
        # Health bar color changes for boss
        health_color = (255, 0, 0) if self.is_boss else CORRUPTION_PINK
        pygame.draw.rect(screen, health_color, 
                        (screen_x - bar_width//2, screen_y - self.size - 15, 
                         int(bar_width * health_percent), bar_height))
        
        # Boss name tag
        if self.is_boss:
            font = pygame.font.Font(None, 24)
            name_text = font.render("BOSS", True, (255, 50, 50))
            text_rect = name_text.get_rect(center=(screen_x, screen_y - self.size - 30))
            screen.blit(name_text, text_rect)
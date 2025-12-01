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
        
        # Visual enhancements
        self.rotation_angle = random.uniform(0, 360)  # Independent rotation
        self.scale_pulse = 0  # For breathing effect
        self.attack_telegraph_time = 0  # Glow before shooting
        
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
        # Update visual effects
        self.rotation_angle += 0.5  # Slow rotation for all enemies
        self.scale_pulse += 0.05  # Breathing animation
        
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
            
            # Attack telegraph - glow before shooting
            if self.shoot_cooldown > 0 and self.shoot_cooldown <= 20:
                self.attack_telegraph_time = self.shoot_cooldown
            else:
                self.attack_telegraph_time = 0
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
        
        # Breathing scale animation (95% to 105%)
        scale_factor = 1 + (math.sin(self.scale_pulse) * 0.05)
        current_size = int(self.size * scale_factor)
        
        # Attack telegraph - brighten and grow
        telegraph_scale = 1.0
        telegraph_brightness = 1.0
        if self.attack_telegraph_time > 0:
            telegraph_scale = 1.0 + (self.attack_telegraph_time / 20 * 0.15)  # Grow up to 15%
            telegraph_brightness = 1.0 + (self.attack_telegraph_time / 20 * 0.5)  # Brighten 50%
            current_size = int(current_size * telegraph_scale)
        
        # Draw shield effect for boss
        if self.shield_active:
            pygame.draw.circle(screen, (100, 200, 255), (screen_x, screen_y), current_size + 10, 2)
            pygame.draw.circle(screen, (100, 200, 255, 50), (screen_x, screen_y), current_size + 8, 1)
        
        # Choose color based on aggro state and type
        if self.type == EnemyType.SQUARE_TURRET:
            base_color = CORRUPTION_PINK if self.is_aggroed else CLEAN_BLUE
            # Apply telegraph brightness
            color = tuple(min(255, int(c * telegraph_brightness)) for c in base_color)
            # Use rotation_angle for consistent rotation
            rect_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(rect_surface, color, 
                           (current_size//2, current_size//2, current_size, current_size), 2)
            rotated_rect = pygame.transform.rotate(rect_surface, self.rotation_angle)
            rect_rect = rotated_rect.get_rect(center=(screen_x, screen_y))
            screen.blit(rotated_rect, rect_rect)
            
        elif self.type == EnemyType.TRIANGLE_BLADE:
            base_color = CORRUPTION_ORANGE if self.is_aggroed else CORRUPTION_PINK
            color = tuple(min(255, int(c * telegraph_brightness)) for c in base_color)
            # Triangle points at cursor when aggroed, rotates when idle
            angle = self.angle if self.is_aggroed else math.radians(self.rotation_angle)
            points = [
                (screen_x + math.cos(angle) * current_size, 
                 screen_y + math.sin(angle) * current_size),
                (screen_x + math.cos(angle + 2.4) * current_size, 
                 screen_y + math.sin(angle + 2.4) * current_size),
                (screen_x + math.cos(angle - 2.4) * current_size, 
                 screen_y + math.sin(angle - 2.4) * current_size)
            ]
            pygame.draw.polygon(screen, color, points, 2)
            
        elif self.type == EnemyType.PENTAGON_GUNNER or self.type == EnemyType.BOSS:
            if self.is_boss:
                base_color = (255, 50, 50) if self.is_aggroed else (200, 100, 0)
                thickness = 4
            else:
                base_color = (255, 100, 100) if self.is_aggroed else CORRUPTION_ORANGE
                thickness = 2
            
            color = tuple(min(255, int(c * telegraph_brightness)) for c in base_color)
            
            # Pentagon rotates continuously
            points = []
            for i in range(5):
                angle = math.radians(self.rotation_angle) + (i * math.pi * 2 / 5)
                points.append((screen_x + math.cos(angle) * current_size,
                             screen_y + math.sin(angle) * current_size))
            pygame.draw.polygon(screen, color, points, thickness)
            
            # Draw inner spinning geometry for gunners when attacking
            if self.attack_telegraph_time > 0 and not self.is_boss:
                inner_points = []
                for i in range(5):
                    angle = math.radians(-self.rotation_angle * 2) + (i * math.pi * 2 / 5)
                    inner_points.append((screen_x + math.cos(angle) * current_size * 0.5,
                                       screen_y + math.sin(angle) * current_size * 0.5))
                pygame.draw.polygon(screen, color, inner_points, 1)
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
import pygame
import math
from src.utils.constants import *
from src.utils.enums import *
from src.entities.bullet import Bullet

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.tank_type = TankType.BASIC
        self.z_index = 100  # Layer: Player drawn on top of enemies and bullets
        
        # Stats (0-7 points each)
        self.stats = {
            'health_regen': 3,
            'max_health': 2,
            'body_damage': 0,
            'bullet_speed': 5,
            'bullet_penetration': 6,
            'bullet_damage': 5,
            'reload': 5,
            'movement_speed': 2
        }
        
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.skill_points = 0
        
        # Health
        self.max_hp = 100 + (self.stats['max_health'] * 20)
        self.hp = self.max_hp
        self.last_damage_time = 0
        
        # Movement
        self.base_speed = 3
        self.speed = self.base_speed + (self.stats['movement_speed'] * 0.5)
        
        # Shooting
        self.shoot_cooldown = 0
        self.base_reload = 60
        
        self.size = 35
        
    def get_reload_speed(self):
        return max(5, self.base_reload - (self.stats['reload'] * 2))
    
    def update(self, keys, mouse_pos, camera_x, camera_y):
        # Movement
        dx = 0
        dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Aim towards mouse
        screen_mouse_x, screen_mouse_y = mouse_pos
        world_mouse_x = screen_mouse_x + camera_x
        world_mouse_y = screen_mouse_y + camera_y
        self.angle = math.atan2(world_mouse_y - self.y, world_mouse_x - self.x)
        
        # Decrease cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Health regeneration (simplified)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > 5000:  # 5 seconds no damage
            regen_amount = 0.5 + (self.stats['health_regen'] * 0.3)
            self.hp = min(self.max_hp, self.hp + regen_amount)
    
    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            bullet_speed = 10 + (self.stats['bullet_speed'] * 1.5)
            bullet_damage = 10 + (self.stats['bullet_damage'] * 3)
            bullet_pen = self.stats['bullet_penetration']
            
            if self.tank_type == TankType.BASIC:
                # Single shot
                offset = 30
                bullet_x = self.x + math.cos(self.angle) * offset
                bullet_y = self.y + math.sin(self.angle) * offset
                bullets.append(Bullet(bullet_x, bullet_y, self.angle, 
                                    bullet_speed, bullet_damage, bullet_pen, "player"))
            elif self.tank_type == TankType.TWIN:
                # Twin shots
                offset = 30
                spread = 10
                for i in [-1, 1]:
                    bullet_x = self.x + math.cos(self.angle) * offset + math.cos(self.angle + math.pi/2) * spread * i
                    bullet_y = self.y + math.sin(self.angle) * offset + math.sin(self.angle + math.pi/2) * spread * i
                    bullets.append(Bullet(bullet_x, bullet_y, self.angle, 
                                        bullet_speed, bullet_damage * 0.8, bullet_pen, "player"))
            
            self.shoot_cooldown = self.get_reload_speed()
    
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.2)
        
        # Award skill point (simplified - should follow diep.io rules)
        if self.level <= 28:
            self.skill_points += 1
        elif self.level == 30:
            self.skill_points += 1
        elif self.level > 30 and (self.level - 30) % 3 == 0:
            self.skill_points += 1
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # LAYERING SYSTEM:
        # Layer 1: Cannons (drawn first, appear behind)
        # Layer 2: Tank body outline (middle)
        # Layer 3: Tank body fill (on top)
        
        cannon_length = 40
        cannon_width = 12
        cannon_color = GREY  # Custom cannon color - change this to whatever you want!
        
        # === LAYER 1: DRAW CANNONS FIRST (BEHIND BODY) ===
        if self.tank_type == TankType.BASIC:
            end_x = screen_x + math.cos(self.angle) * cannon_length
            end_y = screen_y + math.sin(self.angle) * cannon_length
            
            # Draw cannon rectangle
            perp_angle = self.angle + math.pi / 2
            points = [
                (screen_x + math.cos(perp_angle) * cannon_width/2,
                 screen_y + math.sin(perp_angle) * cannon_width/2),
                (screen_x - math.cos(perp_angle) * cannon_width/2,
                 screen_y - math.sin(perp_angle) * cannon_width/2),
                (end_x - math.cos(perp_angle) * cannon_width/2,
                 end_y - math.sin(perp_angle) * cannon_width/2),
                (end_x + math.cos(perp_angle) * cannon_width/2,
                 end_y + math.sin(perp_angle) * cannon_width/2)
            ]
            pygame.draw.polygon(screen, cannon_color, points)
            # Optional: Add cannon outline
            pygame.draw.polygon(screen, CLEAN_BLUE, points, 2)
        
        elif self.tank_type == TankType.TWIN:
            # Twin cannons
            spread = 10
            for i in [-1, 1]:
                offset_x = screen_x + math.cos(self.angle + math.pi/2) * spread * i
                offset_y = screen_y + math.sin(self.angle + math.pi/2) * spread * i
                end_x = offset_x + math.cos(self.angle) * cannon_length
                end_y = offset_y + math.sin(self.angle) * cannon_length
                
                perp_angle = self.angle + math.pi / 2
                points = [
                    (offset_x + math.cos(perp_angle) * cannon_width/2,
                     offset_y + math.sin(perp_angle) * cannon_width/2),
                    (offset_x - math.cos(perp_angle) * cannon_width/2,
                     offset_y - math.sin(perp_angle) * cannon_width/2),
                    (end_x - math.cos(perp_angle) * cannon_width/2,
                     end_y - math.sin(perp_angle) * cannon_width/2),
                    (end_x + math.cos(perp_angle) * cannon_width/2,
                     end_y + math.sin(perp_angle) * cannon_width/2)
                ]
                pygame.draw.polygon(screen, cannon_color, points)
                # Optional: Add cannon outline
                #pygame.draw.polygon(screen, CLEAN_BLUE, points, 2)
        
        # === LAYER 2: DRAW TANK BODY (ON TOP OF CANNONS) ===
        # Draw filled circle (body interior)
        pygame.draw.circle(screen, (20, 40, 80), (screen_x, screen_y), self.size - 8)
        
        # === LAYER 3: DRAW TANK OUTLINE (TOP LAYER) ===
        # Draw outline circle
        #pygame.draw.circle(screen, CLEAN_BLUE, (screen_x, screen_y), self.size, 3)

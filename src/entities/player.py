import pygame
import math
from src.utils.constants import *
from src.utils.enums import *
from src.entities.bullet import Bullet
from src.systems.tank_renderer import TankRenderer
from src.systems.attack_system import ShootingSystem



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
            'reload': 7,
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
        self.base_reload = 40 # this is for the reload speed
        
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
        ShootingSystem.shoot(self, bullets)
    
    def gain_xp(self, amount):
        print("gained xp", amount)
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1) # makes leveling up more difficult
        
        # Award skill point (simplified - should follow diep.io rules)
        self.skill_points += 1
        if self.level == 2:
            self.tank_type = TankType.TWIN
            #self.skill_points += 1
        elif self.level == 3:
            self.tank_type = TankType.TWIN
        elif self.level == 4:
            self.tank_type = TankType.TRIPLET
        elif self.level == 5:
            self.tank_type = TankType.QUAD
        elif self.level == 6:
            self.tank_type = TankType.OCTO
        elif self.level == 7:
            self.tank_type = TankType.PENTA_SHOT
        elif self.level == 8:
            self.tank_type = TankType.SNIPER
        elif self.level == 9:
            self.tank_type = TankType.MACHINE_GUN
        
            #self.skill_points += 1
        #elif self.level > 4 and (self.level - 30) % 3 == 0:
            #self.skill_points += 1
    
    def draw(self, screen, camera_x, camera_y):
        TankRenderer.draw_tank(screen, self, camera_x, camera_y)
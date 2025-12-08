import pygame
import math
from src.utils.constants import *
from src.utils.enums import *
from src.entities.bullet import Bullet
from src.systems.tank_renderer import TankRenderer
from src.systems.attack_system import ShootingSystem
from src.configs.tank_configs import TANK_CONFIGS
from src.utils.enums import TankType, TankPath



class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.tank_type = TankType.BASIC
        self.z_index = 100  # Layer: Player drawn on top of enemies and bullets
        
        # Stats (0-7 points each)
        self.stats = {
            'health_regen': 0,
            'max_health': 0,
            'body_damage': 0,
            'bullet_speed': 0,
            'bullet_penetration': 0,
            'bullet_damage': 0,
            'reload': 0,
            'movement_speed': 0
        }
        
        self.level = 4
        self.xp = 0
        self.xp_to_next_level = 100
        self.skill_points = 0
        
        # Tank Default
        self.chosen_path = TankPath.NONE  # No path chosen yet
        self.path_locked = False  # Has player locked in their choice?
    
        # Track available tanks in chosen path
        self.available_tanks_in_path = [TankType.BASIC]  # Start with basic

        tank_default = TANK_CONFIGS.get(self.tank_type.name)

        
        # Health
        self.max_hp = 100 + (self.stats['max_health'] * 20)
        self.hp = self.max_hp
        self.last_damage_time = 0
        self.dmg_color = (255, 0, 0) # Red color for when damage is taken
        
        # Invulnerability Shield (3 second protection when level starts)
        self.invulnerable = False
        self.invulnerability_end_time = 0
        
        # Movement
        self.base_speed = 3
        self.speed = self.base_speed + (self.stats['movement_speed'] * 0.5)
        
        # Shooting
        self.shoot_cooldown = 0
        self.base_reload = 40 * tank_default['reload_speed'] # set tank reload to the base of current tank type
         
        self.size = 35
    
    def activate_invulnerability(self, duration=3.0):
        """Activate invulnerability shield for specified duration (in seconds)"""
        self.invulnerable = True
        self.invulnerability_end_time = pygame.time.get_ticks() + (duration * 1000)
    
    def update_invulnerability(self):
        """Update invulnerability status - call this in update() method"""
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time >= self.invulnerability_end_time:
                self.invulnerable = False
    
    def get_reload_speed(self):
        return max(5, self.base_reload - (self.stats['reload'] * 2))
    
    def update(self, keys, mouse_pos, camera_x, camera_y):
        # Update invulnerability status
        self.update_invulnerability()
        
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
            regen_amount = 0.5 + ((self.stats['health_regen'] + 1) * 0.3)
            self.hp = min(self.max_hp, self.hp + regen_amount)
    
    def shoot(self, bullets, sound_manager=None):
        # Only play sound if we're actually shooting (cooldown is 0)
        if self.shoot_cooldown == 0 and sound_manager:
            sound_manager.play_sound('shoot', volume_multiplier=0.3)
        
        # Create bullets (ShootingSystem checks cooldown internally)
        ShootingSystem.shoot(self, bullets)
    
    def gain_xp(self, amount, game=None):
        self.xp += amount # currently buffed amount of xp earned for testing purposes
        if self.xp >= self.xp_to_next_level:
            self.level_up(game)

    def take_damage(self, amount, sound_manager=None):
        self.hp -= amount
        # Play hit sound
        if sound_manager:
            sound_manager.play_sound('player_hit', volume_multiplier=0.7)
    
    def level_up(self, game=None):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1) # makes leveling up more difficult
        
        # Award skill point (simplified - should follow diep.io rules)
        self.skill_points += 1
        
        # Show skill point notification
        if game and hasattr(game, 'notification_manager'):
            game.notification_manager.add_notification(
                "You unlocked a Skill Point!",
                x=SCREEN_WIDTH // 2,
                y=200,
                duration=3.0,
                font_size=36,
                color=(100, 255, 100)
            )
        
        if self.level in [15, 25]:
            game.check_for_auto_upgrade()
    
    def draw(self, screen, camera_x, camera_y):
        TankRenderer.draw_tank(screen, self, camera_x, camera_y)
    

    # Add this new method to Player class:
    def choose_path(self, path):
        """
        Lock in a tank path choice
        """
        if self.path_locked:
            return False  # Already chose
        
        self.chosen_path = path
        self.path_locked = True
        
        # Set available tanks for this path
        if path == TankPath.GUNNER:
            self.available_tanks_in_path = [TankType.TWIN, TankType.TRIPLET, TankType.PENTA_SHOT]
        elif path == TankPath.SNIPER:
            self.available_tanks_in_path = [TankType.SNIPER, TankType.MARKSMAN, TankType.RAILGUN]
        elif path == TankPath.SPRAYER:
            self.available_tanks_in_path = [TankType.MACHINE_GUN, TankType.GATLING, TankType.MINIGUN]
        
        return True

    def can_use_tank(self, tank_type):
        """Check if player can use this tank type"""
        if not self.path_locked:
            return tank_type == TankType.BASIC
        
        return tank_type in self.available_tanks_in_path

    def get_current_path_tank_for_level(self):
        """Get the tank player should have based on their level and path"""
        if not self.path_locked:
            return TankType.BASIC
        
        # Map paths to progressions
        progressions = {
            TankPath.GUNNER: {5: TankType.TWIN, 15: TankType.TRIPLET, 25: TankType.PENTA_SHOT},
            TankPath.SNIPER: {5: TankType.SNIPER, 15: TankType.MARKSMAN, 25: TankType.RAILGUN},
            TankPath.SPRAYER: {5: TankType.MACHINE_GUN, 15: TankType.GATLING, 25: TankType.MINIGUN}
        }
        
        if self.chosen_path not in progressions:
            return TankType.BASIC
        
        progression = progressions[self.chosen_path]
        
        # Find highest tier player has unlocked
        available_levels = [lvl for lvl in progression.keys() if lvl <= self.level]
        if not available_levels:
            return TankType.BASIC
        
        highest_level = max(available_levels)
        return progression[highest_level]
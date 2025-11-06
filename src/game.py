
import pygame
import random
import math

from src.entities.player import Player
from src.entities.enemy import Enemy
#from src.levels.level_manager import LevelManager
#from src.ui.hud import HUD
from src.utils.constants import *
from src.utils.enums import *



class Game:
    def __init__(self, width, height, fps):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Nano Drone Combat")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game world
        self.world_width = 3000
        self.world_height = 3000
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Game objects
        self.player = Player(self.world_width // 2, self.world_height // 2)
        self.bullets = []
        self.enemies = []
        
        # Spawn initial enemies
        self.spawn_enemies(5)
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def spawn_enemies(self, count):
        for _ in range(count):
            # Spawn away from player
            while True:
                x = random.randint(100, self.world_width - 100)
                y = random.randint(100, self.world_height - 100)
                dist = math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2)
                if dist > 400:
                    break
            
            enemy_type = random.choice(list(EnemyType))
            self.enemies.append(Enemy(x, y, enemy_type))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_1:
                    self.player.tank_type = TankType.BASIC
                elif event.key == pygame.K_2:
                    self.player.tank_type = TankType.TWIN
    
    def update(self):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Update player
        self.player.update(keys, mouse_pos, self.camera_x, self.camera_y)
        
        # Shooting
        if mouse_buttons[0]:  # Left click
            self.player.shoot(self.bullets)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen(self.camera_x, self.camera_y) or bullet.health <= 0:
                self.bullets.remove(bullet)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y, self.bullets)
        
        # Collision detection: bullets vs enemies
        for bullet in self.bullets[:]:
            if bullet.owner_type == "player":
                for enemy in self.enemies[:]:
                    dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if dist < enemy.size:
                        enemy.health -= bullet.damage
                        bullet.health -= 20
                        
                        if enemy.health <= 0:
                            self.player.gain_xp(enemy.xp_value)
                            self.enemies.remove(enemy)
                            # Spawn new enemy
                            self.spawn_enemies(1)
                        
                        if bullet.health <= 0 and bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
        
        # Collision detection: enemy bullets vs player
        for bullet in self.bullets[:]:
            if bullet.owner_type == "enemy":
                dist = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
                if dist < self.player.size:
                    self.player.hp -= bullet.damage
                    self.player.last_damage_time = pygame.time.get_ticks()
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if self.player.hp <= 0:
                        self.player.hp = 0
                        # Game over (simplified - just reset)
                        self.player.hp = self.player.max_hp
                        self.player.x = self.world_width // 2
                        self.player.y = self.world_height // 2
        
        # Update camera (follow player)
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        
        # Clamp camera to world bounds
        self.camera_x = max(0, min(self.camera_x, self.world_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.world_height - SCREEN_HEIGHT))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        grid_size = 50
        for x in range(0, self.world_width, grid_size):
            screen_x = x - self.camera_x
            if -grid_size < screen_x < SCREEN_WIDTH + grid_size:
                pygame.draw.line(self.screen, (20, 40, 60), 
                               (screen_x, 0), (screen_x, SCREEN_HEIGHT))
        
        for y in range(0, self.world_height, grid_size):
            screen_y = y - self.camera_y
            if -grid_size < screen_y < SCREEN_HEIGHT + grid_size:
                pygame.draw.line(self.screen, (20, 40, 60), 
                               (0, screen_y), (SCREEN_WIDTH, screen_y))
        
        # === Z-LAYER SYSTEM ===
        # Collect all drawable entities
        all_entities = []
        all_entities.extend(self.bullets)
        all_entities.extend(self.enemies)
        all_entities.append(self.player)
        
        # Sort by z_index (lower values drawn first/behind)
        sorted_entities = sorted(all_entities, key=lambda e: e.z_index)
        
        # Draw all entities in sorted order
        for entity in sorted_entities:
            entity.draw(self.screen, self.camera_x, self.camera_y)
        
        # Draw UI (always on top, no z_index needed)
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Health bar
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 80
        bar_width = 300
        bar_height = 20
        
        pygame.draw.rect(self.screen, UI_GRAY, (bar_x, bar_y, bar_width, bar_height))
        health_percent = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, CLEAN_BLUE, 
                        (bar_x, bar_y, int(bar_width * health_percent), bar_height))
        
        health_text = self.font.render(f"HP: {int(self.player.hp)}/{self.player.max_hp}", 
                                       True, WHITE)
        self.screen.blit(health_text, (bar_x + 5, bar_y + 2))
        
        # XP bar
        xp_bar_y = bar_y + 30
        pygame.draw.rect(self.screen, UI_GRAY, (bar_x, xp_bar_y, bar_width, 15))
        xp_percent = self.player.xp / self.player.xp_to_next_level
        pygame.draw.rect(self.screen, CORRUPTION_PURPLE, 
                        (bar_x, xp_bar_y, int(bar_width * xp_percent), 15))
        
        xp_text = self.small_font.render(f"Level {self.player.level} - {self.player.xp}/{self.player.xp_to_next_level} XP", 
                                         True, WHITE)
        self.screen.blit(xp_text, (bar_x + 5, xp_bar_y + 1))
        
        # Stats display (top right)
        stats_x = SCREEN_WIDTH - 200
        stats_y = 20
        stats_text = [
            f"Level: {self.player.level}",
            f"Skill Points: {self.player.skill_points}",
            f"Tank: {self.player.tank_type.name}",
            f"Enemies: {len(self.enemies)}"
        ]
        
        for i, text in enumerate(stats_text):
            rendered = self.small_font.render(text, True, UI_CYAN)
            self.screen.blit(rendered, (stats_x, stats_y + i * 20))
        
        # Controls (bottom right)
        controls_x = SCREEN_WIDTH - 250
        controls_y = SCREEN_HEIGHT - 100
        controls = [
            "WASD/Arrows: Move",
            "Mouse: Aim",
            "Left Click: Shoot",
            "1/2: Change Tank"
        ]
        
        for i, text in enumerate(controls):
            rendered = self.small_font.render(text, True, (100, 150, 200))
            self.screen.blit(rendered, (controls_x, controls_y + i * 18))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
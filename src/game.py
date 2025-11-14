import pygame
import random
import math

from src.ui.game_over import GameOverScreen
from src.entities.player import Player
from src.entities.enemy import Enemy
#from src.levels.level_manager import LevelManager
#from src.ui.hud import HUD
from src.utils.constants import *
from src.utils.enums import *
from src.ui.stat_upgrade_ui import StatUpgradeUI
from src.entities.wall import Wall
from src.systems.collisions import CollisionSystem
from src.levels.map_generator import MapGenerator
from src.ui.level_transition import LevelTransition
from src.ui.level_progress_ui import LevelProgressUI
from src.ui.minimap import Minimap


class Game:
    def __init__(self, width, height, fps):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Nano Drone Combat")
        self.clock = pygame.time.Clock()
        self.running = True

        # Level Manangment
        self.current_level_number = 0
        self.level_name = 'Tutorial'

        # Game world
        self.walls = []
        self.world_width = 3000
        self.world_height = 3000
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Game objects
        self.player = Player(self.world_width // 2, self.world_height // 2)
        self.bullets = []
        self.enemies = []

        # Enemies
        self.enemy_spawn_points = []

        # Boss Fight implementation
        self.has_boss = False
        self.boss_enemy = None

        # Collisions system
        self.collision_system = CollisionSystem() if 'CollisionSystem' in dir() else None
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.stat_ui = StatUpgradeUI() #Ui representing stat points upgrade
        self.level_progress_ui = LevelProgressUI()
        self.minimap = Minimap(self.world_width, self.world_height)

        # Level progress
        self.initial_enemy_count = 0
        self.level_complete = False
        self.next_level_button_rect = None

        # Load first level
        self.load_level(0)


        # Spawn initial enemies
        #self.spawn_enemies(5)
        


    def load_level(self, level_number):
        """Load a level by number"""
        print(f"\n{'='*60}")
        print(f"Loading Level {level_number}...")
        print(f"{'='*60}")
        
        # Generate map from JSON
        map_result = MapGenerator.generate_map_from_json(level_number)
        
        if map_result:
            # Update walls
            self.walls = map_result['walls']
            print(len(map_result['walls']))
            self.enemy_barriers = map_result.get('barriers', [])
            
            # Update world size
            self.world_width, self.world_height = map_result['map_size']
            
            # Update level info
            self.current_level_number = level_number
            self.level_name = map_result['level_name']

            # Get spawn points from map
            self.player_spawn_point = map_result['player_spawn']
            self.enemy_spawn_points = map_result.get('enemy_spawns', [])
            
            # Respawn player at center
            spawn_x, spawn_y = self.player_spawn_point
            self.player.x = spawn_x
            self.player.y = spawn_y
            if hasattr(self.player, 'rect'):
                self.player.rect.center = (spawn_x, spawn_y)
            
            # Clear existing entities
            self.enemies.clear()
            self.bullets.clear()

            # Spawn enemies
            self.spawn_enemies(self.current_level_number)

            # Track initial enemy count for progress bar
            self.initial_enemy_count = len(self.enemies)
            self.level_complete = False
            
            # Update minimap world size
            self.minimap.world_width = self.world_width
            self.minimap.world_height = self.world_height
            
            print(f"✅ Level loaded successfully!")
            print(f"   Name: {self.level_name}")
            print(f"   Walls: {len(self.walls)}")
            print(f"   World size: {self.world_width}x{self.world_height}")
            print(f"   Spawn point: ({spawn_x}, {spawn_y})")
            print(f"{'='*60}\n")
        else:
            print(f"❌ Failed to load level {level_number}, using empty map")
            self.walls = []
    
    def spawn_enemies(self, current_lvl): # Difficulty
        spawn_points = self.enemy_spawn_points
        for i in range(len(spawn_points)):
            spawn_x, spawn_y = spawn_points[i]
            enemy_type = random.choice(list(EnemyType)) # change this to choose what enemy type is
            self.enemies.append(Enemy(spawn_x, spawn_y, enemy_type, current_lvl))

        '''
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
        '''
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:  # ADD THIS
                    self.minimap.toggle()
                elif event.key == pygame.K_1:
                    self.player.tank_type = TankType.BASIC
                elif event.key == pygame.K_2 and self.player.level >= 3:
                    self.player.tank_type = TankType.TWIN
                elif event.key == pygame.K_3 and self.player.level >= 6:
                    self.player.tank_type = TankType.TRIPLET
                elif event.key == pygame.K_4 and self.player.level >= 9:
                    self.player.tank_type = TankType.QUAD
                elif event.key == pygame.K_5 and self.player.level >= 12:
                    self.player.tank_type = TankType.OCTO
                elif event.key == pygame.K_6 and self.player.level >= 15:
                    self.player.tank_type = TankType.PENTA_SHOT
                elif event.key == pygame.K_7 and self.player.level >= 18:
                    self.player.tank_type = TankType.SNIPER
                elif event.key == pygame.K_8 and self.player.level >= 21:
                    self.player.tank_type = TankType.MACHINE_GUN
                elif event.key == pygame.K_c:  # Press 'C' to clear all enemies for testing purposes
                    self.enemies.clear() 


                elif event.key == pygame.K_k:
                    self.stat_ui.toggle_visibility()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.stat_ui.handle_click(event.pos, self.player):
                        pass
                    elif self.level_complete and self.level_progress_ui.check_button_click(event.pos):
                            self.proceed_to_next_level()

# Level Progression

    def proceed_to_next_level(self):
        """Handle transition to next level"""
        next_level = self.current_level_number + 1
        
        # Show transition screen
        transition = LevelTransition(self.current_level_number, next_level)
        if transition.show(self.screen):
            # Load next level
            self.load_level(next_level)
        else:
            # User closed window during transition
            self.running = False
    
# ========== COLLISION DETECTION METHODS ==========
    
    def handle_player_wall_collision(self, old_x, old_y):
        """Check and resolve player collision with walls"""
        if hasattr(self.player, 'rect'):
            player_rect = self.player.rect
        else:
            player_rect = pygame.Rect(
                self.player.x - self.player.size,
                self.player.y - self.player.size,
                self.player.size * 2,
                self.player.size * 2
            )
        
        for wall in self.walls:
            if wall.collides_with(player_rect):
                self.player.x = old_x
                self.player.y = old_y
                if hasattr(self.player, 'rect'):
                    self.player.rect.center = (old_x, old_y)
                return True
        return False
    
    def handle_enemy_collisions(self, enemy_old_positions):
        """Handle all enemy collision detection"""
        for i, enemy in enumerate(self.enemies[:]):
            enemy_old_x, enemy_old_y = enemy_old_positions[i]
            
            # Create enemy rect
            if hasattr(enemy, 'rect'):
                enemy_rect = enemy.rect
            else:
                enemy_rect = pygame.Rect(
                    enemy.x - enemy.size,
                    enemy.y - enemy.size,
                    enemy.size * 2,
                    enemy.size * 2
                )
            
            # Check wall collision
            wall_collision = self._check_enemy_wall_collision(enemy, enemy_rect, enemy_old_x, enemy_old_y)
            
            # Check player collision (only if not colliding with wall)
            if not wall_collision:
                self._check_enemy_player_collision(enemy)
        
        # Check enemy-enemy collisions
        self._check_enemy_enemy_collisions()
    
    def _check_enemy_wall_collision(self, enemy, enemy_rect, old_x, old_y):
        """Check if enemy collides with walls and revert position if so"""
        for wall in self.walls:
            if wall.collides_with(enemy_rect):
                enemy.x = old_x
                enemy.y = old_y
                if hasattr(enemy, 'rect'):
                    enemy.rect.center = (old_x, old_y)
                return True
        return False
    
    def _check_enemy_player_collision(self, enemy):
        """Check and resolve enemy-player collision with contact damage"""
        dist_to_player = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
        collision_distance = enemy.size + self.player.size
        
        if dist_to_player < collision_distance and dist_to_player > 0:
            # Calculate push direction
            dx = (enemy.x - self.player.x) / dist_to_player
            dy = (enemy.y - self.player.y) / dist_to_player
            
            # Push enemy away
            overlap = collision_distance - dist_to_player
            enemy.x += dx * overlap
            enemy.y += dy * overlap
            
            if hasattr(enemy, 'rect'):
                enemy.rect.center = (enemy.x, enemy.y)

            # Dmg multi based on level
            dmg_multi = 1 + (self.current_level_number * 0.1)
            
            # Deal contact damage
            current_time = pygame.time.get_ticks()
            if not hasattr(enemy, 'last_contact_damage') or current_time - enemy.last_contact_damage > 1000:
                self.player.hp -= 5 * dmg_multi
                self.player.last_damage_time = current_time
                enemy.last_contact_damage = current_time           
                if self.player.hp <= 0:
                    return self._handle_player_death()
    
    def _check_enemy_enemy_collisions(self):
        """Prevent enemies from stacking on each other"""
        for i, enemy1 in enumerate(self.enemies):
            for enemy2 in self.enemies[i+1:]:
                dx = enemy2.x - enemy1.x
                dy = enemy2.y - enemy1.y
                dist = math.sqrt(dx**2 + dy**2)
                min_dist = enemy1.size + enemy2.size
                
                if dist < min_dist and dist > 0:
                    # Push enemies apart
                    overlap = min_dist - dist
                    push_x = (dx / dist) * overlap * 0.5
                    push_y = (dy / dist) * overlap * 0.5
                    
                    enemy1.x -= push_x
                    enemy1.y -= push_y
                    enemy2.x += push_x
                    enemy2.y += push_y
                    
                    if hasattr(enemy1, 'rect'):
                        enemy1.rect.center = (enemy1.x, enemy1.y)
                    if hasattr(enemy2, 'rect'):
                        enemy2.rect.center = (enemy2.x, enemy2.y)
    
    def handle_bullet_collisions(self):
        """Handle all bullet collision detection"""
        self._check_player_bullets_vs_enemies()
        result = self._check_enemy_bullets_vs_player()
        return result
    
    def _check_player_bullets_vs_enemies(self):
        """Check player bullets hitting enemies"""
        for bullet in self.bullets[:]:
            if bullet.owner_type == "player":
                for enemy in self.enemies[:]:
                    dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if dist < enemy.size:
                        enemy.take_damage(bullet.damage)
                        bullet.health -= 20
                        
                        if enemy.health <= 0:
                            self.player.gain_xp(enemy.xp_value)
                            self.enemies.remove(enemy)
                        
                        if bullet.health <= 0 and bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
    
    def _check_enemy_bullets_vs_player(self):
        """Check enemy bullets hitting player"""
        for bullet in self.bullets[:]:
            if bullet.owner_type == "enemy":
                dist = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
                if dist < self.player.size:
                    dmg_multi = 1 + (self.current_level_number * 0.1)
                    self.player.hp -= bullet.damage * dmg_multi
                    self.player.last_damage_time = pygame.time.get_ticks()
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if self.player.hp <= 0:
                        return self._handle_player_death()
        return None
    
    def handle_bullet_wall_collisions(self):
        """Check if bullets hit walls and remove them"""
        for bullet in self.bullets[:]:
            # Create bullet rect for collision
            bullet_rect = pygame.Rect(
                bullet.x - bullet.radius,
                bullet.y - bullet.radius,
                bullet.radius * 2,
                bullet.radius * 2
            )
            
            # Check collision with walls
            for wall in self.walls:
                if wall.collides_with(bullet_rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
    
    def _handle_player_death(self):
        """Handle player death and game over screen"""
        print('trying to attempt')
        self.player.hp = 0
        game_over = GameOverScreen(score=(self.player.level - 1) * 100)
        result = game_over.run()
        
        if result == 'retry':
            self.player.hp = self.player.max_hp
            x,y = self.player_spawn_point
            self.player.x = x
            self.player.y = y
            # These comments allow for the level, xp, and skill points to be saved after every point
            #self.player.level = 1
            #self.player.xp = 0
            #self.player.skill_points = 0
            self.enemies.clear()
            self.bullets.clear()
            self.spawn_enemies(self.current_level_number)
        elif result == 'menu':
            self.running = False
            return 'menu'
        else:
            self.running = False
        return None
    
    # ========== MAIN UPDATE METHOD ==========
    
    def update(self):
        """Main game update loop - coordinates all game systems"""
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Store player's old position
        old_x = self.player.x
        old_y = self.player.y
            
        # Update player movement
        self.player.update(keys, mouse_pos, self.camera_x, self.camera_y)
        
        # Handle player-wall collision
        self.handle_player_wall_collision(old_x, old_y)
        
        # Handle shooting
        if mouse_buttons[0] or keys[pygame.K_SPACE]:
            self.player.shoot(self.bullets)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen(self.camera_x, self.camera_y) or bullet.health <= 0:
                self.bullets.remove(bullet)
        self.handle_bullet_wall_collisions()
                
        # Save old enemy positions
        enemy_old_positions = [(enemy.x, enemy.y) for enemy in self.enemies]

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y, self.bullets)
        
        # Handle all collision detection
        self.handle_enemy_collisions(enemy_old_positions)
        result = self.handle_bullet_collisions()
        if result == 'menu':
            return 'menu'

        # Check if level is complete
        if len(self.enemies) == 0 and self.initial_enemy_count > 0 and not self.level_complete:
            self.level_complete = True
        
        # Update camera
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

        # == Draw Walls == #
        for wall in self.walls:
            wall.draw(self.screen, (self.camera_x, self.camera_y))
        
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
        # Enemy progress bar
        self.level_progress_ui.draw_enemy_progress_bar(
            self.screen, 
            len(self.enemies), 
            self.initial_enemy_count, 
            self.level_complete
        )

        # Level Complete Button
        if self.level_complete:
            self.level_progress_ui.draw_next_level_button(self.screen)
        

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
        controls_y = SCREEN_HEIGHT - 120
        controls = [
            "WASD/Arrows: Move",
            "Mouse: Aim",
            "Left Click/Space: Shoot",
            "1/2: Change Tank",
            "k: to toggle stats upgrade"
        ]
        
        for i, text in enumerate(controls):
            rendered = self.small_font.render(text, True, (100, 150, 200))
            self.screen.blit(rendered, (controls_x, controls_y + i * 18))

        # Draw the stat upgrade
        self.stat_ui.draw(self.screen, self.player)

        # Draw minimap (add at the end of draw_ui)
        self.minimap.draw(self.screen, self.player, self.enemies, self.walls)
    
    def run(self):
        while self.running:
            self.handle_events()
            result = self.update()  # Capture the return value from update()
            if result == 'menu':
                return 'menu'  # Pass it back to main.py
            self.draw()
            self.clock.tick(FPS)
        
        return None  # Return None if game exits normally
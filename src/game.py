import pygame
import random
import math

from src.ui.game_over import GameOverScreen
from src.ui.game_won import GameWonScreen
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
from src.entities.particle import ParticleSystem
from src.ui.notification import NotificationManager
from src.ui.victory_screen import VictoryScreen
from src.ui.path_selection_ui import PathSelectionUI
from src.utils.enums import TankPath


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
        self.particle_system = ParticleSystem()
        self.notification_manager = NotificationManager()

        # Level progress
        self.initial_enemy_count = 0
        self.level_complete = False
        self.next_level_button_rect = None

        # Time limit
        self.time_limit = 24 * 60 # minutes (24 minutes)
        self.elapsed_time = 0
        self.time_up = False

        # Path selection tracking
        self.path_selection_shown = False  # Has player seen path selection yet?
        self.pending_tank_upgrade = None  # Tank to upgrade to

        # Load first level
        self.load_level(0)

        # Spawn initial enemies
        #self.spawn_enemies(5)

    def format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins}:{secs:02d}"
        
    def load_level(self, level_number):
        """Load a level by number"""
        print(f"\n{'='*60}")
        print(f"Loading Level {level_number}...")
        print(f"{'='*60}")

        # RESET TIMER FOR NEW LEVEL
        #self.elapsed_time = 0
        self.time_up = False
        
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
            self.boss_spawn_point = map_result.get('boss_spawn', None)  # ← ADD THIS
            
            # Respawn player at spawn point
            spawn_x, spawn_y = self.player_spawn_point
            self.player.x = spawn_x
            self.player.y = spawn_y
            if hasattr(self.player, 'rect'):
                self.player.rect.center = (spawn_x, spawn_y)
            
            # Activate 3 second invulnerability shield
            self.player.activate_invulnerability(3.0)
            
            # Clear existing entities
            self.enemies.clear()
            self.bullets.clear()

            # === SPAWN ENEMIES ===
            self.spawn_enemies(self.current_level_number)
            
            # === SPAWN BOSS IF LEVEL HAS ONE ===
            if self.boss_spawn_point is not None:
                boss_x, boss_y = self.boss_spawn_point
                print(f"   🔴 Boss spawn detected at ({boss_x}, {boss_y})")
                self.spawn_boss(boss_x, boss_y)
            else:
                # No boss on this level
                self.has_boss = False
                self.boss_enemy = None

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
            print(f"   Enemies: {len(self.enemies)} ({'+BOSS' if self.has_boss else 'no boss'})")
            print(f"{'='*60}\n")
        else:
            print(f"❌ Failed to load level {level_number}, using empty map")
            self.walls = []


    def spawn_enemies(self, current_lvl):
        """Spawn regular enemies (excluding boss)"""
        spawn_points = self.enemy_spawn_points
        
        # === REGULAR ENEMY TYPES ONLY (no boss) ===
        regular_enemy_types = [
            EnemyType.SQUARE_TURRET,
            EnemyType.TRIANGLE_BLADE,
            EnemyType.PENTAGON_GUNNER
        ]
        
        for i in range(len(spawn_points)):
            spawn_x, spawn_y = spawn_points[i]
            # Choose only from regular enemies (boss excluded)
            enemy_type = random.choice(regular_enemy_types)
            self.enemies.append(Enemy(spawn_x, spawn_y, enemy_type, current_lvl))
        
        print(f"   Spawned {len(spawn_points)} regular enemies")
    def spawn_boss(self, x=None, y=None):
        """
        Spawn a boss enemy at specified location.
        If no location provided, spawns at center of world.
        """ 
        if x is None:
            x = self.world_width // 2
        if y is None:
            y = self.world_height // 2
        
        # Create boss enemy
        boss = Enemy(x, y, EnemyType.BOSS, self.current_level_number)
        self.enemies.append(boss)
        self.boss_enemy = boss  # Keep reference
        self.has_boss = True
        
        return boss


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
                    if self.player.level >= 5 and self.player.can_use_tank(TankType.TWIN):
                        self.player.tank_type = TankType.TWIN
                elif event.key == pygame.K_2:
                    if self.player.level >= 5 and self.player.can_use_tank(TankType.SNIPER):
                        self.player.tank_type = TankType.SNIPER
                    elif self.player.level >= 15 and self.player.can_use_tank(TankType.TRIPLET):
                        self.player.tank_type = TankType.TRIPLET
                elif event.key == pygame.K_3:
                    if self.player.level >= 5 and self.player.can_use_tank(TankType.MACHINE_GUN):
                        self.player.tank_type = TankType.MACHINE_GUN
                    elif self.player.level >= 15 and self.player.can_use_tank(TankType.MARKSMAN):
                        self.player.tank_type = TankType.MARKSMAN
                elif event.key == pygame.K_4:
                    if self.player.level >= 15 and self.player.can_use_tank(TankType.GATLING):
                        self.player.tank_type = TankType.GATLING
                elif event.key == pygame.K_5:
                    if self.player.level >= 25 and self.player.can_use_tank(TankType.PENTA_SHOT):
                        self.player.tank_type = TankType.PENTA_SHOT
                    elif self.player.level >= 25 and self.player.can_use_tank(TankType.RAILGUN):
                        self.player.tank_type = TankType.RAILGUN
                    elif self.player.level >= 25 and self.player.can_use_tank(TankType.MINIGUN):
                        self.player.tank_type = TankType.MINIGUN
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
        """Handle transition to next level or victory screen"""
        
        # === CHECK IF THIS WAS THE FINAL LEVEL ===
        if self.current_level_number == 5:
            # Player completed layer 5 (the 6th and final layer, since we start at 0)
            # Show VICTORY screen instead of transition
            
            from src.ui.victory_screen import VictoryScreen
            
            # Calculate total enemies killed (if you're tracking this)
            total_enemies_killed = getattr(self, 'enemies_killed', self.initial_enemy_count)
            
            victory = VictoryScreen(
                self.elapsed_time,                      # Total time taken
                total_enemies_killed,                   # Total enemies eliminated
                self.player.level,                      # Final player level
                getattr(self.player, 'death_count', 0)  # Deaths (0 if not tracked)
            )
            
            result = victory.show(self.screen)
            
            if result == 'menu':
                # Return to main menu
                self.running = False
                return 'menu'
            elif result == 'quit':
                # Close game
                self.running = False
                return None
        
        else:
            # === NORMAL LEVEL TRANSITION (Layers 0-4) ===
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
            
            # Deal contact damage (skip if invulnerable)
            current_time = pygame.time.get_ticks()
            if not self.player.invulnerable and (not hasattr(enemy, 'last_contact_damage') or current_time - enemy.last_contact_damage > 1000):
                self.player.take_damage(5 * dmg_multi)
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
                    # Skip if we already hit this enemy
                    if enemy in bullet.hit_enemies:
                        continue
                    
                    dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if dist < enemy.size:
                        enemy.take_damage(bullet.damage)
                        
                        # === DIFFERENT PENETRATION COST PER ENEMY TYPE ===
                        penetration_cost = self.get_enemy_penetration_cost(enemy)
                        bullet.health -= penetration_cost
                        
                        bullet.hit_enemies.append(enemy)  # Mark as hit
                        
                        if enemy.health <= 0:
                            # CREATE EXPLOSION WHEN ENEMY DIES
                            enemy_color = self.get_enemy_color(enemy)
                            self.particle_system.create_explosion(
                                enemy.x, 
                                enemy.y, 
                                enemy_color,
                                particle_count=20,
                                speed=4
                            )
                            
                            self.player.gain_xp(enemy.xp_value, self)
                            self.enemies.remove(enemy)
                        
                        if bullet.health <= 0 and bullet in self.bullets:
                            self.bullets.remove(bullet)
                            break  # Bullet is dead, stop checking

    def get_enemy_penetration_cost(self, enemy):
        """
        How much bullet health is consumed when hitting this enemy type
        Lower = easier to penetrate
        """
        from src.utils.enums import EnemyType
        
        if enemy.type == EnemyType.SQUARE_TURRET:
            return 20  # Easiest - weak armor
        elif enemy.type == EnemyType.TRIANGLE_BLADE:
            return 50  # Medium - fast but fragile
        elif enemy.type == EnemyType.PENTAGON_GUNNER:
            return 100  # Hard - tough armor
        elif enemy.type == EnemyType.BOSS:
            return 500  # Hardest - massive armor
        else:
            return 20  # Default



    def get_enemy_color(self, enemy):
        """Get the color for an enemy based on type"""
        if enemy.type == EnemyType.SQUARE_TURRET:
            return CORRUPTION_PINK
        elif enemy.type == EnemyType.TRIANGLE_BLADE:
            return CORRUPTION_ORANGE
        elif enemy.type == EnemyType.PENTAGON_GUNNER:
            return (255, 100, 100)
        else:
            return CORRUPTION_PINK
    
    def _check_enemy_bullets_vs_player(self):
        """Check enemy bullets hitting player"""
        for bullet in self.bullets[:]:
            if bullet.owner_type == "enemy":
                dist = math.sqrt((bullet.x - self.player.x)**2 + (bullet.y - self.player.y)**2)
                if dist < self.player.size and not self.player.invulnerable:  # Check invulnerability
                    dmg_multi = 1 + (self.current_level_number * 0.1)
                    self.player.take_damage(bullet.damage * dmg_multi)
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
        print('Player death - showing game over screen')
        self.player.hp = 0
        
        # Calculate final score: (level * 100) + (enemies killed * 50)
        enemies_killed = self.initial_enemy_count - len(self.enemies)
        final_score = (self.player.level * 100) + (enemies_killed * 50)

        game_over = GameOverScreen(score=final_score)
        result = game_over.run()
        
        if result == 'retry':
            # === RESET PLAYER ===
            self.player.hp = self.player.max_hp
            x, y = self.player_spawn_point
            self.player.x = x
            self.player.y = y
            
            # Optional: Reset level/XP (currently commented out)
            # self.player.level = 1
            # self.player.xp = 0
            # self.player.skill_points = 0
            
            # === CLEAR GAME STATE ===
            self.enemies.clear()
            self.bullets.clear()
            self.particle_system.clear()
            
            # === RESPAWN ENEMIES ===
            self.spawn_enemies(self.current_level_number)
            
            # === RESPAWN BOSS IF LEVEL HAS ONE ===
            if self.boss_spawn_point is not None:
                boss_x, boss_y = self.boss_spawn_point
                print(f"   Respawning boss at ({boss_x}, {boss_y})")
                self.spawn_boss(boss_x, boss_y)
            else:
                # No boss on this level
                self.has_boss = False
                self.boss_enemy = None
            
            # === RESET LEVEL TRACKING ===
            self.initial_enemy_count = len(self.enemies)
            self.level_complete = False
            
            # === RESET TIMER ===
            self.elapsed_time = 0
            self.time_up = False
            
            print(f"   Level retry: {len(self.enemies)} enemies spawned")
            if self.has_boss:
                print(f"   Boss respawned!")
        
        elif result == 'menu':
            self.running = False
            return 'menu'
        else:
            self.running = False
        
        return None


    def check_for_auto_upgrade(self):
        """Check if player should auto-upgrade their tank"""
        if not self.player.path_locked:
            return
        
        # Get what tank they should have at this level
        target_tank = self.player.get_current_path_tank_for_level()
        
        # If it's different from current, upgrade!
        if target_tank != self.player.tank_type:
            old_tank = self.player.tank_type.name
            self.player.tank_type = target_tank
            
            # === FIXED NOTIFICATION ===
            self.notification_manager.add_notification(
                f"🔧 EVOLVED: {old_tank} → {target_tank.name}",
                x=SCREEN_WIDTH // 2,
                y=250,
                duration=4.0,
                font_size=42,
                color=(0, 255, 100)
            )


    # ========== MAIN UPDATE METHOD ==========
    
    def update(self):
        """Main game update loop - coordinates all game systems"""
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Update elapsed time
        self.elapsed_time += 1/60.0  # Add 1/60th of a second per frame
        
        # Check if time is up
        if self.elapsed_time >= self.time_limit and not self.time_up:
            self.time_up = True
            return self._handle_player_death()

        if self.player.level >= 5 and not self.path_selection_shown and not self.player.path_locked:
            # Pause game and show path selection
            self.show_path_selection()
            self.path_selection_shown = True
        
        # === CHECK FOR AUTO TANK UPGRADES (Level 10, 15) ===
        if self.player.level in [15, 25] and self.player.path_locked:
            self.check_for_auto_upgrade()

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

        # Update particles
        self.particle_system.update()

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
        
        # Update notifications
        self.notification_manager.update(1/60.0)
    
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

        # Draw particles
        self.particle_system.draw(self.screen, self.camera_x, self.camera_y)

        # Draw UI (always on top, no z_index needed)
        self.draw_ui()
        
        pygame.display.flip()
    
    def show_path_selection(self):
        """Show path selection UI at level 5"""
        path_ui = PathSelectionUI(self.screen)
        chosen_path = path_ui.show()
        
        if chosen_path:
            self.player.choose_path(chosen_path)
            
            # Auto-upgrade to tier 1 of chosen path
            self.check_for_auto_upgrade()
            
            # Show confirmation notification
            path_names = {
                TankPath.GUNNER: "GUNNER",
                TankPath.SNIPER: "SNIPER",
                TankPath.SPRAYER: "SPRAYER"
            }
            
            # === FIXED NOTIFICATION ===
            self.notification_manager.add_notification(
                f"PATH LOCKED: {path_names.get(chosen_path, 'UNKNOWN')}",
                x=SCREEN_WIDTH // 2,
                y=200,
                duration=5.0,
                font_size=36,
                color=(255, 215, 0)
            )
    
    def draw_ui(self):
        # ===== INVULNERABILITY SHIELD VISUAL =====
        if self.player.invulnerable:
            # Calculate time remaining
            time_remaining = max(0, (self.player.invulnerability_end_time - pygame.time.get_ticks()) / 1000.0)
            # Create pulsing shield effect
            shield_intensity = (abs(math.sin(pygame.time.get_ticks() * 0.01)) + 0.5) * 100
            shield_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            shield_overlay.fill((0, 200, 255, int(shield_intensity * 0.15)))  # Cyan flash
            self.screen.blit(shield_overlay, (0, 0))
            
            # Draw shield timer text
            shield_text = self.font.render(f"SHIELD: {time_remaining:.1f}s", True, (0, 200, 255))
            self.screen.blit(shield_text, (SCREEN_WIDTH // 2 - shield_text.get_width() // 2, 30))
        
        # ===== RED FLASH EFFECT WHEN HEALTH <= 50% =====
        if self.player.hp <= self.player.max_hp * 0.5:
            # Create pulsing flash effect based on time
            flash_intensity = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 100
            red_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, int(flash_intensity * 0.4)))  # Red with varying alpha
            self.screen.blit(red_overlay, (0, 0))
        
        # ===== ENHANCED MISSION TIMER (SMART UNIT DISPLAY) =====
        remaining_time = max(0, self.time_limit - self.elapsed_time)

        # === EDEN TIME DISPLAY ===
        # If over 60 seconds, show as minutes:seconds
        if remaining_time >= 60:
            eden_minutes = int(remaining_time // 60)
            eden_seconds = int(remaining_time % 60)
            eden_display = f"{eden_minutes}:{eden_seconds:02d}m"
        else:
            # Under 60 seconds, just show seconds
            eden_display = f"{int(remaining_time)}s"

        # === REAL WORLD TIME DISPLAY (1 EDEN minute = 3 real hours) ===
        real_total_hours = remaining_time / 60 * 3  # Convert to real hours

        # If over 24 hours, show as days + hours
        if real_total_hours >= 24:
            real_days = int(real_total_hours // 24)
            real_hours = int(real_total_hours % 24)
            if real_hours > 0:
                real_display = f"{real_days}d {real_hours}h"
            else:
                real_display = f"{real_days}d"
        else:
            # Under 24 hours, show as hours + minutes
            real_hours = int(real_total_hours)
            real_minutes = int((real_total_hours % 1) * 60)
            if real_minutes > 0:
                real_display = f"{real_hours}h {real_minutes}m"
            else:
                real_display = f"{real_hours}h"

        # Format the full display string
        timer_text = f"EDEN: {eden_display} | REAL: {real_display}"

        # Change color based on urgency
        if remaining_time < 300:  # Less than 5 minutes
            time_color = (255, 0, 0)  # Red
        elif remaining_time < 600:  # Less than 10 minutes
            time_color = (255, 165, 0)  # Orange
        else:
            time_color = (0, 255, 255)  # Cyan

        # Render the text
        time_text = self.font.render(timer_text, True, time_color)

        # Draw background box for visibility
        box_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 70))
        inflated_rect = box_rect.inflate(40, 20)

        # Create semi-transparent background
        bg_surface = pygame.Surface(inflated_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        self.screen.blit(bg_surface, inflated_rect.topleft)

        # Draw border
        pygame.draw.rect(self.screen, time_color, inflated_rect, 2)

        # Draw the timer text
        self.screen.blit(time_text, box_rect)
        # Draw border (stays opaque)
        pygame.draw.rect(self.screen, time_color, inflated_rect, 2)

        # Draw text
        self.screen.blit(time_text, box_rect)
                
        # Enemy progress bar
        self.level_progress_ui.draw_enemy_progress_bar(
            self.screen, 
            len(self.enemies), 
            self.initial_enemy_count, 
            self.level_complete
        )

                # === BOSS HEALTH BAR (if boss exists) ===
        if self.has_boss and self.boss_enemy is not None and self.boss_enemy in self.enemies:
            # Boss is alive - draw health bar
            boss = self.boss_enemy
            
            # Position (below enemy progress bar)
            boss_bar_x = SCREEN_WIDTH // 2 - 300  # Center, 600px wide
            boss_bar_y = 150  # Below timer
            boss_bar_width = 600
            boss_bar_height = 40
            
            # === BOSS NAME LABEL ===
            boss_name_font = pygame.font.Font(None, 32)
            boss_name = boss_name_font.render("⚠️ CORRUPTION CORE ⚠️", True, (255, 50, 50))
            name_rect = boss_name.get_rect(center=(SCREEN_WIDTH // 2, boss_bar_y - 20))
            
            # Name background
            name_bg_rect = name_rect.inflate(40, 15)
            name_bg = pygame.Surface(name_bg_rect.size, pygame.SRCALPHA)
            name_bg.fill((0, 0, 0, 200))
            self.screen.blit(name_bg, name_bg_rect.topleft)
            pygame.draw.rect(self.screen, (255, 50, 50), name_bg_rect, 2)
            
            self.screen.blit(boss_name, name_rect)
            
            # === HEALTH BAR BACKGROUND ===
            bar_bg = pygame.Surface((boss_bar_width, boss_bar_height), pygame.SRCALPHA)
            bar_bg.fill((0, 0, 0, 230))
            self.screen.blit(bar_bg, (boss_bar_x, boss_bar_y))
            
            # Calculate health percentage
            health_percent = max(0, boss.health / boss.max_health)
            
            # Health bar color based on percentage
            if health_percent > 0.75:
                health_color = (255, 100, 0)  # Orange - full health
            elif health_percent > 0.5:
                health_color = (255, 150, 0)  # Orange-yellow
            elif health_percent > 0.25:
                health_color = (255, 200, 0)  # Yellow - getting low
            else:
                health_color = (255, 50, 50)  # Red - critical
            
            # === FILL HEALTH BAR ===
            fill_width = int((boss_bar_width - 4) * health_percent)
            if fill_width > 0:
                pygame.draw.rect(self.screen, health_color,
                                (boss_bar_x + 2, boss_bar_y + 2, fill_width, boss_bar_height - 4))
            
            # === SHIELD INDICATOR ===
            if boss.shield_active:
                # Draw pulsing shield overlay
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
                shield_alpha = int(100 + pulse * 100)
                
                shield_overlay = pygame.Surface((boss_bar_width - 4, boss_bar_height - 4), pygame.SRCALPHA)
                shield_overlay.fill((100, 200, 255, shield_alpha))
                self.screen.blit(shield_overlay, (boss_bar_x + 2, boss_bar_y + 2))
                
                # Shield text
                shield_font = pygame.font.Font(None, 24)
                shield_text = shield_font.render("🛡️ SHIELD ACTIVE 🛡️", True, (200, 255, 255))
                shield_rect = shield_text.get_rect(center=(SCREEN_WIDTH // 2, boss_bar_y + boss_bar_height // 2))
                self.screen.blit(shield_text, shield_rect)
            
            # === BORDER ===
            pygame.draw.rect(self.screen, health_color, 
                            (boss_bar_x, boss_bar_y, boss_bar_width, boss_bar_height), 3)
            
            # === HP TEXT ===
            hp_font = pygame.font.Font(None, 28)
            hp_text = hp_font.render(f"{int(boss.health)}/{int(boss.max_health)} HP", True, WHITE)
            hp_rect = hp_text.get_rect(center=(SCREEN_WIDTH // 2, boss_bar_y + boss_bar_height // 2))
            
            # Don't draw HP text if shield is active (would overlap)
            if not boss.shield_active:
                self.screen.blit(hp_text, hp_rect)
            
            # === SHIELD PHASE INDICATORS ===
            # Show which shield phases are remaining
            phase_y = boss_bar_y + boss_bar_height + 10
            phase_font = pygame.font.Font(None, 20)
            
            # Check which thresholds haven't been used yet
            remaining_shields = []
            for threshold in boss.shield_thresholds:
                if threshold not in boss.shield_used:
                    remaining_shields.append(int(threshold * 100))
            
        # Level Complete Button
        if self.level_complete:
            self.level_progress_ui.draw_next_level_button(self.screen)

        # Health bar
        bar_x = 20
        bar_y = SCREEN_HEIGHT - 80
        bar_width = 300
        bar_height = 20
        
        pygame.draw.rect(self.screen, UI_RED, (bar_x, bar_y, bar_width, bar_height))
        health_percent = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, CLEAN_GREEN, 
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
        
        # Draw notifications
        self.notification_manager.draw(self.screen)
    
    def run(self):
        while self.running:
            self.handle_events()
            result = self.update()  # Capture the return value from update()
            if result == 'menu':
                return 'menu'  # Pass it back to main.py
            self.draw()
            self.clock.tick(FPS)
        
        return None  # Return None if game exits normally
import pygame
import random
import math

from src.ui.game_over import GameOverScreen
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.boss import VoidCoreBoss
#from src.levels.level_manager import LevelManager
#from src.ui.hud import HUD
from src.utils.constants import *
from src.utils.enums import *
from src.ui.stat_upgrade_ui import StatUpgradeUI
from src.entities.wall import Wall
from src.entities.barrier import Barrier
from src.systems.collisions import CollisionSystem
from src.levels.map_generator import MapGenerator
from src.ui.level_transition import LevelTransition
from src.ui.level_progress_ui import LevelProgressUI
from src.ui.minimap import Minimap
from src.entities.particle import ParticleSystem
from src.ui.notification import NotificationManager


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
        self.time_limit = 180 # seconds (3 minutes)
        self.elapsed_time = 0
        self.time_up = False

        # Load first level (4 = boss level for testing)
        self.load_level(4)

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
        self.elapsed_time = 0
        self.time_up = False
        
        # Special handling for boss level (level 4) - Create open arena
        if level_number == 4:
            self.current_level_number = 4
            self.level_name = "THE VOID CORE - FINAL BATTLE"
            
            # Open arena dimensions - larger space for bullet hell dodging
            self.world_width = 3000
            self.world_height = 3000
            
            # Create only boundary walls (open arena)
            self.walls = self._create_boss_arena_walls()
            self.enemy_barriers = []
            
            # Boss and player positions
            boss_x = self.world_width // 2
            boss_y = self.world_height // 2
            
            # Spawn player facing the boss from below
            spawn_x = boss_x
            spawn_y = boss_y + 500
            
            self.player.x = spawn_x
            self.player.y = spawn_y
            if hasattr(self.player, 'rect'):
                self.player.rect.center = (spawn_x, spawn_y)
            
            # Set spawn points for boss minions (around the arena)
            self.enemy_spawn_points = [
                (boss_x + 400, boss_y),
                (boss_x - 400, boss_y),
                (boss_x, boss_y + 400),
                (boss_x, boss_y - 400),
                (boss_x + 350, boss_y + 350),
                (boss_x - 350, boss_y - 350),
                (boss_x + 350, boss_y - 350),
                (boss_x - 350, boss_y + 350)
            ]
            
            # Activate invulnerability shield
            self.player.activate_invulnerability(3.0)
            
            # Clear existing entities
            self.enemies.clear()
            self.bullets.clear()
            
            # Spawn the boss
            self.spawn_enemies(4)
            
            # Track for progress
            self.initial_enemy_count = 1
            self.level_complete = False
            
            # Update minimap
            self.minimap.world_width = self.world_width
            self.minimap.world_height = self.world_height
            
            print(f"✅ Boss Arena created!")
            print(f"   Name: {self.level_name}")
            print(f"   Arena size: {self.world_width}x{self.world_height}")
            print(f"   Style: OPEN SPACE - Bullet Hell Arena")
            print(f"   Player spawn: ({spawn_x}, {spawn_y})")
            print(f"   Boss spawn: ({boss_x}, {boss_y})")
            print(f"{'='*60}\n")
            return
        
        # Normal level loading for levels 0-3
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
            
            # Normal spawn from map data
            spawn_x, spawn_y = self.player_spawn_point
            
            # Respawn player at spawn position
            self.player.x = spawn_x
            self.player.y = spawn_y
            if hasattr(self.player, 'rect'):
                self.player.rect.center = (spawn_x, spawn_y)
            
            # Activate 3 second invulnerability shield
            self.player.activate_invulnerability(3.0)
            
            # Clear existing entities
            self.enemies.clear()
            self.bullets.clear()

            # Spawn enemies
            self.spawn_enemies(self.current_level_number)

            # Track initial enemy count for progress bar
            if self.current_level_number == 4:
                # Boss level - only count the boss, not spawned minions
                self.initial_enemy_count = 1 if self.has_boss else 0
                self.boss_level_enemy_count = 0  # Track minions separately
            else:
                # Normal level - count spawned enemies
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
    
    def _create_boss_arena_walls(self):
        """Create boundary walls and obstacles for boss arena"""
        walls = []
        wall_thickness = 100  # Thick walls to prevent escape
        
        # === BOUNDARY WALLS === (using enemy_barrier style for boss theme)
        # Top wall
        walls.append(Wall(0, 0, self.world_width, wall_thickness, "enemy_barrier"))
        
        # Bottom wall
        walls.append(Wall(0, self.world_height - wall_thickness, 
                         self.world_width, wall_thickness, "enemy_barrier"))
        
        # Left wall
        walls.append(Wall(0, 0, wall_thickness, self.world_height, "enemy_barrier"))
        
        # Right wall
        walls.append(Wall(self.world_width - wall_thickness, 0, 
                         wall_thickness, self.world_height, "enemy_barrier"))
        
        # === STRATEGIC OBSTACLES === (using enemy_barrier walls for boss theme)
        center_x = self.world_width // 2
        center_y = self.world_height // 2
        
        # Four corner pillars - enemy barrier style for cover
        pillar_size = 150
        corner_offset = 600  # Distance from center
        
        # Top-left pillar
        walls.append(Wall(center_x - corner_offset - pillar_size//2, 
                         center_y - corner_offset - pillar_size//2, 
                         pillar_size, pillar_size, "enemy_barrier"))
        
        # Top-right pillar
        walls.append(Wall(center_x + corner_offset - pillar_size//2, 
                         center_y - corner_offset - pillar_size//2, 
                         pillar_size, pillar_size, "enemy_barrier"))
        
        # Bottom-left pillar
        walls.append(Wall(center_x - corner_offset - pillar_size//2, 
                         center_y + corner_offset - pillar_size//2, 
                         pillar_size, pillar_size, "enemy_barrier"))
        
        # Bottom-right pillar
        walls.append(Wall(center_x + corner_offset - pillar_size//2, 
                         center_y + corner_offset - pillar_size//2, 
                         pillar_size, pillar_size, "enemy_barrier"))
        
        # Four small cover walls at cardinal directions (enemy barrier style)
        cover_wall_length = 200
        cover_wall_thickness = 50
        cover_distance = 400  # Distance from boss
        
        # North cover (horizontal wall)
        walls.append(Wall(center_x - cover_wall_length//2, 
                         center_y - cover_distance, 
                         cover_wall_length, cover_wall_thickness, "enemy_barrier"))
        
        # South cover (horizontal wall)
        walls.append(Wall(center_x - cover_wall_length//2, 
                         center_y + cover_distance - cover_wall_thickness, 
                         cover_wall_length, cover_wall_thickness, "enemy_barrier"))
        
        # West cover (vertical wall)
        walls.append(Wall(center_x - cover_distance, 
                         center_y - cover_wall_length//2, 
                         cover_wall_thickness, cover_wall_length, "enemy_barrier"))
        
        # East cover (vertical wall)
        walls.append(Wall(center_x + cover_distance - cover_wall_thickness, 
                         center_y - cover_wall_length//2, 
                         cover_wall_thickness, cover_wall_length, "enemy_barrier"))
        
        print(f"   Created {len(walls)} walls (all 12 using enemy_barrier style)")
        return walls
    
    def spawn_enemies(self, current_lvl): # Difficulty
        # Check if this is the boss level (level 4)
        if current_lvl == 4:
            # Spawn the boss in the center of the map
            boss_x = self.world_width // 2
            boss_y = self.world_height // 2
            self.boss_enemy = VoidCoreBoss(boss_x, boss_y, current_lvl)
            self.has_boss = True
            
            # Show boss warning notification
            self.notification_manager.add_notification(
                "⚠ WARNING: VOID CORE DETECTED ⚠",
                x=SCREEN_WIDTH // 2,
                y=SCREEN_HEIGHT // 2,
                duration=5.0,
                font_size=48,
                color=(255, 0, 0)
            )
            print(f"🔴 BOSS SPAWNED: {self.boss_enemy.boss_name}")
            print(f"   Position: ({boss_x}, {boss_y})")
            return
        
        # Normal enemy spawning for non-boss levels
        spawn_points = self.enemy_spawn_points
        for i in range(len(spawn_points)):
            spawn_x, spawn_y = spawn_points[i]
            # Filter out boss type from random selection
            normal_enemy_types = [et for et in EnemyType if et != EnemyType.VOID_CORE_BOSS]
            enemy_type = random.choice(normal_enemy_types)
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
        # Check if we just completed the final level (boss level 4)
        if self.current_level_number >= 4:
            # Show victory screen instead of trying to load level 5
            print("\n" + "="*60)
            print("🎉 GAME COMPLETE! YOU DEFEATED THE VOID CORE! 🎉")
            print("="*60 + "\n")
            
            # Show game over screen with victory message
            final_score = (self.player.level * 100) + 1000  # Bonus for beating boss
            game_over = GameOverScreen(score=final_score)
            result = game_over.run()
            
            if result == 'menu':
                self.running = False
                return 'menu'
            else:
                self.running = False
            return
        
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
            # Check collision based on wall type (Wall vs Barrier)
            collision = False
            if hasattr(wall, 'collides_with'):
                # Wall object
                collision = wall.collides_with(player_rect)
            elif hasattr(wall, 'collides_with_circle'):
                # Barrier object
                collision = wall.collides_with_circle(self.player.x, self.player.y, self.player.size)
            
            if collision:
                self.player.x = old_x
                self.player.y = old_y
                if hasattr(self.player, 'rect'):
                    self.player.rect.center = (old_x, old_y)
                return True
        return False
    
    def handle_enemy_collisions(self, enemy_old_positions):
        """Handle all enemy collision detection"""
        # Safety check: ensure we have old positions for all enemies
        if len(self.enemies) == 0 or len(enemy_old_positions) != len(self.enemies):
            return
        
        for i, enemy in enumerate(self.enemies[:]):
            if i >= len(enemy_old_positions):
                continue
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
            # Check collision based on wall type (Wall vs Barrier)
            collision = False
            if hasattr(wall, 'collides_with'):
                # Wall object
                collision = wall.collides_with(enemy_rect)
            elif hasattr(wall, 'collides_with_circle'):
                # Barrier object
                collision = wall.collides_with_circle(enemy.x, enemy.y, enemy.size)
            
            if collision:
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
                        break

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
                # Check collision based on wall type (Wall vs Barrier)
                collision = False
                if hasattr(wall, 'collides_with'):
                    # Wall object
                    collision = wall.collides_with(bullet_rect)
                elif hasattr(wall, 'collides_with_circle'):
                    # Barrier object
                    collision = wall.collides_with_circle(bullet.x, bullet.y, bullet.radius)
                
                if collision:
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
    
    def _handle_boss_collisions(self):
        """Handle boss-specific collision detection"""
        if not self.boss_enemy:
            return
        
        # Check player bullets hitting boss
        for bullet in self.bullets[:]:
            if bullet.owner_type == "player":
                dist = math.sqrt((bullet.x - self.boss_enemy.x)**2 + 
                               (bullet.y - self.boss_enemy.y)**2)
                if dist < self.boss_enemy.size:
                    self.boss_enemy.take_damage(bullet.damage)
                    bullet.health -= 1
                    
                    # Create hit particles
                    self.particle_system.create_explosion(
                        bullet.x, bullet.y, 
                        (255, 0, 0),
                        particle_count=5,
                        speed=2
                    )
                    
                    if bullet.health <= 0 and bullet in self.bullets:
                        self.bullets.remove(bullet)
        
        # Check tendril hits on player
        tendril_hitboxes = self.boss_enemy.get_tendril_hitboxes()
        for hitbox in tendril_hitboxes:
            # Simple distance check for tendril collision
            end_x, end_y = hitbox['end']
            dist = math.sqrt((end_x - self.player.x)**2 + (end_y - self.player.y)**2)
            if dist < hitbox['thickness'] + self.player.size:
                self.player.hp -= hitbox['damage'] * 0.1  # Damage per frame
                self.player.last_damage_time = pygame.time.get_ticks()
        
        # Check boss body collision with player
        dist = math.sqrt((self.boss_enemy.x - self.player.x)**2 + 
                        (self.boss_enemy.y - self.player.y)**2)
        if dist < self.boss_enemy.size + self.player.size:
            # Contact damage
            self.player.hp -= 0.5  # Damage per frame
            self.player.last_damage_time = pygame.time.get_ticks()
    
    def _handle_player_death(self):
        """Handle player death and game over screen"""
        print('trying to attempt')
        self.player.hp = 0
        
        # Calculate final score: (level * 100) + (enemies killed * 50)
        enemies_killed = self.initial_enemy_count - len(self.enemies)
        final_score = (self.player.level * 100) + (enemies_killed * 50)

        game_over = GameOverScreen(score=final_score)  # ✅ FIXED - Now using final_score!
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
            self.particle_system.clear()
            self.spawn_enemies(self.current_level_number)
            
            # RESET TIMER
            self.elapsed_time = 0
            self.time_up = False
        
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

        # Update elapsed time
        self.elapsed_time += 1/60.0  # Add 1/60th of a second per frame
        
        # Check if time is up
        if self.elapsed_time >= self.time_limit and not self.time_up:
            self.time_up = True
            return self._handle_player_death()

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
        
        # Update walls (for animated walls like enemy_barrier)
        for wall in self.walls:
            if hasattr(wall, 'update'):
                wall.update()

        # Update boss if present
        if self.has_boss and self.boss_enemy:
            self.boss_enemy.update(self.player.x, self.player.y, self.bullets)
            
            # Check if boss should spawn corruption enemies
            spawn_positions = self.boss_enemy.check_spawn_corruption()
            if spawn_positions:
                # Filter out boss type from spawns
                normal_enemy_types = [et for et in EnemyType if et != EnemyType.VOID_CORE_BOSS]
                for spawn_x, spawn_y in spawn_positions:
                    enemy_type = random.choice(normal_enemy_types)
                    self.enemies.append(Enemy(spawn_x, spawn_y, enemy_type, self.current_level_number))

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y, self.bullets)
        
        # Handle all collision detection
        self.handle_enemy_collisions(enemy_old_positions)
        result = self.handle_bullet_collisions()
        if result == 'menu':
            return 'menu'
        
        # Handle boss-specific collisions
        if self.has_boss and self.boss_enemy:
            self._handle_boss_collisions()

        # Check if level is complete
        if self.has_boss:
            # Boss level - complete when boss is defeated
            if self.boss_enemy and self.boss_enemy.health <= 0:
                # Create epic victory explosion
                self.particle_system.create_explosion(
                    self.boss_enemy.x,
                    self.boss_enemy.y,
                    (255, 0, 0),
                    particle_count=100,
                    speed=8
                )
                
                # Show victory notification
                self.notification_manager.add_notification(
                    "🎉 VOID CORE DESTROYED! 🎉",
                    x=SCREEN_WIDTH // 2,
                    y=SCREEN_HEIGHT // 2 - 100,
                    duration=5.0,
                    font_size=56,
                    color=(255, 215, 0)  # Gold color
                )
                
                self.notification_manager.add_notification(
                    "CONGRATULATIONS! You saved the network!",
                    x=SCREEN_WIDTH // 2,
                    y=SCREEN_HEIGHT // 2,
                    duration=5.0,
                    font_size=36,
                    color=(100, 255, 100)  # Green
                )
                
                # End the game immediately with victory screen
                print("🎉 BOSS DEFEATED!")
                print("\n" + "="*60)
                print("🎉 GAME COMPLETE! YOU DEFEATED THE VOID CORE! 🎉")
                print("="*60 + "\n")
                
                # Wait a moment for particles to show, then show game over
                pygame.time.wait(3000)  # 3 second delay to see the victory effects
                
                final_score = (self.player.level * 100) + 1000  # Bonus for beating boss
                game_over = GameOverScreen(score=final_score)
                result = game_over.run()
                
                if result == 'menu':
                    self.running = False
                    return 'menu'
                else:
                    self.running = False
                    return None
                
        elif len(self.enemies) == 0 and self.initial_enemy_count > 0 and not self.level_complete:
            # Normal level - complete when all enemies defeated
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
        
        # === ENHANCED BACKGROUND LAYERS ===
        
        # Layer 1: Subtle hexagonal background pattern (deepest layer)
        hex_grid_size = 100
        hex_color = (15, 25, 35)  # Very faint
        for x in range(0, self.world_width, hex_grid_size):
            for y in range(0, self.world_height, hex_grid_size):
                screen_x = x - int(self.camera_x * 0.95)  # Slight parallax
                screen_y = y - int(self.camera_y * 0.95)
                if -hex_grid_size < screen_x < SCREEN_WIDTH + hex_grid_size and \
                   -hex_grid_size < screen_y < SCREEN_HEIGHT + hex_grid_size:
                    # Draw small hexagon
                    hex_points = []
                    for i in range(6):
                        angle = math.radians(60 * i)
                        hx = screen_x + math.cos(angle) * 20
                        hy = screen_y + math.sin(angle) * 20
                        hex_points.append((hx, hy))
                    pygame.draw.polygon(self.screen, hex_color, hex_points, 1)
        
        # Layer 2: Circuit board lines (middle layer)
        circuit_spacing = 200
        circuit_color = (20, 35, 50)
        for x in range(0, self.world_width, circuit_spacing):
            screen_x = x - int(self.camera_x * 0.98)  # Different parallax speed
            if -10 < screen_x < SCREEN_WIDTH + 10:
                # Vertical circuit lines with nodes
                pygame.draw.line(self.screen, circuit_color, 
                               (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
                # Add circuit nodes
                for y in range(0, SCREEN_HEIGHT, circuit_spacing // 2):
                    pygame.draw.circle(self.screen, circuit_color, 
                                     (screen_x, y), 3)
        
        for y in range(0, self.world_height, circuit_spacing):
            screen_y = y - int(self.camera_y * 0.98)
            if -10 < screen_y < SCREEN_HEIGHT + 10:
                # Horizontal circuit lines
                pygame.draw.line(self.screen, circuit_color, 
                               (0, screen_y), (SCREEN_WIDTH, screen_y), 1)
        
        # Layer 3: Main grid (front layer - slightly more visible)
        grid_size = 50
        if self.current_level_number == 4:
            # Boss level - darker, more ominous grid
            grid_color = (30, 10, 10)  # Dark red tint
        else:
            # Normal levels - blue grid
            grid_color = (25, 45, 65)  # Slightly brighter than before
        
        for x in range(0, self.world_width, grid_size):
            screen_x = x - self.camera_x
            if -grid_size < screen_x < SCREEN_WIDTH + grid_size:
                pygame.draw.line(self.screen, grid_color, 
                               (screen_x, 0), (screen_x, SCREEN_HEIGHT))
        
        for y in range(0, self.world_height, grid_size):
            screen_y = y - self.camera_y
            if -grid_size < screen_y < SCREEN_HEIGHT + grid_size:
                pygame.draw.line(self.screen, grid_color, 
                               (0, screen_y), (SCREEN_WIDTH, screen_y))

        # == Draw Walls == #
        for wall in self.walls:
            # Handle different draw signatures (Wall vs Barrier)
            if isinstance(wall, Barrier):
                wall.draw(self.screen, self.camera_x, self.camera_y)
            else:
                wall.draw(self.screen, (self.camera_x, self.camera_y))
        
        # === Z-LAYER SYSTEM ===
        # Collect all drawable entities
        all_entities = []
        all_entities.extend(self.bullets)
        all_entities.extend(self.enemies)
        all_entities.append(self.player)
        
        # Add boss if present
        if self.has_boss and self.boss_enemy:
            all_entities.append(self.boss_enemy)
        
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
    
    def draw_ui(self):
        # Draw boss health bar at the very top if boss is present
        if self.has_boss and self.boss_enemy:
            self.boss_enemy.draw_boss_health_bar(self.screen)
        
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
        
        # Time limit display (top center)
        remaining_time = max(0, self.time_limit - self.elapsed_time)
        time_text_str = self.format_time(remaining_time)
        
        # Change color if time is running out
        if remaining_time < 3:  # Red if less than 3 seconds
            time_color = (255, 0, 0)
        elif remaining_time < 5:  # Orange if less than 5 seconds
            time_color = (255, 165, 0)
        else:
            time_color = WHITE
        
        # Draw time with background for visibility
        time_text = self.font.render(f"TIMER: {time_text_str}", True, time_color)

        # Draw background box for time (with transparency)
        box_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 70))
        inflated_rect = box_rect.inflate(100, 10)

        # Create transparent surface for background
        bg_surface = pygame.Surface(inflated_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 0), bg_surface.get_rect())  # LAST NUMBER IS THE TRANSPARENCY
        self.screen.blit(bg_surface, inflated_rect.topleft)

        # Draw border (stays opaque)
        pygame.draw.rect(self.screen, time_color, inflated_rect, 2)

        # Draw text
        self.screen.blit(time_text, box_rect)
                
        # Enemy progress bar
        # Calculate enemies remaining (for boss level, only count boss, not minions)
        if self.current_level_number == 4:
            # Boss level - only show boss count
            enemies_remaining = 1 if (self.has_boss and self.boss_enemy) else 0
        else:
            # Normal level - show all enemies
            enemies_remaining = len(self.enemies)
        
        self.level_progress_ui.draw_enemy_progress_bar(
            self.screen, 
            enemies_remaining, 
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
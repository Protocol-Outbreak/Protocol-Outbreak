import pygame
from src.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()

'''
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (10, 22, 40)
WHITE = (255, 255, 255)
GREY = (153, 153, 153)
CLEAN_BLUE = (81, 175, 219)
CORRUPTION_ORANGE = (255, 107, 0)
CORRUPTION_PINK = (255, 0, 102)
CORRUPTION_PURPLE = (157, 0, 255)
UI_CYAN = (0, 217, 255)
UI_GRAY = (100, 100, 100)

class TankType(Enum):
    BASIC = 1
    TWIN = 2
    SNIPER = 3
    MACHINE_GUN = 4
    FLANK_GUARD = 5

class EnemyType(Enum):
    SQUARE_TURRET = 1
    TRIANGLE_BLADE = 2
    PENTAGON_GUNNER = 3

class Bullet:
    def __init__(self, x, y, angle, speed, damage, penetration, owner_type="player"):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.health = penetration * 10  # Penetration determines bullet health
        self.max_health = self.health
        self.owner_type = owner_type
        self.radius = 5
        self.z_index = 25  # Layer: Bullets drawn below enemies and player
        
        # Calculate velocity
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw bullet with health-based transparency
        health_percent = self.health / self.max_health
        color = CLEAN_BLUE if self.owner_type == "player" else CORRUPTION_ORANGE
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)
        
    def is_off_screen(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        return (screen_x < -100 or screen_x > SCREEN_WIDTH + 100 or 
                screen_y < -100 or screen_y > SCREEN_HEIGHT + 100)

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
        
        # Set stats based on type
        if enemy_type == EnemyType.SQUARE_TURRET:
            self.health = 80
            self.max_health = 80
            self.speed = 0.5
            self.shoot_delay = 90
            self.xp_value = 15
        elif enemy_type == EnemyType.TRIANGLE_BLADE:
            self.health = 30
            self.max_health = 30
            self.speed = 3
            self.shoot_delay = 0  # Melee only
            self.xp_value = 25
        elif enemy_type == EnemyType.PENTAGON_GUNNER:
            self.health = 100
            self.max_health = 100
            self.speed = 1.5
            self.shoot_delay = 45
            self.xp_value = 50
    
    def update(self, player_x, player_y, bullets):
        # AI behavior
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
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
        
        # Draw based on type
        if self.type == EnemyType.SQUARE_TURRET:
            pygame.draw.rect(screen, CLEAN_BLUE, 
                           (screen_x - self.size//2, screen_y - self.size//2, self.size, self.size), 2)
        elif self.type == EnemyType.TRIANGLE_BLADE:
            points = [
                (screen_x + math.cos(self.angle) * self.size, 
                 screen_y + math.sin(self.angle) * self.size),
                (screen_x + math.cos(self.angle + 2.4) * self.size, 
                 screen_y + math.sin(self.angle + 2.4) * self.size),
                (screen_x + math.cos(self.angle - 2.4) * self.size, 
                 screen_y + math.sin(self.angle - 2.4) * self.size)
            ]
            pygame.draw.polygon(screen, CORRUPTION_PINK, points, 2)
        elif self.type == EnemyType.PENTAGON_GUNNER:
            points = []
            for i in range(5):
                angle = self.angle + (i * math.pi * 2 / 5)
                points.append((screen_x + math.cos(angle) * self.size,
                             screen_y + math.sin(angle) * self.size))
            pygame.draw.polygon(screen, CORRUPTION_ORANGE, points, 2)
        
        # Health bar
        bar_width = 40
        bar_height = 4
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, UI_GRAY, 
                        (screen_x - bar_width//2, screen_y - self.size - 10, bar_width, bar_height))
        pygame.draw.rect(screen, CORRUPTION_PINK, 
                        (screen_x - bar_width//2, screen_y - self.size - 10, 
                         int(bar_width * health_percent), bar_height))

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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
'''
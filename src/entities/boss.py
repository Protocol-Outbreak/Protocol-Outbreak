import pygame
import math
import random
from src.utils.constants import *
from src.entities.bullet import Bullet
from src.entities.particle import ParticleSystem

class VoidCoreBoss:
    """
    The Void Core - Final Boss
    A writhing mass of corruption with rotating tendrils and spawning abilities.
    Based on "The Void Core" concept - organic, threatening, chaotic.
    """
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.angle = 0
        self.game_level = level
        
        # Boss stats
        difficulty_multi = 1 + (self.game_level * 0.15)
        self.max_health = 2000 * difficulty_multi
        self.health = self.max_health
        self.size = 80  # Large boss
        self.speed = 0.6
        self.xp_value = 500
        self.z_index = 100  # Draw on top
        
        # Boss identification
        self.is_boss = True
        self.boss_name = "THE VOID CORE"
        
        # Aggro system
        self.is_aggroed = False
        self.aggro_range = 600
        self.deaggro_range = 800
        
        # Attack systems
        self.shoot_cooldown = 0
        self.shoot_delay = 40  # Fast shooting
        self.tendril_attack_cooldown = 0
        self.tendril_attack_delay = 180  # Every 3 seconds
        
        # Tendrils (8 rotating arms)
        self.tendrils = []
        for i in range(8):
            self.tendrils.append({
                'base_angle': i * (math.pi / 4),  # Evenly spaced
                'length': 0,
                'target_length': 80 + random.random() * 30,
                'thickness': 3,
                'attacking': False
            })
        
        # Corruption spawn system
        self.spawn_cooldown = 0
        self.spawn_delay = 480  # Every 8 seconds
        self.can_spawn = True
        self.max_spawns = 5  # Max corruption entities at once
        
        # Animation
        self.animation_frame = 0
        self.pulse = 0
        
        # Phase system (becomes more aggressive as health decreases)
        self.phase = 1  # Phases: 1, 2, 3
        
        # Corruption orbits (smaller entities that orbit the boss)
        self.corruption_orbiters = []
        for i in range(5):
            self.corruption_orbiters.append({
                'angle': i * (math.pi * 2 / 5),
                'distance': 120,
                'size': 12,
                'speed': 0.08
            })
        
        # Screen shake when tendrils slam
        self.screen_shake_intensity = 0
        
    def take_damage(self, damage):
        """Handle taking damage and phase transitions"""
        self.health -= damage
        self.is_aggroed = True
        
        # Phase transitions
        health_percent = self.health / self.max_health
        if health_percent <= 0.33 and self.phase < 3:
            self.enter_phase_3()
        elif health_percent <= 0.66 and self.phase < 2:
            self.enter_phase_2()
    
    def enter_phase_2(self):
        """Phase 2: More aggressive"""
        self.phase = 2
        self.shoot_delay = 30  # Faster shooting
        self.tendril_attack_delay = 120  # More frequent tendril attacks
        self.spawn_delay = 360  # Spawn more often
        print(f"🔴 {self.boss_name} ENTERS PHASE 2!")
        
    def enter_phase_3(self):
        """Phase 3: Maximum aggression"""
        self.phase = 3
        self.shoot_delay = 20  # Very fast shooting
        self.tendril_attack_delay = 90  # Constant tendril attacks
        self.spawn_delay = 240  # Spawn frequently
        self.speed = 1.0  # Moves faster
        print(f"🔴 {self.boss_name} ENTERS FINAL PHASE!")
    
    def update(self, player_x, player_y, bullets):
        """Main update loop"""
        self.animation_frame += 1
        self.pulse = math.sin(self.animation_frame * 0.15) * 15
        
        # Calculate distance to player
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Aggro check
        if not self.is_aggroed:
            if distance <= self.aggro_range:
                self.is_aggroed = True
        else:
            if distance > self.deaggro_range:
                self.is_aggroed = False
        
        # Only act if aggroed
        if self.is_aggroed and distance > 0:
            self.angle = math.atan2(dy, dx)
            
            # Movement - keeps medium distance
            if distance < 250:
                self.x -= (dx / distance) * self.speed
                self.y -= (dy / distance) * self.speed
            elif distance > 400:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            
            # Update tendrils
            self._update_tendrils(player_x, player_y)
            
            # Update corruption orbiters
            for orbiter in self.corruption_orbiters:
                orbiter['angle'] += orbiter['speed']
            
            # Shooting attack
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_radial_burst(bullets)
                self.shoot_cooldown = self.shoot_delay
            
            # Tendril slam attack
            self.tendril_attack_cooldown -= 1
            if self.tendril_attack_cooldown <= 0:
                self._trigger_tendril_attack()
                self.tendril_attack_cooldown = self.tendril_attack_delay
        else:
            # Idle rotation
            self.angle += 0.02
            for orbiter in self.corruption_orbiters:
                orbiter['angle'] += 0.02
    
    def _update_tendrils(self, player_x, player_y):
        """Update tendril animation and attacks"""
        for i, tendril in enumerate(self.tendrils):
            # Animate length
            if tendril['attacking']:
                tendril['length'] = min(tendril['length'] + 10, 150)
                if tendril['length'] >= 150:
                    tendril['attacking'] = False
            else:
                # Retract to target length
                if tendril['length'] > tendril['target_length']:
                    tendril['length'] -= 5
                else:
                    tendril['length'] = tendril['target_length']
            
            # Sine wave variation
            variation = math.sin(self.animation_frame * 0.1 + i) * 30
            tendril['current_length'] = tendril['length'] + variation
    
    def _trigger_tendril_attack(self):
        """Trigger all tendrils to lash out"""
        for tendril in self.tendrils:
            tendril['attacking'] = True
        self.screen_shake_intensity = 10
    
    def shoot_radial_burst(self, bullets):
        """Fire bullets in a radial pattern"""
        dmg_multi = 1 + (self.game_level * 0.1)
        num_bullets = 5 if self.phase == 1 else (8 if self.phase == 2 else 12)
        
        for i in range(num_bullets):
            angle = self.angle + (i - num_bullets / 2) * 0.4
            bullet = Bullet(self.x, self.y, angle, 8, 12 * dmg_multi, 3, "enemy")
            bullet.radius = 8  # Bigger bullets
            bullets.append(bullet)
    
    def check_spawn_corruption(self):
        """Check if boss should spawn corruption entities - called from game.py"""
        if not self.can_spawn or not self.is_aggroed:
            return None
        
        self.spawn_cooldown -= 1
        if self.spawn_cooldown <= 0:
            self.spawn_cooldown = self.spawn_delay
            
            # Spawn corruption entities around boss
            spawn_positions = []
            num_spawns = 2 if self.phase == 1 else (3 if self.phase == 2 else 4)
            
            for i in range(num_spawns):
                angle = random.random() * math.pi * 2
                distance = 100 + random.random() * 80
                spawn_x = self.x + math.cos(angle) * distance
                spawn_y = self.y + math.sin(angle) * distance
                spawn_positions.append((spawn_x, spawn_y))
            
            return spawn_positions
        return None
    
    def get_tendril_hitboxes(self):
        """Return hitboxes for tendrils (for collision with player)"""
        hitboxes = []
        for i, tendril in enumerate(self.tendrils):
            if tendril.get('current_length', 0) > 50:  # Only if extended
                angle = tendril['base_angle'] + self.angle
                end_x = self.x + math.cos(angle) * tendril['current_length']
                end_y = self.y + math.sin(angle) * tendril['current_length']
                
                # Create hitbox rect for tendril
                hitboxes.append({
                    'start': (self.x, self.y),
                    'end': (end_x, end_y),
                    'thickness': tendril['thickness'] * 3,
                    'damage': 15 if tendril['attacking'] else 5
                })
        return hitboxes
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the boss with all visual effects"""
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Draw background corruption spread (pulsing circles)
        for i in range(3):
            radius = int(self.size + self.pulse + (i * 40))
            alpha = max(0, int(100 - i * 30))
            color = (255, 0, 0)
            
            # Create surface for alpha blending
            corruption_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(corruption_surface, (*color, alpha), 
                             (radius, radius), radius, 2 + i)
            screen.blit(corruption_surface, 
                       (screen_x - radius, screen_y - radius))
        
        # Draw tendrils
        for i, tendril in enumerate(self.tendrils):
            angle = tendril['base_angle'] + (self.animation_frame * 0.02)
            length = tendril.get('current_length', tendril['length'])
            
            end_x = screen_x + math.cos(angle) * length
            end_y = screen_y + math.sin(angle) * length
            
            # Tendril color - more red when attacking
            if tendril['attacking']:
                color = (255, 0, 0)
                thickness = int(tendril['thickness'] * 2)
            else:
                color = (255, 50, 50)
                thickness = int(tendril['thickness'])
            
            # Draw tendril with gradient effect
            pygame.draw.line(screen, color, (screen_x, screen_y), 
                           (end_x, end_y), thickness)
            
            # Draw tendril tip
            pygame.draw.circle(screen, color, (int(end_x), int(end_y)), thickness)
        
        # Draw corruption orbiters
        for orbiter in self.corruption_orbiters:
            orbit_x = screen_x + math.cos(orbiter['angle']) * orbiter['distance']
            orbit_y = screen_y + math.sin(orbiter['angle']) * orbiter['distance']
            
            # Draw orbiter with glow
            glow_surface = pygame.Surface((orbiter['size'] * 3, orbiter['size'] * 3), 
                                         pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 0, 0, 100), 
                             (orbiter['size'] * 1.5, orbiter['size'] * 1.5), 
                             orbiter['size'] * 1.5)
            screen.blit(glow_surface, 
                       (orbit_x - orbiter['size'] * 1.5, orbit_y - orbiter['size'] * 1.5))
            
            # Draw orbiter core
            pygame.draw.circle(screen, (255, 100, 100), 
                             (int(orbit_x), int(orbit_y)), orbiter['size'] // 2)
        
        # Draw main body - irregular, threatening shape
        points = []
        num_points = 9
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            # Irregular shape using varying radius
            radius_var = self.size + self.pulse + math.sin(angle * 3) * 15
            point_x = screen_x + math.cos(angle) * radius_var
            point_y = screen_y + math.sin(angle) * radius_var
            points.append((point_x, point_y))
        
        # Draw body with glow
        pygame.draw.polygon(screen, (100, 0, 0), points, 0)  # Fill
        pygame.draw.polygon(screen, (255, 0, 0), points, 4)  # Outline
        
        # Draw pulsing core eye
        core_size = int(30 + self.pulse * 0.3)
        core_glow = pygame.Surface((core_size * 3, core_size * 3), pygame.SRCALPHA)
        pygame.draw.circle(core_glow, (255, 0, 0, 150), 
                         (core_size * 1.5, core_size * 1.5), core_size * 1.5)
        screen.blit(core_glow, (screen_x - core_size * 1.5, screen_y - core_size * 1.5))
        
        pygame.draw.circle(screen, (255, 100, 100), (screen_x, screen_y), core_size // 2)
        pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), core_size // 2, 2)
        
    def draw_boss_health_bar(self, screen):
        """Draw boss health bar at top of screen"""
        bar_width = SCREEN_WIDTH - 200
        bar_height = 30
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 20
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_percent = max(0, self.health / self.max_health)
        fill_width = int(bar_width * health_percent)
        
        # Color changes based on phase
        if self.phase == 3:
            health_color = (255, 0, 0)
        elif self.phase == 2:
            health_color = (255, 100, 0)
        else:
            health_color = (200, 0, 0)
        
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Boss name
        font = pygame.font.Font(None, 28)
        name_text = font.render(self.boss_name, True, (255, 0, 0))
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y - 15))
        screen.blit(name_text, name_rect)
        
        # Phase indicator
        phase_text = font.render(f"PHASE {self.phase}", True, (255, 50, 50))
        screen.blit(phase_text, (bar_x + bar_width + 10, bar_y + 5))
        
        # Health text
        health_text = font.render(f"{int(self.health)}/{int(self.max_health)}", 
                                 True, (255, 255, 255))
        health_rect = health_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(health_text, health_rect)

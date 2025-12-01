import pygame
import math
import random
from src.utils.constants import *

class Particle:
    """Individual particle for explosions"""
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx  # Velocity x
        self.vy = vy  # Velocity y
        self.color = color
        self.lifetime = lifetime  # frames
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
        self.z_index = 30  # Draw below enemies
    
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Apply gravity
        self.vy += 0.1
    
    def is_alive(self):
        """Check if particle should still exist"""
        return self.lifetime > 0
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the particle"""
        if not self.is_alive():
            return
        
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Fade out effect
        alpha = int((self.lifetime / self.max_lifetime) * 255)
        
        # Create a temporary surface for the particle with alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(particle_surface, (screen_x - self.size, screen_y - self.size))


class ParticleSystem:
    """Manages all particles in the game"""
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color, particle_count=15, speed=3):
        """Create an explosion effect at a position"""
        for _ in range(particle_count):
            # Random direction
            angle = random.random() * math.pi * 2
            speed_variation = random.uniform(0.5, speed)
            vx = math.cos(angle) * speed_variation
            vy = math.sin(angle) * speed_variation
            
            # Random lifetime
            lifetime = random.randint(20, 40)
            
            particle = Particle(x, y, vx, vy, color, lifetime)
            self.particles.append(particle)
    
    def update(self):
        """Update all particles"""
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw(self, screen, camera_x, camera_y):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
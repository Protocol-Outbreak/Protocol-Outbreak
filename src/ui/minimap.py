import pygame
import math

class Minimap:
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        self.visible = False
        
        # Minimap settings
        self.width = 250
        self.height = 250
        self.margin = 20
        self.background_color = (10, 15, 25, 200)  # Semi-transparent dark
        self.border_color = (0, 255, 255)  # Cyan
        self.grid_color = (30, 50, 80)
        
        # Colors
        self.player_color = (0, 255, 255)  # Cyan
        self.enemy_color = (255, 80, 120)  # Pink/Red
        self.wall_color = (100, 120, 150)  # Gray
        
        # Create surface with transparency
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
    def toggle(self):
        """Toggle minimap visibility"""
        self.visible = not self.visible
    
    def world_to_minimap(self, world_x, world_y):
        """Convert world coordinates to minimap coordinates"""
        # Scale world position to minimap
        minimap_x = (world_x / self.world_width) * self.width
        minimap_y = (world_y / self.world_height) * self.height
        return int(minimap_x), int(minimap_y)
    
    def draw(self, screen, player, enemies, walls):
        """Draw the minimap"""
        if not self.visible:
            return
        
        # Clear surface
        self.surface.fill(self.background_color)
        
        # Draw grid
        grid_spacing = 50
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.surface, self.grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.surface, self.grid_color, (0, y), (self.width, y), 1)
        
        # Draw walls (optional - can be slow with many walls)
        for wall in walls[:100]:  # Limit to first 100 walls for performance
            wall_x, wall_y = self.world_to_minimap(wall.rect.x, wall.rect.y)
            wall_w = int((wall.rect.width / self.world_width) * self.width)
            wall_h = int((wall.rect.height / self.world_height) * self.height)
            pygame.draw.rect(self.surface, self.wall_color, 
                        (wall_x, wall_y, max(2, wall_w), max(2, wall_h)))

        # Draw enemies
        for enemy in enemies:
            enemy_x, enemy_y = self.world_to_minimap(enemy.x, enemy.y)
            pygame.draw.circle(self.surface, self.enemy_color, (enemy_x, enemy_y), 4)
            # Draw small glow
            glow_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.enemy_color, 80), (6, 6), 6)
            self.surface.blit(glow_surf, (enemy_x - 6, enemy_y - 6))
        
        # Draw player (last, so it's on top)
        player_x, player_y = self.world_to_minimap(player.x, player.y)
        pygame.draw.circle(self.surface, self.player_color, (player_x, player_y), 5)
        # Player glow
        glow_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.player_color, 100), (8, 8), 8)
        self.surface.blit(glow_surf, (player_x - 8, player_y - 8))
        
        # Draw border
        pygame.draw.rect(self.surface, self.border_color, 
                        (0, 0, self.width, self.height), 3)
        
        # Position minimap in top-right corner
        screen_x = self.margin
        screen_y = self.margin
        screen.blit(self.surface, (screen_x, screen_y))
        
        """
        # Draw "MINIMAP" label, remove quotes if you want it to show
        font = pygame.font.Font(None, 16)
        label = font.render("MINIMAP", True, self.border_color)
        screen.blit(label, (screen_x + 2, screen_y + 2))
        """
        
        """ 
       # Draw enemy counter at the bottom left, remove quotes if you want it to show
        enemy_text = font.render(f"Enemies: {len(enemies)}", True, self.enemy_color)
        screen.blit(enemy_text, (screen_x + 2, screen_y + self.height - 25))
        """
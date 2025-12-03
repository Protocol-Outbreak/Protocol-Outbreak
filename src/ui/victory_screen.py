# src/ui/victory_screen.py
import pygame
import math
from src.utils.constants import *

class VictoryScreen:
    """
    Displays the final victory screen after completing all 6 layers.
    Shows mission stats and celebrates the player's success.
    """
    def __init__(self, elapsed_time, enemies_killed, player_level, death_count=0):
        """
        Args:
            elapsed_time: Total time taken in seconds
            enemies_killed: Total enemies eliminated
            player_level: Final player level achieved
            death_count: Number of times player died (if you track this)
        """
        self.elapsed_time = elapsed_time
        self.enemies_killed = enemies_killed
        self.player_level = player_level
        self.death_count = death_count
        
        # Create fonts
        self.font_huge = pygame.font.Font(None, 84)
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
    def show(self, screen):
        """
        Display the victory screen.
        Returns 'menu' to go back to main menu.
        """
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        
        waiting = True
        while waiting:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        return 'menu'  # Return to menu
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
            
            # Calculate animation time
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - start_time) / 1000.0  # seconds
            
            # Draw everything
            self._draw_background(screen, elapsed)
            self._draw_content(screen, elapsed)
            
            pygame.display.flip()
            clock.tick(60)
        
        return 'menu'
    
    def _draw_background(self, screen, elapsed):
        """Draw animated background"""
        screen.fill(BLACK)
        
        # Animated grid (slower than level transition)
        grid_size = 50
        offset = int(elapsed * 20) % grid_size
        
        for x in range(-grid_size, SCREEN_WIDTH + grid_size, grid_size):
            pygame.draw.line(screen, (20, 60, 80), 
                           (x + offset, 0), (x + offset, SCREEN_HEIGHT), 1)
        
        for y in range(-grid_size, SCREEN_HEIGHT + grid_size, grid_size):
            pygame.draw.line(screen, (20, 60, 80), 
                           (0, y + offset), (SCREEN_WIDTH, y + offset), 1)
        
        # Pulsing glow effect
        pulse = abs(math.sin(elapsed * 1.5))
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        glow_alpha = int(20 + pulse * 30)
        glow_surface.fill((0, 255, 100, glow_alpha))
        screen.blit(glow_surface, (0, 0))
    
    def _draw_content(self, screen, elapsed):
        """Draw all victory content"""
        y_pos = 80
        
        # === MAIN TITLE (fades in 0-1 second) ===
        if elapsed < 1:
            alpha = int((elapsed / 1.0) * 255)
        else:
            alpha = 255
        
        title = self.font_huge.render("MISSION COMPLETE", True, (0, 255, 100))
        title.set_alpha(alpha)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(title, title_rect)
        
        # Underline with glow
        if elapsed >= 0.5:
            pygame.draw.line(screen, (0, 255, 100),
                           (title_rect.left, title_rect.bottom + 15),
                           (title_rect.right, title_rect.bottom + 15), 4)
        
        y_pos += 100
        
        # === INFECTION PURGED (fades in 1-2 seconds) ===
        if elapsed > 1:
            if elapsed < 2:
                alpha = int(((elapsed - 1) / 1.0) * 255)
            else:
                alpha = 255
            
            subtitle = self.font_large.render("INFECTION PURGED", True, (0, 255, 255))
            subtitle.set_alpha(alpha)
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(subtitle, subtitle_rect)
        
        y_pos += 80
        
        # === USERS FREED (fades in 2-3 seconds) ===
        if elapsed > 2:
            if elapsed < 3:
                alpha = int(((elapsed - 2) / 1.0) * 255)
            else:
                alpha = 255
            
            users_text = self.font_large.render("8,000,000,000 USERS FREED", True, (255, 255, 100))
            users_text.set_alpha(alpha)
            users_rect = users_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(users_text, users_rect)
        
        y_pos += 100
        
        # === STATISTICS (fade in 3+ seconds) ===
        if elapsed > 3:
            if elapsed < 4:
                alpha = int(((elapsed - 3) / 1.0) * 255)
            else:
                alpha = 255
            
            # Stats header
            stats_header = self.font_medium.render("═══ MISSION STATISTICS ═══", True, (0, 255, 255))
            stats_header.set_alpha(alpha)
            stats_rect = stats_header.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            screen.blit(stats_header, stats_rect)
            
            y_pos += 60
            
            # Calculate time
            eden_minutes = int(self.elapsed_time // 60)
            eden_seconds = int(self.elapsed_time % 60)
            real_hours = int((self.elapsed_time / 60) * 3)
            
            # Stats list
            stats = [
                f"Completion Time: {eden_minutes}:{eden_seconds:02d} (EDEN) | {real_hours}h (Real World)",
                f"Hostiles Eliminated: {self.enemies_killed:,}",
                f"Final Configuration Level: {self.player_level}",
                f"All 6 Layers Purged",
                f"GUARDIAN Systems: RESTORED"
            ]
            
            for i, stat in enumerate(stats):
                # Stagger the stat lines slightly
                stat_delay = 4 + (i * 0.1)
                if elapsed > stat_delay:
                    if elapsed < stat_delay + 0.3:
                        stat_alpha = int(((elapsed - stat_delay) / 0.3) * 255)
                    else:
                        stat_alpha = 255
                    
                    stat_text = self.font_small.render(stat, True, WHITE)
                    stat_text.set_alpha(stat_alpha)
                    stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                    screen.blit(stat_text, stat_rect)
                    y_pos += 45
        
        # === FINAL MESSAGE (fades in 5+ seconds) ===
        if elapsed > 5:
            if elapsed < 6:
                alpha = int(((elapsed - 5) / 1.0) * 255)
            else:
                alpha = 255
            
            # Message box
            box_width = 900
            box_height = 120
            box_x = (SCREEN_WIDTH - box_width) // 2
            box_y = SCREEN_HEIGHT - 200
            
            # Box background
            box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surface.fill((0, 100, 150, 150))
            box_surface.set_alpha(alpha)
            screen.blit(box_surface, (box_x, box_y))
            
            # Box border
            pygame.draw.rect(screen, (0, 255, 255), 
                           (box_x, box_y, box_width, box_height), 3)
            
            # Message text
            message1 = self.font_small.render("You were Protocol: Outbreak. An adaptive weapon.", True, (200, 230, 255))
            message2 = self.font_small.render("You became humanity's savior.", True, (200, 230, 255))
            
            message1.set_alpha(alpha)
            message2.set_alpha(alpha)
            
            message1_rect = message1.get_rect(center=(SCREEN_WIDTH // 2, box_y + 35))
            message2_rect = message2.get_rect(center=(SCREEN_WIDTH // 2, box_y + 75))
            
            screen.blit(message1, message1_rect)
            screen.blit(message2, message2_rect)
        
        # === CONTINUE PROMPT (always visible, pulsing) ===
        if elapsed > 4:
            pulse = abs(math.sin(elapsed * 3))
            prompt_alpha = int(150 + pulse * 105)
            
            prompt = self.font_tiny.render("Press SPACE or ENTER to return to menu", True, (150, 150, 150))
            prompt.set_alpha(prompt_alpha)
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(prompt, prompt_rect)
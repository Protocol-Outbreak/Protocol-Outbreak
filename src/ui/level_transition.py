import pygame
import time
from src.utils.constants import *

class LevelTransition:
    def __init__(self, current_level, next_level):
        self.current_level = current_level
        self.next_level = next_level
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
    def show(self, screen):
        """Display transition screen for 4-5 seconds"""
        start_time = time.time()
        duration = 4.5  # seconds
        
        clock = pygame.time.Clock()
        
        while time.time() - start_time < duration:
            # Handle events (allow closing window)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            
            # Calculate progress (0 to 1)
            progress = (time.time() - start_time) / duration
            
            # Draw background with fade effect
            screen.fill(BLACK)
            
            # Draw animated background
            self._draw_animated_background(screen, progress)
            
            # Draw level completion text
            if progress < 0.3:
                # Fade in "Level Complete"
                alpha = int((progress / 0.3) * 255)
                self._draw_text_with_fade(screen, f"Level {self.current_level} Complete!", 
                                         SCREEN_HEIGHT // 3, CLEAN_BLUE, self.font_large, alpha)
            else:
                # Show "Level Complete" fully
                self._draw_text_with_fade(screen, f"Level {self.current_level} Complete!", 
                                         SCREEN_HEIGHT // 3, CLEAN_BLUE, self.font_large, 255)
            
            # Draw next level text
            if progress > 0.4:
                alpha = int(((progress - 0.4) / 0.6) * 255)
                self._draw_text_with_fade(screen, f"Entering Level {self.next_level}...", 
                                         SCREEN_HEIGHT // 2, CORRUPTION_PURPLE, self.font_medium, alpha)
            
            # Draw loading bar
            if progress > 0.5:
                self._draw_loading_bar(screen, (progress - 0.5) / 0.5)
            
            # Draw tips
            if progress > 0.6:
                alpha = int(((progress - 0.6) / 0.4) * 255)
                tip = "Tip: Use cover to your advantage!"
                self._draw_text_with_fade(screen, tip, 
                                         SCREEN_HEIGHT * 2 // 3 + 80, UI_CYAN, self.font_small, alpha)
            
            pygame.display.flip()
            clock.tick(60)
        
        return True
    
    def _draw_animated_background(self, screen, progress):
        """Draw animated grid background"""
        grid_size = 50
        offset = int(progress * 50)
        
        for x in range(-grid_size, SCREEN_WIDTH + grid_size, grid_size):
            pygame.draw.line(screen, (20, 40, 60), 
                           (x + offset, 0), (x + offset, SCREEN_HEIGHT), 1)
        
        for y in range(-grid_size, SCREEN_HEIGHT + grid_size, grid_size):
            pygame.draw.line(screen, (20, 40, 60), 
                           (0, y + offset), (SCREEN_WIDTH, y + offset), 1)
    
    def _draw_loading_bar(self, screen, progress):
        """Draw loading progress bar"""
        bar_width = 400
        bar_height = 30
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT * 2 // 3
        
        # Background
        pygame.draw.rect(screen, UI_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Progress fill
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, CORRUPTION_PURPLE, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Percentage text
        percent_text = self.font_small.render(f"{int(progress * 100)}%", True, WHITE)
        text_rect = percent_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(percent_text, text_rect)
    
    def _draw_text_with_fade(self, screen, text, y_pos, color, font, alpha):
        """Draw text with fade effect"""
        text_surface = font.render(text, True, color)
        text_surface.set_alpha(alpha)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(text_surface, text_rect)
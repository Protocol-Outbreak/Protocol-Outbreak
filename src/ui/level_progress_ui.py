import pygame
from src.utils.constants import *

class LevelProgressUI:
    """UI for displaying level progress and next level button"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.button_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 18)
        self.next_level_button_rect = None
    
    def draw_enemy_progress_bar(self, screen, enemies_remaining, initial_enemy_count, level_complete):
        """Draw enemy kill progress bar at top of screen"""
        bar_width = 500
        bar_height = 25
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = 20
        
        # Calculate progress
        enemies_killed = initial_enemy_count - enemies_remaining
        if initial_enemy_count > 0:
            progress = enemies_killed / initial_enemy_count
        else:
            progress = 0
        
        # Background
        pygame.draw.rect(screen, UI_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Progress fill
        fill_width = int(bar_width * progress)
        color = CLEAN_BLUE if progress < 1.0 else (0, 255, 0)  # Green when complete
        pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Text
        text = f"Enemies: {enemies_killed}/{initial_enemy_count}"
        if level_complete:
            text = "ALL ENEMIES ELIMINATED!"
        
        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))
        screen.blit(text_surface, text_rect)
    
    def draw_next_level_button(self, screen):
        """Draw button to proceed to next level"""
        button_width = 300
        button_height = 60
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = SCREEN_HEIGHT // 2 - button_height // 2
        
        # Store button rect for click detection
        self.next_level_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Check if mouse is hovering
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.next_level_button_rect.collidepoint(mouse_pos)
        
        # Draw button with hover effect
        button_color = CORRUPTION_PURPLE if is_hovering else CLEAN_BLUE
        pygame.draw.rect(screen, button_color, self.next_level_button_rect)
        pygame.draw.rect(screen, WHITE, self.next_level_button_rect, 3)
        
        # Draw button text
        button_text = self.button_font.render("PROCEED TO NEXT LEVEL", True, WHITE)
        text_rect = button_text.get_rect(center=self.next_level_button_rect.center)
        screen.blit(button_text, text_rect)
        
        # Draw instruction text below button
        instruction = self.small_font.render("Click to continue", True, UI_CYAN)
        inst_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, button_y + button_height + 30))
        screen.blit(instruction, inst_rect)
    
    def check_button_click(self, mouse_pos):
        """Check if next level button was clicked"""
        if self.next_level_button_rect:
            return self.next_level_button_rect.collidepoint(mouse_pos)
        return False
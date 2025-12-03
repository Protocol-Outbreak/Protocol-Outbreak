import pygame
import math
from src.utils.constants import *


class GameWonScreen:
    """Screen displayed when player completes the final level (Level 4)"""
    
    def __init__(self, final_score, levels_completed=5):
        self.final_score = final_score
        self.levels_completed = levels_completed
        self.font_title = pygame.font.Font(None, 80)
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Button rects
        self.menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 120, 300, 60)
        self.restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 50, 300, 60)
        
        # Animation
        self.elapsed_time = 0
        self.particle_system = []
        self.create_confetti()
    
    def create_confetti(self):
        """Create confetti particles for celebration"""
        import random
        for _ in range(50):
            self.particle_system.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(-50, SCREEN_HEIGHT // 2),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(2, 6),
                'color': random.choice([
                    (255, 0, 0),      # Red
                    (0, 255, 0),      # Green
                    (0, 0, 255),      # Blue
                    (255, 255, 0),    # Yellow
                    (0, 255, 255),    # Cyan
                    (255, 0, 255)     # Magenta
                ]),
                'size': random.randint(3, 8)
            })
    
    def update(self):
        """Update confetti animation"""
        self.elapsed_time += 1/60.0
        
        # Update particles
        for particle in self.particle_system[:]:
            particle['y'] += particle['vy']
            particle['x'] += particle['vx']
            particle['vy'] += 0.2  # Gravity
            
            # Remove if off-screen
            if particle['y'] > SCREEN_HEIGHT:
                self.particle_system.remove(particle)
        
        # Create new confetti occasionally
        if len(self.particle_system) < 30 and self.elapsed_time < 10:
            import random
            self.particle_system.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': -10,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(2, 6),
                'color': random.choice([
                    (255, 0, 0), (0, 255, 0), (0, 0, 255),
                    (255, 255, 0), (0, 255, 255), (255, 0, 255)
                ]),
                'size': random.randint(3, 8)
            })
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if self.menu_button_rect.collidepoint(mouse_pos):
                    return 'menu'
                elif self.restart_button_rect.collidepoint(mouse_pos):
                    return 'restart'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'menu'
        
        return None
    
    def draw(self, screen):
        """Draw the game won screen"""
        screen.fill(BLACK)
        
        # Draw confetti
        for particle in self.particle_system:
            pygame.draw.circle(
                screen,
                particle['color'],
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Title - "VICTORY"
        title_text = self.font_title.render("VICTORY", True, (0, 255, 100))
        title_shadow = self.font_title.render("VICTORY", True, (0, 100, 50))
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 4, 60 + 4))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60))
        
        # Subtitle
        subtitle_text = self.font_normal.render("You Have Defeated the Corruption", True, (0, 200, 255))
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 160))
        
        # Stats box
        box_y = 240
        box_height = 200
        box_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 300,
            box_y,
            600,
            box_height
        )
        
        # Draw box background
        box_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (20, 60, 100, 180), (0, 0, box_rect.width, box_rect.height))
        pygame.draw.rect(box_surface, (0, 200, 255), (0, 0, box_rect.width, box_rect.height), 3)
        screen.blit(box_surface, box_rect.topleft)
        
        # Stats text
        stats_y = box_y + 30
        
        # Levels Completed
        levels_text = self.font_normal.render(f"Levels Completed: {self.levels_completed}/5", True, (0, 255, 100))
        screen.blit(levels_text, (SCREEN_WIDTH // 2 - levels_text.get_width() // 2, stats_y))
        
        # Final Score
        stats_y += 60
        score_label = self.font_normal.render("Final Score:", True, (100, 255, 200))
        score_value = self.font_large.render(f"{self.final_score}", True, (0, 255, 100))
        screen.blit(score_label, (SCREEN_WIDTH // 2 - 300, stats_y))
        screen.blit(score_value, (SCREEN_WIDTH // 2 + 50, stats_y - 5))
        
        # Message
        stats_y = box_y + box_height + 20
        message_text = self.font_normal.render("You have successfully cleansed the neural network!", True, (255, 255, 255))
        screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, stats_y))
        
        # Buttons
        # Menu Button
        menu_hovered = self.menu_button_rect.collidepoint(pygame.mouse.get_pos())
        menu_color = (0, 200, 255) if menu_hovered else (0, 150, 200)
        pygame.draw.rect(screen, menu_color, self.menu_button_rect)
        pygame.draw.rect(screen, (100, 255, 255), self.menu_button_rect, 2)
        menu_text = self.font_small.render("RETURN TO MENU", True, (0, 0, 0))
        screen.blit(menu_text, (
            self.menu_button_rect.centerx - menu_text.get_width() // 2,
            self.menu_button_rect.centery - menu_text.get_height() // 2
        ))
        
        # Restart Button
        restart_hovered = self.restart_button_rect.collidepoint(pygame.mouse.get_pos())
        restart_color = (0, 200, 0) if restart_hovered else (0, 150, 0)
        pygame.draw.rect(screen, restart_color, self.restart_button_rect)
        pygame.draw.rect(screen, (100, 255, 100), self.restart_button_rect, 2)
        restart_text = self.font_small.render("PLAY AGAIN", True, (0, 0, 0))
        screen.blit(restart_text, (
            self.restart_button_rect.centerx - restart_text.get_width() // 2,
            self.restart_button_rect.centery - restart_text.get_height() // 2
        ))
     
    def run(self, screen):
        """Run the game won screen loop"""
        clock = pygame.time.Clock()
        
        while True:
            self.update()
            result = self.handle_events()
            
            if result == 'menu':
                return 'menu'
            elif result == 'restart':
                return 'restart'
            elif result == 'quit':
                return None
            
            self.draw(screen)
            pygame.display.flip()
            clock.tick(60)
"""
Path Selection UI - Appears at Level 5
Player chooses their tank progression path permanently
"""
import pygame
from src.utils.constants import *
from src.utils.enums import TankPath

class PathSelectionUI:
    """Full-screen path selection interface"""
    
    def __init__(self, screen):
        self.screen = screen
        self.selected_path = None
        self.hovered_path = None
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.path_font = pygame.font.Font(None, 42)
        self.desc_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Path data
        self.paths = {
            TankPath.GUNNER: {
                "name": "GUNNER PATH",
                "key": "1",
                "progression": "Twin -> Triplet -> Penta Shot",
                "playstyle": "Area control, bullet spam, crowd clearing",
                "color": (100, 255, 100)
            },
            TankPath.SNIPER: {
                "name": "SNIPER PATH",
                "key": "2",
                "progression": "Sniper -> Marksman -> Railgun",
                "playstyle": "Long range, precision, boss killer",
                "color": (100, 150, 255)
            },
            TankPath.SPRAYER: {
                "name": "SPRAYER PATH",
                "key": "3",
                "progression": "Machine Gun -> Gatling -> Minigun",
                "playstyle": "Suppressive fire, maximum DPS",
                "color": (255, 150, 100)
            }
        }
        
        # Calculate box positions
        self.box_width = 350
        self.box_height = 200
        self.box_spacing = 40
        self.total_width = (self.box_width * 3) + (self.box_spacing * 2)
        self.start_x = (SCREEN_WIDTH - self.total_width) // 2
        self.box_y = 280
    
    def show(self):
        """
        Display path selection screen and wait for choice
        Returns: TankPath enum value
        """
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Player closed window
                
                if event.type == pygame.KEYDOWN:
                    # Check for path selection keys
                    if event.key == pygame.K_1:
                        self.selected_path = TankPath.GUNNER
                        waiting = False
                    elif event.key == pygame.K_2:
                        self.selected_path = TankPath.SNIPER
                        waiting = False
                    elif event.key == pygame.K_3:
                        self.selected_path = TankPath.SPRAYER
                        waiting = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if clicked on a path box
                    mx, my = event.pos
                    clicked_path = self.get_clicked_path(mx, my)
                    if clicked_path:
                        self.selected_path = clicked_path
                        waiting = False
            
            # Update hover state
            mx, my = pygame.mouse.get_pos()
            self.hovered_path = self.get_clicked_path(mx, my)
            
            # Draw
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        return self.selected_path
    
    def get_clicked_path(self, mx, my):
        """Check if mouse is over a path box"""
        for i, path in enumerate([TankPath.GUNNER, TankPath.SNIPER, TankPath.SPRAYER]):
            box_x = self.start_x + (i * (self.box_width + self.box_spacing))
            box_rect = pygame.Rect(box_x, self.box_y, self.box_width, self.box_height)
            
            if box_rect.collidepoint(mx, my):
                return path
        
        return None
    
    def draw(self):
        """Draw the path selection screen"""
        # Dark overlay
        self.screen.fill((10, 15, 25))
        
        # Animated grid background
        self.draw_animated_grid()
        
        # Title
        title = self.title_font.render("CONFIGURATION PATH", True, (0, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.subtitle_font.render("LEVEL 5 REACHED - Choose Your Specialization", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Warning
        warning = self.small_font.render("This choice is permanent", True, (255, 200, 0))
        warning_rect = warning.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(warning, warning_rect)
        
        # Draw path boxes
        for i, (path, data) in enumerate(self.paths.items()):
            self.draw_path_box(i, path, data)
        
        # Instructions
        instr = self.small_font.render("Press 1-3 or Click to Choose", True, (150, 150, 150))
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(instr, instr_rect)
    
    def draw_animated_grid(self):
        """Draw subtle animated background"""
        grid_size = 50
        time = pygame.time.get_ticks()
        offset = (time // 50) % grid_size
        
        for x in range(-grid_size, SCREEN_WIDTH + grid_size, grid_size):
            pygame.draw.line(self.screen, (20, 30, 50), 
                           (x + offset, 0), (x + offset, SCREEN_HEIGHT), 1)
        
        for y in range(-grid_size, SCREEN_HEIGHT + grid_size, grid_size):
            pygame.draw.line(self.screen, (20, 30, 50), 
                           (0, y + offset), (SCREEN_WIDTH, y + offset), 1)
    
    def draw_path_box(self, index, path, data):
        """Draw a single path selection box"""
        box_x = self.start_x + (index * (self.box_width + self.box_spacing))
        box_y = self.box_y
        
        # Check if hovered
        is_hovered = (self.hovered_path == path)
        
        # Box background
        box_surface = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        if is_hovered:
            box_surface.fill((40, 60, 80, 220))
        else:
            box_surface.fill((25, 35, 50, 200))
        
        self.screen.blit(box_surface, (box_x, box_y))
        
        # Box border (colored by path)
        border_color = data["color"] if is_hovered else (100, 100, 100)
        border_width = 3 if is_hovered else 2
        pygame.draw.rect(self.screen, border_color, 
                        (box_x, box_y, self.box_width, self.box_height), 
                        border_width)
        
        # Key indicator
        key_size = 30
        key_x = box_x + 15
        key_y = box_y + 15
        pygame.draw.rect(self.screen, data["color"], 
                        (key_x, key_y, key_size, key_size))
        key_text = self.path_font.render(data["key"], True, (20, 20, 40))
        key_rect = key_text.get_rect(center=(key_x + key_size // 2, key_y + key_size // 2))
        self.screen.blit(key_text, key_rect)
        
        # Path name
        name = self.path_font.render(data["name"], True, data["color"])
        name_rect = name.get_rect(center=(box_x + self.box_width // 2, box_y + 40))
        self.screen.blit(name, name_rect)
        
        # Progression
        prog = self.desc_font.render(data["progression"], True, WHITE)
        prog_rect = prog.get_rect(center=(box_x + self.box_width // 2, box_y + 85))
        self.screen.blit(prog, prog_rect)
        
        # Playstyle (word-wrapped)
        self.draw_wrapped_text(
            data["playstyle"],
            box_x + 20,
            box_y + 120,
            self.box_width - 40,
            self.small_font,
            (200, 200, 200)
        )
    
    def draw_wrapped_text(self, text, x, y, max_width, font, color):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            self.screen.blit(line_surface, (x, y + (i * 25)))
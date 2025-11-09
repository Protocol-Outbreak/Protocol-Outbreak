# Game Over Screen for GAME2500 Final Project
import pygame as pg
import os

WIDTH, HEIGHT = 1280, 720
FPS = 60

# Color scheme
DARK_BG = (8, 15, 30)
GRID_COLOR = (20, 40, 70)
CYAN = (0, 255, 255)
BRIGHT_CYAN = (100, 255, 255)
RED = (255, 50, 100)
BRIGHT_RED = (255, 100, 120)
WHITE = (255, 255, 255)
GRAY = (150, 160, 170)

class GameOverScreen:
    def __init__(self, score=0):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.score = score
        
        # Load custom fonts
        try:
            font_path = os.path.join(os.path.dirname(__file__), "fonts", "Sterion-BLLId.ttf")
            italic_path = os.path.join(os.path.dirname(__file__), "fonts", "SterionItalic-R99PA.ttf")
            
            self.title_font = pg.font.Font(font_path, 65)
            self.subtitle_font = pg.font.Font(italic_path, 22)
            self.heading_font = pg.font.Font(font_path, 26)
            self.score_font = pg.font.Font(font_path, 40)
        except:
            print("Custom font not found, using default")
            self.title_font = pg.font.SysFont("arial", 65, bold=True)
            self.subtitle_font = pg.font.SysFont("arial", 22, italic=True)
            self.heading_font = pg.font.SysFont("arial", 26, bold=True)
            self.score_font = pg.font.SysFont("arial", 40, bold=True)
        
        # Create grid background
        self.bg_image = self.create_grid_background()
        
        # Laser scan animation
        self.laser_y = 0
        self.laser_speed = 200
        
        # Buttons
        self.retry_button = pg.Rect(0, 0, 360, 50)
        self.retry_button.center = (WIDTH // 2, HEIGHT // 2 + 180)
        
        self.menu_button = pg.Rect(0, 0, 360, 50)
        self.menu_button.center = (WIDTH // 2, HEIGHT // 2 + 250)

    def create_grid_background(self):
        """Create a dark blue grid background"""
        surface = pg.Surface((WIDTH, HEIGHT))
        surface.fill(DARK_BG)
        
        # Draw grid lines
        grid_spacing = 50
        for x in range(0, WIDTH, grid_spacing):
            pg.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, grid_spacing):
            pg.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 1)
        
        return surface

    def run(self):
        """Returns: 'retry' to restart game, 'menu' to go to main menu, None to quit"""
        while True:
            dt = self.clock.tick(FPS) / 1000
            
            # Update laser position
            self.laser_y += self.laser_speed * dt
            if self.laser_y > HEIGHT:
                self.laser_y = 0
            
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    return None
                if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    return 'menu'
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = pg.mouse.get_pos()
                    if self.retry_button.collidepoint(mx, my):
                        return 'retry'
                    elif self.menu_button.collidepoint(mx, my):
                        return 'menu'

            self.draw()
            pg.display.flip()

    def draw_laser_scan(self):
        """Draw animated scanning laser effect"""
        pg.draw.line(self.screen, BRIGHT_CYAN, (0, int(self.laser_y)), (WIDTH, int(self.laser_y)), 2)
        
        glow_range = 15
        for offset in range(1, glow_range):
            if offset < glow_range - 1:
                if self.laser_y - offset >= 0:
                    pg.draw.line(self.screen, (0, 150, 180), 
                               (0, int(self.laser_y - offset)), 
                               (WIDTH, int(self.laser_y - offset)), 1)
                if self.laser_y + offset <= HEIGHT:
                    pg.draw.line(self.screen, (0, 150, 180), 
                               (0, int(self.laser_y + offset)), 
                               (WIDTH, int(self.laser_y + offset)), 1)

    def draw(self):
        # Draw background
        self.screen.blit(self.bg_image, (0, 0))
        
        # Draw laser scan effect
        self.draw_laser_scan()
        
        # Draw semi-transparent panel - MADE BIGGER
        panel_rect = pg.Rect(WIDTH // 2 - 240, HEIGHT // 2 - 200, 480, 500)
        panel_surface = pg.Surface((panel_rect.width, panel_rect.height), pg.SRCALPHA)
        panel_surface.fill((5, 10, 25, 240))
        
        # Draw red glowing border
        pg.draw.rect(panel_surface, RED, (0, 0, panel_rect.width, panel_rect.height), 3)
        # Outer glow
        for i in range(1, 8):
            glow_color = (255, 50, 100, max(0, 80 - i * 10))
            glow_rect = pg.Rect(-i, -i, panel_rect.width + i*2, panel_rect.height + i*2)
            pg.draw.rect(panel_surface, glow_color, glow_rect, 2)
        
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # Title
        title = self.title_font.render("SYSTEM FAILURE", True, RED)
        title_shadow = self.title_font.render("SYSTEM FAILURE", True, (150, 30, 50))
        self.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, HEIGHT//2 - 150))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 153))
            
        # Subtitle messages
        subtitle1 = self.subtitle_font.render("The corruption overwhelmed your systems.", True, WHITE)
        subtitle2 = self.subtitle_font.render("Humanity's last hope has fallen.", True, CYAN)
        self.screen.blit(subtitle1, (WIDTH//2 - subtitle1.get_width()//2, HEIGHT//2 - 80))
        self.screen.blit(subtitle2, (WIDTH//2 - subtitle2.get_width()//2, HEIGHT//2 - 50))
        
        # Score box
        score_box_rect = pg.Rect(WIDTH // 2 - 165, HEIGHT // 2 - 10, 330, 100)
        pg.draw.rect(self.screen, (10, 20, 35), score_box_rect)
        pg.draw.rect(self.screen, RED, score_box_rect, 2)
        
        score_label = self.heading_font.render("FINAL SCORE", True, WHITE)
        score_value = self.score_font.render(str(self.score), True, RED)
        
        self.screen.blit(score_label, (WIDTH//2 - score_label.get_width()//2, HEIGHT//2 + 5))
        self.screen.blit(score_value, (WIDTH//2 - score_value.get_width()//2, HEIGHT//2 + 35))
        
        # Buttons
        mx, my = pg.mouse.get_pos()
        
        # Retry button
        retry_hovered = self.retry_button.collidepoint(mx, my)
        retry_color = BRIGHT_CYAN if retry_hovered else CYAN
        pg.draw.rect(self.screen, retry_color, self.retry_button)
        pg.draw.rect(self.screen, WHITE, self.retry_button, 2)
        retry_text = self.heading_font.render("RETRY MISSION", True, DARK_BG)
        self.screen.blit(retry_text, (self.retry_button.centerx - retry_text.get_width()//2,
                                      self.retry_button.centery - retry_text.get_height()//2))
        
        # Menu button
        menu_hovered = self.menu_button.collidepoint(mx, my)
        pg.draw.rect(self.screen, (30, 35, 45) if not menu_hovered else (50, 55, 65), self.menu_button)
        pg.draw.rect(self.screen, WHITE, self.menu_button, 2)
        menu_text = self.heading_font.render("MAIN MENU", True, WHITE)
        self.screen.blit(menu_text, (self.menu_button.centerx - menu_text.get_width()//2,
                                     self.menu_button.centery - menu_text.get_height()//2))


if __name__ == "__main__":
    game_over = GameOverScreen(score=1337)
    result = game_over.run()
    print(f"User selected: {result}")
# Menu UI for GAME2500 Final Project - Neural Cleanse Theme
import sys
import pygame as pg
import os
import random
import math

WIDTH, HEIGHT = 1280, 720
FPS = 60

# Color scheme
DARK_BG = (8, 15, 30)
GRID_COLOR = (20, 40, 70)
CYAN = (0, 255, 255)
BRIGHT_CYAN = (100, 255, 255)
DARK_CYAN = (0, 180, 200)
PURPLE = (180, 100, 255)
RED = (255, 50, 100)
WHITE = (255, 255, 255)
GRAY = (150, 160, 170)

class NanoDrone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_size = random.randint(6, 8)
        self.speed_x = random.uniform(-80, 80)
        self.speed_y = random.uniform(-60, 60)
        self.color = random.choice([CYAN, BRIGHT_CYAN, PURPLE])
        
        # Pulsing animation for center light
        self.pulse_timer = random.uniform(0, 3.14)
        self.pulse_speed = random.uniform(3, 5)
        
    def update(self, dt):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt
        
        # Wrap around screen
        if self.x < -20:
            self.x = WIDTH + 20
        elif self.x > WIDTH + 20:
            self.x = -20
        if self.y < -20:
            self.y = HEIGHT + 20
        elif self.y > HEIGHT + 20:
            self.y = -20
        
        # Update pulse animation
        self.pulse_timer += self.pulse_speed * dt
    
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        size = self.base_size
        
        # Draw propeller glow effects (4 corners)
        glow_offset = size + 3
        glow_size = 4
        glow_color = (*self.color, 100)  # Semi-transparent
        
        # Create glow surface for transparency
        glow_surf = pg.Surface((glow_size * 3, glow_size * 3), pg.SRCALPHA)
        
        # Top-left propeller glow
        self._draw_glow(screen, x - glow_offset, y - glow_offset, glow_size, glow_color)
        # Top-right propeller glow
        self._draw_glow(screen, x + glow_offset, y - glow_offset, glow_size, glow_color)
        # Bottom-left propeller glow
        self._draw_glow(screen, x - glow_offset, y + glow_offset, glow_size, glow_color)
        # Bottom-right propeller glow
        self._draw_glow(screen, x + glow_offset, y + glow_offset, glow_size, glow_color)
        
        # Draw arms/connectors (cross shape)
        arm_length = size + 4
        arm_color = (*self.color, 80)
        
        # Horizontal arm
        arm_surf = pg.Surface((arm_length * 2, 2), pg.SRCALPHA)
        arm_surf.fill(arm_color)
        screen.blit(arm_surf, (x - arm_length, y - 1))
        
        # Vertical arm
        arm_surf_v = pg.Surface((2, arm_length * 2), pg.SRCALPHA)
        arm_surf_v.fill(arm_color)
        screen.blit(arm_surf_v, (x - 1, y - arm_length))
        
        # Draw drone body (rotated square/diamond)
        body_points = [
            (x, y - size),      # Top
            (x + size, y),      # Right
            (x, y + size),      # Bottom
            (x - size, y)       # Left
        ]
        
        # Body with border
        pg.draw.polygon(screen, self.color, body_points)
        pg.draw.polygon(screen, self.color, body_points, 1)  # Border
        
        # Main glow around body
        main_glow_surf = pg.Surface((size * 6, size * 6), pg.SRCALPHA)
        pg.draw.circle(main_glow_surf, (*self.color, 30), (size * 3, size * 3), size * 3)
        screen.blit(main_glow_surf, (x - size * 3, y - size * 3))
        
        # Center pulsing light (accent color)
        pulse_intensity = (math.sin(self.pulse_timer) + 1) / 2  # 0 to 1
        center_size = int(2 + pulse_intensity * 2)
        accent_color = (255, 150, 255)  # Purple/pink accent
        
        # Pulsing glow
        pulse_glow_surf = pg.Surface((center_size * 6, center_size * 6), pg.SRCALPHA)
        glow_alpha = int(100 + pulse_intensity * 100)
        pg.draw.circle(pulse_glow_surf, (*accent_color, glow_alpha), 
                      (center_size * 3, center_size * 3), center_size * 3)
        screen.blit(pulse_glow_surf, (x - center_size * 3, y - center_size * 3))
        
        # Center dot
        pg.draw.circle(screen, accent_color, (x, y), center_size)
    
    def _draw_glow(self, screen, x, y, size, color):
        """Helper to draw a glowing circle"""
        glow_surf = pg.Surface((size * 4, size * 4), pg.SRCALPHA)
        pg.draw.circle(glow_surf, color, (size * 2, size * 2), size * 2)
        pg.draw.circle(glow_surf, color, (size * 2, size * 2), size, 0)
        screen.blit(glow_surf, (x - size * 2, y - size * 2))

class MenuApp:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Protocol: Outbreak")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        
        # Load custom fonts
        try:
            font_path = os.path.join(os.path.dirname(__file__), "fonts", "Sterion-BLLId.ttf")
            italic_path = os.path.join(os.path.dirname(__file__), "fonts", "SterionItalic-R99PA.ttf")
            
            self.title_font = pg.font.Font(font_path, 72)
            self.subtitle_font = pg.font.Font(italic_path, 22)
            self.heading_font = pg.font.Font(font_path, 26)
            self.body_font = pg.font.Font(font_path, 17)
            self.small_font = pg.font.Font(italic_path, 15)
            self.dev_font = pg.font.SysFont("arial", 20)
            
        except:
            print("Custom font not found, using default")
            self.title_font = pg.font.SysFont("arial", 72, bold=True)
            self.subtitle_font = pg.font.SysFont("arial", 22, italic=True)
            self.heading_font = pg.font.SysFont("arial", 26, bold=True)
            self.body_font = pg.font.SysFont("arial", 17)
            self.small_font = pg.font.SysFont("arial", 15, italic=True)
            self.dev_font = pg.font.SysFont("arial", 20)
        
        # Create grid background
        self.bg_image = self.create_grid_background()
        
        # Laser scan animation
        self.laser_y = 0
        self.laser_speed = 200  # pixels per second
        
        # Main button
        self.start_button = pg.Rect(0, 0, 500, 60)
        self.start_button.center = (WIDTH // 2, HEIGHT - 100)  # Moved up slightly

        # Nano drones
        import random
        self.drones = []
        for _ in range(15):  # Spawn 15 drones
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            self.drones.append(NanoDrone(x, y))
        
        self.started = False

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
        while True:
            dt = self.clock.tick(FPS) / 1000
            
            # Update laser position
            self.laser_y += self.laser_speed * dt
            if self.laser_y > HEIGHT:
                self.laser_y = 0
            
            # ADD THIS - Update drones
            for drone in self.drones:
                drone.update(dt)
            
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    return False
                if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    return False
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = pg.mouse.get_pos()
                    if self.start_button.collidepoint(mx, my):
                        return True

            self.draw_menu()
            pg.display.flip()

    def draw_laser_scan(self):
        """Draw animated scanning laser effect"""
        # Main laser line (bright cyan)
        pg.draw.line(self.screen, BRIGHT_CYAN, (0, int(self.laser_y)), (WIDTH, int(self.laser_y)), 2)
        
        # Glow effect - draw fading lines above and below
        glow_range = 15
        for offset in range(1, glow_range):
            alpha = 255 - (offset * 17)  # Fade out
            glow_color = (0, 255, 255, max(0, alpha))
            
            # Create surface for glow line with alpha
            if offset < glow_range - 1:
                # Above
                if self.laser_y - offset >= 0:
                    pg.draw.line(self.screen, (0, 150, 180), 
                               (0, int(self.laser_y - offset)), 
                               (WIDTH, int(self.laser_y - offset)), 1)
                # Below
                if self.laser_y + offset <= HEIGHT:
                    pg.draw.line(self.screen, (0, 150, 180), 
                               (0, int(self.laser_y + offset)), 
                               (WIDTH, int(self.laser_y + offset)), 1)

    def draw_menu(self):
        # Draw background
        self.screen.blit(self.bg_image, (0, 0))
        
        # Draw drones FIRST (behind everything)
        for drone in self.drones:
            drone.draw(self.screen)
        
        # Draw laser scan
        self.draw_laser_scan()
        
        # ... rest of your draw code
        
        # Draw laser scan effect (behind everything)
        self.draw_laser_scan()
        
        # Draw semi-transparent overlay panel - MADE TALLER
        panel_rect = pg.Rect(50, 40, WIDTH - 100, HEIGHT - 75)  # Changed from HEIGHT - 80
        panel_surface = pg.Surface((panel_rect.width, panel_rect.height), pg.SRCALPHA)
        panel_surface.fill((5, 10, 25, 220))
        
        # Draw border
        pg.draw.rect(panel_surface, CYAN, (0, 0, panel_rect.width, panel_rect.height), 2)
        self.screen.blit(panel_surface, panel_rect.topleft)
        
        # Title
        title = self.title_font.render("PROTOCOL: OUTBREAK", True, CYAN)
        title_shadow = self.title_font.render("PROTOCOL: OUTBREAK", True, DARK_CYAN)
        self.screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 73))
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        
        # Subtitle
        subtitle = self.subtitle_font.render("You are humanity's failsafe — a nano drone sent into the machine that once saved us.", True, WHITE)
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 150))
        
        # Mission Briefing Section
        y_offset = 185
        
        heading = self.heading_font.render("MISSION BRIEFING", True, WHITE)
        self.screen.blit(heading, (100, y_offset))
        y_offset += 40
        
        briefing_text = [
            "The AI's neural nodes have been corrupted. Each level represents a deeper layer in its",
            "consciousness. Your objective: infiltrate, survive, and destroy all infection points."
        ]
        for line in briefing_text:
            text = self.body_font.render(line, True, WHITE)
            self.screen.blit(text, (100, y_offset))
            y_offset += 26
        
        # Objectives Section
        y_offset += 12
        objectives_heading = self.heading_font.render("OBJECTIVES", True, PURPLE)
        self.screen.blit(objectives_heading, (100, y_offset))
        y_offset += 35
        
        objectives = [
            ("Eliminate all ", "Infection Nodes", " to progress"),
            ("Survive waves of ", "Rogue Defense Units", ""),
            ("Maintain system integrity (your health)", "", "")
        ]
        
        for prefix, highlight, suffix in objectives:
            # Draw bullet point
            pg.draw.circle(self.screen, RED, (115, y_offset + 8), 4)
            
            x_pos = 140
            if prefix:
                t1 = self.body_font.render(prefix, True, WHITE)
                self.screen.blit(t1, (x_pos, y_offset))
                x_pos += t1.get_width()
            if highlight:
                t2 = self.body_font.render(highlight, True, RED)
                self.screen.blit(t2, (x_pos, y_offset))
                x_pos += t2.get_width()
            if suffix:
                t3 = self.body_font.render(suffix, True, WHITE)
                self.screen.blit(t3, (x_pos, y_offset))
            
            y_offset += 26
        
        # Controls Section
        y_offset += 12
        controls_heading = self.heading_font.render("CONTROLS", True, CYAN)
        self.screen.blit(controls_heading, (100, y_offset))
        y_offset += 35
        
        controls = [
            ("WASD/Arrow Keys", "Movement"),
            ("Mouse/Space", "Aim & Fire")
        ]
        
        for key, action in controls:
            # Key box - make wider for "Mouse/Space"
            box_width = 140 # if key == "Mouse/Space" else 80
            key_box = pg.Rect(115, y_offset - 5, box_width, 28)
            pg.draw.rect(self.screen, DARK_CYAN, key_box)
            pg.draw.rect(self.screen, CYAN, key_box, 2)
            
            key_text = self.body_font.render(key, True, WHITE)
            self.screen.blit(key_text, (key_box.centerx - key_text.get_width()//2, key_box.centery - key_text.get_height()//2))
            
            action_text = self.body_font.render(action, True, WHITE)
            self.screen.blit(action_text, (115 + box_width + 20, y_offset))
            
            y_offset += 35
        
        # Enemy Types Section
        y_offset += 8
        enemy_heading = self.heading_font.render("ENEMY TYPES", True, PURPLE)
        self.screen.blit(enemy_heading, (100, y_offset))
        y_offset += 35
        
        enemy_types = [
            ("Fast Units", " - High speed, low health", RED),
            ("Basic Units", " - Balanced threat", (255, 150, 50)),
            ("Tank Units", " - Slow but heavily armored", (100, 150, 255))
        ]
        
        for name, desc, color in enemy_types:
            # Draw colored circle bullet
            pg.draw.circle(self.screen, color, (115, y_offset + 8), 5)
            
            name_text = self.body_font.render(name, True, WHITE)
            self.screen.blit(name_text, (140, y_offset))
            
            desc_text = self.body_font.render(desc, True, WHITE)
            self.screen.blit(desc_text, (140 + name_text.get_width(), y_offset))
            
            y_offset += 26
        
        # Start Button
        mx, my = pg.mouse.get_pos()
        hovered = self.start_button.collidepoint(mx, my)

        # Create a slightly larger button rect if hovered (pop-out effect)
        if hovered:
            button_rect = self.start_button.inflate(20, 8)  # Make it 20px wider, 8px taller
        else:
            button_rect = self.start_button

        button_color = BRIGHT_CYAN if hovered else CYAN
        pg.draw.rect(self.screen, button_color, button_rect)
        pg.draw.rect(self.screen, WHITE, button_rect, 2)

        button_text = self.heading_font.render("INITIATE INFILTRATION", True, DARK_BG)
        self.screen.blit(button_text, (button_rect.centerx - button_text.get_width()//2, 
                                    button_rect.centery - button_text.get_height()//2))
                
        # Warning at bottom
        warning = self.small_font.render("Warning: As you descend deeper, the corruption intensifies. Enemies adapt. Stay alert.", True, (255, 255, 255))
        self.screen.blit(warning, (WIDTH//2 - warning.get_width()//2, HEIGHT - 63))  # Moved up

        # Developers section at very bottom
        developers = ["Jason He", "Cristian Gutierrez Espinoza", "Joshua Paulino Ozuna", "Ian Khanna"]
        dev_text = "Game created by: " + ", ".join(developers)

        # Create semi-transparent bar at bottom
        bar_height = 42
        bar = pg.Surface((WIDTH, bar_height), pg.SRCALPHA)
        bar.fill((0, 0, 0, 0))  # LAST NUMBER IS THE TRANSPARENCY
        self.screen.blit(bar, (0, HEIGHT - bar_height))

        dev_label = self.dev_font.render(dev_text, True, WHITE)
        self.screen.blit(dev_label, (WIDTH//2 - dev_label.get_width()//2, HEIGHT - bar_height//2 - dev_label.get_height()//2 + 2))


if __name__ == "__main__":
    app = MenuApp()

    app.run()

# Menu UI only for GAME2500 Final Project
# This code is only for the menu UI portion of the final project. Once the "Start" button is pressed, implement the code that begins the game.

import sys
import pygame as pg
import os

WIDTH, HEIGHT = 1280, 720
FPS = 120

BG = (250, 251, 255)
TITLE_COLOR = (44, 62, 80)
SUB_COLOR = (99, 110, 114)
BTN = (52, 152, 219)
BTN_HOVER = (41, 128, 185)
WHITE = (255, 255, 255)
RED = (228, 8, 10)
RED_HOVER = (245, 70, 72)

class MenuApp:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Menu UI Only")
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 30)
        self.big = pg.font.SysFont("consolas", 32, bold=True)
        self.small = pg.font.SysFont("javanese text", 20)
        self.state = "menu"

        # Load background image
        self.bg_image = pg.image.load(os.path.join(os.path.dirname(__file__), "background.png")).convert()
        self.bg_image = pg.transform.scale(self.bg_image, (WIDTH, HEIGHT))

        # Buttons
        self.start_rect = pg.Rect(0, 0, 260, 64)
        self.start_rect.center = (WIDTH // 2, HEIGHT // 2 + 20)
        self.quit_rect = pg.Rect(0, 0, 260, 64)
        self.quit_rect.center = (WIDTH // 2, HEIGHT // 2 + 110)

        self.started = False

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    return False  # User quit
                if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    return False  # User quit
                if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = pg.mouse.get_pos()
                    if self.start_rect.collidepoint(mx, my):
                        return True  # Start game
                    elif self.quit_rect.collidepoint(mx, my):
                        return False  # User quit

            # Draw menu
            self.draw_menu()
            pg.display.flip()

    def button(self, rect: pg.Rect, text: str):
        mx, my = pg.mouse.get_pos()
        hovered = rect.collidepoint(mx, my)

        # Red for quit, blue for others
        if rect == self.quit_rect:
            base_color = RED
            hover_color = RED_HOVER
        else:
            base_color = BTN
            hover_color = BTN_HOVER

        pg.draw.rect(self.screen, hover_color if hovered else base_color, rect, border_radius=12)
        lbl = self.big.render(text, True, WHITE)
        self.screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

    def draw_menu(self):
        # Draw the background image instead of a solid color
        self.screen.blit(self.bg_image, (0, 0))

        title = self.big.render("Protocol: Outbreak", True, WHITE)
        sub = self.font.render("Initializing sequence...", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 - 65))
        self.button(self.start_rect, "Start")
        self.button(self.quit_rect, "Quit")

        self.developers(["Jason He", "Cristian Gutierrez Espinoza", "Joshua Paulino Ozuna", "Ian Khanna"])

    def developers(self, names):
        # Display developer names at the bottom of the screen
        text = "Game created by: " + ", ".join(names)
        bar_h = 30
        bar = pg.Surface((WIDTH, bar_h), pg.SRCALPHA)
        bar.fill((0, 0, 0, 110))  # RGBA — last value is alpha (0–255)
        self.screen.blit(bar, (0, HEIGHT - bar_h))

        # centered label on the bar
        lbl = self.small.render(text, True, WHITE)
        self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2,
                               HEIGHT - bar_h//2 - lbl.get_height()//2 + 4))

if __name__ == "__main__":
    MenuApp().run()
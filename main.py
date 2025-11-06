import pygame
from src.ui.menu import MenuApp
from src.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    menu = MenuApp()
    menu.run()

if __name__ == "__main__":
    main()  
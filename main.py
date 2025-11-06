"""import pygame
from src.ui.menu import MenuApp
from src.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    menu = MenuApp()
    menu.run()

if __name__ == "__main__":
    main()"""

# Old code above, new code below runs the game on the same sized window.

import pygame
from src.ui.menu import MenuApp
from src.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    
    # Show menu
    menu = MenuApp()
    start_game = menu.run()
    
    # If player pressed start, launch the game
    if start_game:
        game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
        game.run()
    
    pygame.quit()

if __name__ == "__main__":
    main()
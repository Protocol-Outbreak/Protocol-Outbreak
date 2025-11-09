import pygame
from src.ui.menu import MenuApp
from src.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    
    while True:  # Main game loop
        # Show menu
        menu = MenuApp()
        start_game = menu.run()
        
        if not start_game:
            # User quit from menu
            break
        
        # Start the game
        game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
        result = game.run()
        
        # If result is 'menu', loop back to menu
        # If result is None or anything else, quit
        if result != 'menu':
            break
    
    pygame.quit()

if __name__ == "__main__":
    main()
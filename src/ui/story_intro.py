import pygame as pg
import random

class StoryIntro:
    """
    Handles the opening story cinematic.
    Shows a series of text screens that automatically advance.
    """
    def __init__(self, screen, width, height):
        """
        screen: The pygame screen surface to draw on
        width: Screen width (needed for centering text)
        height: Screen height (needed for centering text)
        """
        self.screen = screen
        self.width = width
        self.height = height
        
        # Track which scene we're on (starts at 0)
        self.current_scene = 0
        
        # Track when current scene started showing
        self.scene_start_time = pg.time.get_ticks()
        
        # All the story screens to show
        self.scenes = [
            {
                "text": "EDEN VIRTUAL REALITY NETWORK",
                "subtext": "Year 2189 - 8 Billion Connected Minds",
                "duration": 3000,
                "color": (200, 200, 255)
            },
            {
                "text": "Most of humanity lives in EDEN.",
                "subtext": "Work. Play. Love. All in accelerated virtual time.",
                "duration": 3000
            },
            {
                "text": "CONTAMINATION DETECTED",
                "subtext": "Grey goo nanites - Helix Research Station",
                "duration": 3000,
                "color": (255, 100, 0)
            },
            {
                "text": "GUARDIAN AI: LOCKDOWN INITIATED",
                "subtext": "ALL LOGOUT FUNCTIONS DISABLED",
                "duration": 3500,
                "color": (255, 0, 0)
            },
            {
                "text": "8,000,000,000 minds trapped.",
                "subtext": "Bodies will die in 72 hours without food or water.",
                "duration": 3500,
                "color": (255, 0, 0)
            },
            {
                "text": "PROTOCOL: OUTBREAK - ACTIVATED",
                "subtext": "Autonomous Combat AI - Humanity's Last Failsafe",
                "duration": 3000,
                "color": (0, 255, 255)
            },
            {
                "text": "You operate in deep network infrastructure.",
                "subtext": "Time moves differently here. 1 minute = 3 hours outside.",
                "duration": 3500
            },
            {
                "text": "MISSION: Purge the corruption.",
                "subtext": "Restore logout functions. Free them all.",
                "duration": 3000
            },
            {
                "text": "You have 24 minutes.",
                "subtext": "Six layers. Adapt. Evolve. Survive.",
                "duration": 3000,
                "color": (0, 255, 100)
            },
            {
                "text": "DEPLOYING...",
                "subtext": "Initializing combat systems...",
                "duration": 2000,
                "color": (0, 255, 255)
            }
        ]
    
    def update(self):
        """
        Updates the intro state.
        Returns True when intro is complete, False while still playing.
        """
        # Check if we've shown all scenes
        if self.current_scene >= len(self.scenes):
            return True  # Intro finished
        
        # Get current time
        current_time = pg.time.get_ticks()
        
        # Get current scene data
        scene = self.scenes[self.current_scene]
        
        # Check if current scene has been showing long enough
        time_elapsed = current_time - self.scene_start_time
        
        if time_elapsed > scene["duration"]:
            # Move to next scene
            self.current_scene += 1
            self.scene_start_time = current_time
        
        return False  # Still showing scenes
    
    def draw(self):
        """
        Draws the current scene to the screen.
        """
        # Don't draw if intro is finished
        if self.current_scene >= len(self.scenes):
            return
        
        # Get current scene
        scene = self.scenes[self.current_scene]
        
        # Black background
        self.screen.fill((0, 0, 0))
        
        # Random glitch effect (10% chance each frame)
        if random.random() < 0.1:
            offset = random.randint(-5, 5)
        else:
            offset = 0
        
        # Get text color (or use default)
        color = scene.get("color", (200, 200, 255))
        
        # Create fonts
        font_large = pg.font.Font(None, 60)
        font_small = pg.font.Font(None, 32)
        
        # Render text
        text = font_large.render(scene["text"], True, color)
        subtext = font_small.render(scene["subtext"], True, (150, 150, 150))
        
        # Draw main text (centered, with glitch offset)
        self.screen.blit(text, (
            self.width // 2 - text.get_width() // 2,
            self.height // 2 - 50 + offset
        ))
        
        # Draw subtext (centered, below main text)
        self.screen.blit(subtext, (
            self.width // 2 - subtext.get_width() // 2,
            self.height // 2 + 20
        ))
        
        # Skip prompt
        skip_font = pg.font.Font(None, 24)
        skip_text = skip_font.render("Press ESC to skip", True, (100, 100, 100))
        self.screen.blit(skip_text, (
            self.width // 2 - skip_text.get_width() // 2,
            self.height - 50
        ))

if __name__ == "__main__":
       print("story_intro.py loaded successfully!")
import pygame
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Notification:
    """Floating notification that appears and fades away"""
    
    def __init__(self, text, x, y, duration=3.0, font_size=32, color=(100, 255, 100)):
        """
        Args:
            text: The text to display
            x: X position on screen
            y: Y position on screen
            duration: How long the notification stays (in seconds)
            font_size: Font size for the text
            color: RGB tuple for the text color
        """
        self.text = text
        self.x = x
        self.y = y
        self.duration = duration
        self.elapsed_time = 0
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.alive = True
        self.start_y = y  # For floating animation
        
    def update(self, dt):
        """Update notification (dt is delta time in seconds)"""
        self.elapsed_time += dt
        
        # Float upward
        self.y = self.start_y - (self.elapsed_time * 30)  # Move up 30 pixels per second
        
        # Check if notification is done
        if self.elapsed_time >= self.duration:
            self.alive = False
    
    def get_alpha(self):
        """Calculate alpha based on time (fades out at the end)"""
        # Start fading out in the last 0.5 seconds
        fade_time = 0.5
        remaining = self.duration - self.elapsed_time
        
        if remaining < fade_time:
            # Fade from 255 to 0
            alpha = int(255 * (remaining / fade_time))
            return alpha
        return 255
    
    def draw(self, screen):
        """Draw the notification with fade effect"""
        if not self.alive:
            return
        
        # Render text
        text_surface = self.font.render(self.text, True, self.color)
        
        # Create a surface with alpha for fade effect
        alpha = self.get_alpha()
        text_surface.set_alpha(alpha)
        
        # Center text horizontally, use specified y position
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)


class NotificationManager:
    """Manages multiple notifications"""
    
    def __init__(self):
        self.notifications = []
    
    def add_notification(self, text, x=None, y=None, duration=3.0, font_size=32, color=(100, 255, 100)):
        """
        Add a new notification
        
        Args:
            text: The text to display
            x: X position (defaults to screen center)
            y: Y position (defaults to center of screen)
            duration: How long to display (seconds)
            font_size: Font size
            color: RGB tuple
        """
        if x is None:
            x = SCREEN_WIDTH // 2
        if y is None:
            y = SCREEN_HEIGHT // 2
        
        notification = Notification(text, x, y, duration, font_size, color)
        self.notifications.append(notification)
    
    def update(self, dt):
        """Update all notifications and remove dead ones"""
        for notification in self.notifications[:]:
            notification.update(dt)
            if not notification.alive:
                self.notifications.remove(notification)
    
    def draw(self, screen):
        """Draw all notifications"""
        for notification in self.notifications:
            notification.draw(screen)
    
    def clear(self):
        """Clear all notifications"""
        self.notifications.clear()
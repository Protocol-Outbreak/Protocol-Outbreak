import pygame
from src.utils.constants import *

class StatUpgradeUI:
    """
    Diep.io-style stat upgrade UI
    Shows in bottom-left corner with clickable upgrade buttons
    """
    
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # UI positioning
        self.x = 20
        self.y = SCREEN_HEIGHT - 350
        self.width = 280
        self.stat_height = 25
        self.bar_width = 140
        self.bar_height = 18
        self.button_size = 20
        
        # Stat order (matches diep.io)
        self.stat_order = [
            'health_regen',
            'max_health',
            'body_damage',
            'bullet_speed',
            'bullet_penetration',
            'bullet_damage',
            'reload',
            'movement_speed'
        ]
        
        # Stat display names
        self.stat_names = {
            'health_regen': 'Health Regen',
            'max_health': 'Max Health',
            'body_damage': 'Body Damage',
            'bullet_speed': 'Bullet Speed',
            'bullet_penetration': 'Bullet Pen',
            'bullet_damage': 'Bullet Damage',
            'reload': 'Reload',
            'movement_speed': 'Move Speed'
        }
        
        # Stat colors (like diep.io)
        self.stat_colors = {
            'health_regen': (255, 100, 100),   # Red
            'max_health': (180, 80, 80),       # Dark red
            'body_damage': (220, 180, 80),     # Gold
            'bullet_speed': (100, 180, 255),   # Light blue
            'bullet_penetration': (80, 140, 255), # Blue
            'bullet_damage': (255, 180, 80),   # Orange
            'reload': (180, 100, 255),         # Purple
            'movement_speed': (100, 255, 180)  # Green
        }
        
        # UI state
        self.hovered_stat = None
        self.visible = True
    
    def toggle_visibility(self):
        """Show/hide the upgrade UI"""
        self.visible = not self.visible
    
    def handle_click(self, mouse_pos, player):
        """
        Handle mouse click on upgrade buttons
        Returns True if a stat was upgraded
        """
        if not self.visible:
            return False
        
        mx, my = mouse_pos
        
        # Check each stat's upgrade button
        for i, stat_key in enumerate(self.stat_order):
            button_rect = self.get_button_rect(i)
            
            if button_rect.collidepoint(mx, my):
                # Check if can upgrade
                if player.skill_points > 0 and player.stats[stat_key] < 7:
                    player.stats[stat_key] += 1
                    player.skill_points -= 1
                    
                    # Update derived stats
                    self.update_player_stats(player)
                    
                    return True
        
        return False
    
    def update_player_stats(self, player):
        """Recalculate player stats after upgrade"""
        player.max_hp = 100 + (player.stats['max_health'] * 20)
        player.speed = 3 + (player.stats['movement_speed'] * 0.5)
        # Add other stat recalculations as needed
    
    def handle_hover(self, mouse_pos):
        """Track which stat is being hovered"""
        if not self.visible:
            self.hovered_stat = None
            return
        
        mx, my = mouse_pos
        
        for i, stat_key in enumerate(self.stat_order):
            stat_rect = self.get_stat_rect(i)
            
            if stat_rect.collidepoint(mx, my):
                self.hovered_stat = stat_key
                return
        
        self.hovered_stat = None
    
    def get_stat_rect(self, index):
        """Get the rect for a stat row"""
        y_pos = self.y + 40 + (index * self.stat_height)
        return pygame.Rect(self.x, y_pos, self.width, self.stat_height)
    
    def get_button_rect(self, index):
        """Get the rect for an upgrade button"""
        y_pos = self.y + 40 + (index * self.stat_height)
        button_x = self.x + self.width - self.button_size - 5
        return pygame.Rect(button_x, y_pos + 2, self.button_size, self.button_size)
    
    def draw(self, screen, player):
        """Draw the upgrade UI"""
        if not self.visible:
            return
        
        # Background panel
        panel_height = 40 + (len(self.stat_order) * self.stat_height) + 10
        pygame.draw.rect(screen, (20, 30, 40), 
                        (self.x - 5, self.y - 5, self.width + 10, panel_height),
                        border_radius=5)
        pygame.draw.rect(screen, UI_CYAN, 
                        (self.x - 5, self.y - 5, self.width + 10, panel_height), 
                        2, border_radius=5)
        
        # Skill points display
        points_text = self.font.render(f"SKILL POINTS: {player.skill_points}", True, WHITE)
        screen.blit(points_text, (self.x + 5, self.y + 5))
        
        # Draw each stat
        for i, stat_key in enumerate(self.stat_order):
            self.draw_stat_row(screen, player, stat_key, i)
    
    def draw_stat_row(self, screen, player, stat_key, index):
        """Draw a single stat row"""
        y_pos = self.y + 40 + (index * self.stat_height)
        current_value = player.stats[stat_key]
        max_value = 7
        
        # Highlight if hovered
        if self.hovered_stat == stat_key:
            pygame.draw.rect(screen, (40, 50, 60),
                           (self.x, y_pos, self.width - 30, self.stat_height))
        
        # Stat name
        name_text = self.small_font.render(self.stat_names[stat_key], True, WHITE)
        screen.blit(name_text, (self.x + 5, y_pos + 4))
        
        # Stat bar background
        bar_x = self.x + self.width - self.bar_width - self.button_size - 15
        pygame.draw.rect(screen, (40, 40, 40),
                        (bar_x, y_pos + 3, self.bar_width, self.bar_height))
        
        # Stat bar filled portion
        fill_width = int((current_value / max_value) * self.bar_width)
        if fill_width > 0:
            color = self.stat_colors[stat_key]
            pygame.draw.rect(screen, color,
                           (bar_x, y_pos + 3, fill_width, self.bar_height))
        
        # Stat bar outline
        pygame.draw.rect(screen, (80, 80, 80),
                        (bar_x, y_pos + 3, self.bar_width, self.bar_height), 1)
        
        # Draw upgrade button
        self.draw_upgrade_button(screen, player, stat_key, index)
    
    def draw_upgrade_button(self, screen, player, stat_key, index):
        """Draw the + button for upgrading"""
        y_pos = self.y + 40 + (index * self.stat_height)
        button_x = self.x + self.width - self.button_size - 5
        button_y = y_pos + 2
        
        current_value = player.stats[stat_key]
        can_upgrade = player.skill_points > 0 and current_value < 7
        
        # Button background
        if can_upgrade:
            button_color = (80, 200, 120)
            text_color = WHITE
            
            # Hover effect
            button_rect = pygame.Rect(button_x, button_y, self.button_size, self.button_size)
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                button_color = (100, 255, 140)
        else:
            button_color = (60, 60, 60)
            text_color = (100, 100, 100)
        
        pygame.draw.rect(screen, button_color,
                        (button_x, button_y, self.button_size, self.button_size))
        pygame.draw.rect(screen, (100, 100, 100),
                        (button_x, button_y, self.button_size, self.button_size), 1)
        
        # + symbol
        if current_value < 7:
            plus_text = self.font.render("+", True, text_color)
            plus_rect = plus_text.get_rect(center=(button_x + self.button_size//2, 
                                                   button_y + self.button_size//2))
            screen.blit(plus_text, plus_rect)
        else:
            # Max indicator
            max_text = self.small_font.render("MAX", True, (255, 215, 0))
            max_rect = max_text.get_rect(center=(button_x + self.button_size//2, 
                                                 button_y + self.button_size//2))
            screen.blit(max_text, max_rect)
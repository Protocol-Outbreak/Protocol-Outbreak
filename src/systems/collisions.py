import pygame

class CollisionSystem:
    """Handles collision detection and response"""
    
    @staticmethod
    def check_wall_collision(entity_rect, walls, velocity):
        """
        Check collision with walls and return adjusted velocity
        
        Args:
            entity_rect: pygame.Rect of the entity
            walls: list of Wall objects
            velocity: (vx, vy) tuple
        
        Returns:
            (new_vx, new_vy) adjusted velocity
        """
        vx, vy = velocity
        
        # Test horizontal movement
        test_rect = entity_rect.copy()
        test_rect.x += vx
        
        for wall in walls:
            if wall.collides_with(test_rect):
                vx = 0  # Block horizontal movement
                break
        
        # Test vertical movement
        test_rect = entity_rect.copy()
        test_rect.y += vy
        
        for wall in walls:
            if wall.collides_with(test_rect):
                vy = 0  # Block vertical movement
                break
        
        return vx, vy
    
    @staticmethod
    def push_out_of_walls(entity_rect, walls):
        """
        Push entity out if stuck in walls
        Returns adjusted position (x, y) or None if no collision
        """
        for wall in walls:
            if wall.collides_with(entity_rect):
                # Calculate overlap on each side
                overlap_left = entity_rect.right - wall.rect.left
                overlap_right = wall.rect.right - entity_rect.left
                overlap_top = entity_rect.bottom - wall.rect.top
                overlap_bottom = wall.rect.bottom - entity_rect.top
                
                # Push in direction of least overlap
                min_overlap = min(overlap_left, overlap_right, 
                                 overlap_top, overlap_bottom)
                
                if min_overlap == overlap_left:
                    return entity_rect.x - overlap_left, entity_rect.y
                elif min_overlap == overlap_right:
                    return entity_rect.x + overlap_right, entity_rect.y
                elif min_overlap == overlap_top:
                    return entity_rect.x, entity_rect.y - overlap_top
                else:
                    return entity_rect.x, entity_rect.y + overlap_bottom
        
        return None
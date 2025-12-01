import pygame

class CollisionSystem:
    """Handles collision detection and response"""

    
# ========== COLLISION DETECTION METHODS ==========
    
    def handle_player_wall_collision(self, old_x, old_y):
        """Check and resolve player collision with walls"""
        if hasattr(self.player, 'rect'):
            player_rect = self.player.rect
        else:
            player_rect = pygame.Rect(
                self.player.x - self.player.size,
                self.player.y - self.player.size,
                self.player.size * 2,
                self.player.size * 2
            )
        
        for wall in self.walls:
            if wall.collides_with(player_rect):
                self.player.x = old_x
                self.player.y = old_y
                if hasattr(self.player, 'rect'):
                    self.player.rect.center = (old_x, old_y)
                return True
        return False
    
    def handle_enemy_collisions(self, enemy_old_positions):
        """Handle all enemy collision detection"""
        for i, enemy in enumerate(self.enemies[:]):
            enemy_old_x, enemy_old_y = enemy_old_positions[i]
            
            # Create enemy rect
            if hasattr(enemy, 'rect'):
                enemy_rect = enemy.rect
            else:
                enemy_rect = pygame.Rect(
                    enemy.x - enemy.size,
                    enemy.y - enemy.size,
                    enemy.size * 2,
                    enemy.size * 2
                )
            
            # Check wall collision
            wall_collision = self._check_enemy_wall_collision(enemy, enemy_rect, enemy_old_x, enemy_old_y)
            
            # Check player collision (only if not colliding with wall)
            if not wall_collision:
                self._check_enemy_player_collision(enemy)
        
        # Check enemy-enemy collisions
        self._check_enemy_enemy_collisions()
    
    def _check_enemy_wall_collision(self, enemy, enemy_rect, old_x, old_y):
        """Check if enemy collides with walls and revert position if so"""
        for wall in self.walls:
            if wall.collides_with(enemy_rect):
                enemy.x = old_x
                enemy.y = old_y
                if hasattr(enemy, 'rect'):
                    enemy.rect.center = (old_x, old_y)
                return True
        return False
    
    def _check_enemy_player_collision(self, enemy):
        """Check and resolve enemy-player collision with contact damage"""
        dist_to_player = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
        collision_distance = enemy.size + self.player.size
        
        if dist_to_player < collision_distance and dist_to_player > 0:
            # Calculate push direction
            dx = (enemy.x - self.player.x) / dist_to_player
            dy = (enemy.y - self.player.y) / dist_to_player
            
            # Push enemy away
            overlap = collision_distance - dist_to_player
            enemy.x += dx * overlap
            enemy.y += dy * overlap
            
            if hasattr(enemy, 'rect'):
                enemy.rect.center = (enemy.x, enemy.y)

            # Dmg multi based on level
            dmg_multi = 1 + (self.current_level_number * 0.1)
            
            # Deal contact damage
            current_time = pygame.time.get_ticks()
            if not hasattr(enemy, 'last_contact_damage') or current_time - enemy.last_contact_damage > 1000:
                self.player.hp -= 5 * dmg_multi
                self.player.last_damage_time = current_time
                enemy.last_contact_damage = current_time           
                if self.player.hp <= 0:
                    return self._handle_player_death()
    
    def _check_enemy_enemy_collisions(self):
        """Prevent enemies from stacking on each other"""
        for i, enemy1 in enumerate(self.enemies):
            for enemy2 in self.enemies[i+1:]:
                dx = enemy2.x - enemy1.x
                dy = enemy2.y - enemy1.y
                dist = math.sqrt(dx**2 + dy**2)
                min_dist = enemy1.size + enemy2.size
                
                if dist < min_dist and dist > 0:
                    # Push enemies apart
                    overlap = min_dist - dist
                    push_x = (dx / dist) * overlap * 0.5
                    push_y = (dy / dist) * overlap * 0.5
                    
                    enemy1.x -= push_x
                    enemy1.y -= push_y
                    enemy2.x += push_x
                    enemy2.y += push_y
                    
                    if hasattr(enemy1, 'rect'):
                        enemy1.rect.center = (enemy1.x, enemy1.y)
                    if hasattr(enemy2, 'rect'):
                        enemy2.rect.center = (enemy2.x, enemy2.y)
    
    def handle_bullet_collisions(self):
        """Handle all bullet collision detection"""
        self._check_player_bullets_vs_enemies()
        result = self._check_enemy_bullets_vs_player()
        return result
    
    def _check_player_bullets_vs_enemies(self):
        """Check player bullets hitting enemies"""
        for bullet in self.bullets[:]:
            if bullet.owner_type == "player":
                for enemy in self.enemies[:]:
                    dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if dist < enemy.size:
                        enemy.take_damage(bullet.damage)
                        bullet.health -= 20
                        
                        if enemy.health <= 0:
                            # CREATE EXPLOSION WHEN ENEMY DIES
                            enemy_color = self.get_enemy_color(enemy)
                            self.particle_system.create_explosion(
                                enemy.x, 
                                enemy.y, 
                                enemy_color,
                                particle_count=20,
                                speed=4
                            )
                            
                            self.player.gain_xp(enemy.xp_value, self)
                            self.enemies.remove(enemy)
                        
                        if bullet.health <= 0 and bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break

    
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
                #vx = 0  # Block horizontal movement
                break
        
        # Test vertical movement
        test_rect = entity_rect.copy()
        test_rect.y += vy
        
        for wall in walls:
            if wall.collides_with(test_rect):
                #vy = 0  # Block vertical movement
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
"""
Map Generator - Converts JSON grid data to game walls
"""

import json
import os
from src.entities.wall import Wall

class MapGenerator:
    """Generates Wall objects from JSON map data"""
    
    @staticmethod
    def generate_map_from_json(level_identifier):
        """
        Load JSON and generate walls
        
        Args:
            level_identifier: Can be:
                - int: Level number (1, 2, 3) → loads 'level_1.json', 'level_2.json', etc.
                - str: Level name ('tutorial', 'maze') → loads 'tutorial.json', 'maze.json'
                - str: Full path ('assets/maps/json/level_1.json') → loads that exact file
        
        Returns:
            {
                'walls': List of Wall objects,
                'metadata': Dict with map info,
                'spawn_point': Tuple (x, y) - center of map,
                'map_size': Tuple (width, height),
                'level_name': str - name of the level
            }
        """
        # Convert level identifier to path
        json_path = MapGenerator._resolve_path(level_identifier)
        
        try:
            # Load JSON file
            with open(json_path, 'r') as f:
                map_data = json.load(f)
            
            metadata = map_data['metadata']
            grid = map_data['grid']
            
            # Extract level name from path
            level_name = os.path.splitext(os.path.basename(json_path))[0]
            
            print(f"\n🗺️  Generating map: {level_name}")
            print(f"   Source: {metadata['source_file']}")
            print(f"   Grid: {metadata['width']}x{metadata['height']} pixels")
            print(f"   World: {metadata['world_width']}x{metadata['world_height']} units")
            print(f"   Wall pixels: {metadata['wall_pixel_count']}")
            
            # Generate optimized walls from grid
            walls, barriers = MapGenerator._grid_to_walls(grid, metadata)
            
            # Add border walls
            '''
            border_walls = MapGenerator._create_border_walls(
                metadata['world_width'],
                metadata['world_height']
            )
            walls.extend(border_walls)
            '''
            
            # Calculate spawn point (center of map)
            player_spawn = tuple(metadata.get('player_spawn', [
                metadata['world_width'] // 2,
                metadata['world_height'] // 2
            ]))

            enemy_spawns = [tuple(spawn) for spawn in metadata.get('enemy_spawns', [])] # get all spawn points for enemies
            
            map_size = (metadata['world_width'], metadata['world_height'])
            
            print(f"   ✅ Generated {len(walls)} wall objects")
            print(f"   Spawn: {player_spawn}")
            
            return {
                'walls': walls,
                'barriers': barriers,
                'metadata': metadata,
                'player_spawn': player_spawn,
                'enemy_spawns': enemy_spawns,
                'map_size': map_size,
                'level_name': level_name
            }
            
        except FileNotFoundError:
            print(f"❌ JSON file not found: {json_path}")
            print("   Available levels:")
            MapGenerator._list_available_levels()
            print("   Run: python tools/convert_map.py --all")
            return None
        except Exception as e:
            print(f"❌ Error generating map: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _resolve_path(level_identifier):
        """
        Convert level identifier to full JSON path
        
        Args:
            level_identifier: int (level number), str (level name), or str (full path)
        
        Returns:
            Full path to JSON file
        """
        # If it's an integer, convert to level_N format
        if isinstance(level_identifier, int):
            filename = f"level_{level_identifier}.json"
            return os.path.join('assets', 'maps', 'json', filename)
        
        # If it's a string
        if isinstance(level_identifier, str):
            # Check if it's already a full path (contains 'assets' or file extension)
            if 'assets' in level_identifier or level_identifier.endswith('.json'):
                return level_identifier
            
            # Otherwise, treat it as a level name
            filename = f"{level_identifier}.json"
            return os.path.join('assets', 'maps', 'json', filename)
        
        raise ValueError(f"Invalid level_identifier type: {type(level_identifier)}")
    
    @staticmethod
    def _list_available_levels():
        """List all available JSON map files"""
        json_dir = os.path.join('assets', 'maps', 'json')
        
        if not os.path.exists(json_dir):
            print(f"   (No maps directory found at {json_dir})")
            return
        
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        
        if json_files:
            for filename in sorted(json_files):
                level_name = os.path.splitext(filename)[0]
                print(f"   - {level_name}")
        else:
            print(f"   (No JSON maps found in {json_dir})")
    
    @staticmethod
    def _grid_to_walls(grid, metadata):
        """
        Convert boolean grid to optimized Wall objects
        Combines adjacent wall tiles into larger rectangles for performance
        
        Args:
            grid: 2D list of booleans (True = wall, False = empty)
            metadata: Dict with 'width', 'height', 'tile_size'
        
        Returns:
            List of Wall objects
        """
        height = metadata['height']
        width = metadata['width']
        tile_size = metadata['tile_size']
        
        walls = []
        barriers = []
        visited = [[False] * width for _ in range(height)]
        
        # Scan through grid and find rectangles
        for y in range(height):
            for x in range(width):
                if grid[y][x] != 'wall' or visited[y][x]:
                    continue
                rect_w, rect_h = MapGenerator._find_largest_rectangle_of_type(
                    grid, visited, x, y, width, height, 'wall'
                )

                    # Only create wall if we found a valid rectangle
                if rect_w > 0 and rect_h > 0:
                    
                    world_x = x * tile_size
                    world_y = y * tile_size
                    world_w = rect_w * tile_size
                    world_h = rect_h * tile_size
                    
                    walls.append(Wall(world_x, world_y, world_w, world_h, "solid"))
        
        visited_barriers = [[False] * width for _ in range(height)]

        for y in range(height):
            for x in range(width):
                if grid[y][x] != 'barrier' or visited_barriers[y][x]:
                    continue
                rect_w, rect_h = MapGenerator._find_largest_rectangle_of_type(
                    grid, visited_barriers, x, y, width, height, 'barrier'
                )

                if rect_w > 0 and rect_h > 0:
                    world_x = x * tile_size
                    world_y = y * tile_size
                    world_w = rect_w * tile_size
                    world_h = rect_h * tile_size
                    
                    barriers.append(Wall(world_x, world_y, world_w, world_h, "enemy_barrier"))
    
        return walls, barriers
    
    @staticmethod
    def _find_largest_rectangle_of_type(grid, visited, start_x, start_y, grid_width, grid_height, target_type):
        """
        Find the largest rectangle of a specific tile type
        
        Args:
            target_type: 'wall', 'barrier', or 'empty'
        """
        # Find maximum width on the starting row
        max_width = 0
        for x in range(start_x, grid_width):
            if grid[start_y][x] == target_type and not visited[start_y][x]:
                max_width += 1
            else:
                break
        
        # Find maximum height while maintaining the width
        max_height = 1
        for y in range(start_y + 1, grid_height):
            valid_row = True
            for x in range(start_x, start_x + max_width):
                if grid[y][x] != target_type or visited[y][x]:
                    valid_row = False
                    break
            
            if valid_row:
                max_height += 1
            else:
                break
        
        # Mark all cells as visited
        for y in range(start_y, start_y + max_height):
            for x in range(start_x, start_x + max_width):
                visited[y][x] = True
        
        # DEBUG: Log large rectangles
        if max_width * max_height > 1:
            print(f"       Found {max_width}x{max_height} rectangle at ({start_x},{start_y})")

        return max_width, max_height
    
    @staticmethod
    def _create_border_walls(map_width, map_height, thickness=50):
        """
        Create border walls around the entire map
        
        Args:
            map_width: Total map width in pixels
            map_height: Total map height in pixels
            thickness: Border wall thickness
        
        Returns:
            List of 4 Wall objects (top, bottom, left, right)
        """
        return [
            Wall(0, 0, map_width, thickness, "border"),  # Top
            Wall(0, map_height - thickness, map_width, thickness, "border"),  # Bottom
            Wall(0, 0, thickness, map_height, "border"),  # Left
            Wall(map_width - thickness, 0, thickness, map_height, "border")  # Right
        ]
    
    @staticmethod
    def get_wall_stats(walls):
        """
        Get statistics about generated walls (useful for debugging)
        
        Returns:
            Dict with wall statistics
        """
        if not walls:
            return {'total': 0}
        
        total_area = sum(wall.rect.width * wall.rect.height for wall in walls)
        border_walls = [w for w in walls if w.wall_type == "border"]
        solid_walls = [w for w in walls if w.wall_type == "solid"]
        
        return {
            'total': len(walls),
            'border_walls': len(border_walls),
            'solid_walls': len(solid_walls),
            'total_area': total_area,
            'avg_wall_size': total_area // len(walls) if walls else 0
        }
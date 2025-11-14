"""
PNG to JSON Map Converter - Development Tool
============================================
Run this script once when you create/edit a PNG map to convert it to JSON.
Automatically skips files that are already up-to-date.

Usage:
    python tools/convert_map.py                          # Interactive mode
    python tools/convert_map.py level_1.png             # Convert specific file
    python tools/convert_map.py --all                   # Convert all PNGs
    python tools/convert_map.py --all --force           # Force reconvert all
    python tools/convert_map.py level_1.png --force     # Force reconvert one

After conversion, you never need to run this again unless you edit the PNG.
"""
# ff0000 the red used for the barriers to be opened
# 3aff00 the green used to represent the spawn point
# ff00fa the pink used to represent the enemy spawn points
# fffa00 the yellow is for a boss
# ff7400 the orange is for stationary snipers
import pygame
import json
import os
import sys
from datetime import datetime

class MapConverter:
    def __init__(self, tile_size=50):
        self.tile_size = tile_size
        pygame.init()
    
    def needs_conversion(self, png_path, json_path):
        """
        Check if PNG needs to be converted
        Returns: (needs_conversion, reason)
        """
        # JSON doesn't exist
        if not os.path.exists(json_path):
            return True, "JSON file doesn't exist"
        
        # Check if PNG is newer than JSON
        png_time = os.path.getmtime(png_path)
        json_time = os.path.getmtime(json_path)
        
        if png_time > json_time:
            png_date = datetime.fromtimestamp(png_time).strftime('%Y-%m-%d %H:%M:%S')
            json_date = datetime.fromtimestamp(json_time).strftime('%Y-%m-%d %H:%M:%S')
            return True, f"PNG modified after JSON (PNG: {png_date}, JSON: {json_date})"
        
        # JSON is up-to-date
        return False, "Already up-to-date"
    
    def convert(self, png_path, json_path=None, force=False):
        """
        Convert a single PNG to JSON
        
        Args:
            png_path: Path to PNG file
            json_path: Path to save JSON (auto-generated if None)
            force: Force conversion even if up-to-date
        
        Returns:
            (success, status) where status is 'converted', 'skipped', or 'error'
        """
        # Auto-generate json_path if not provided
        if json_path is None:
            json_path = png_path.replace('/png/', '/json/').replace('.png', '.json')
        
        # Create output directory
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        # Check if conversion is needed
        needs_conv, reason = self.needs_conversion(png_path, json_path)
        
        if not needs_conv and not force:
            print(f"\n⏭️  Skipping: {os.path.basename(png_path)}")
            print(f"   {reason}")
            return True, 'skipped'
        
        try:
            print(f"\n📄 Converting: {os.path.basename(png_path)}")
            if force:
                print(f"   (Force mode)")
            elif needs_conv:
                print(f"   ({reason})")
            
            # Load PNG
            image = pygame.image.load(png_path)
            width, height = image.get_size()
            print(f"   Size: {width}x{height} pixels → {width*self.tile_size}x{height*self.tile_size} world units")
            
            # Convert to grid
            grid = []
            wall_count = 0
            barrier_count = 0
            enemy_spawns = []
            player_spawn = None

            for y in range(height):
                row = []
                for x in range(width):
                    color = image.get_at((x, y))

                    if color.g > 200 and color.r < 100 and color.b < 50:
                        row.append('player_spawn')
                        world_x = (x * self.tile_size) + (self.tile_size // 2)
                        world_y = (y * self.tile_size) + (self.tile_size // 2)
                        player_spawn = [world_x,world_y]

                    elif color.r > 200 and color.b > 200 and color.g < 50:
                        row.append("enemy_spawn")
                        world_x = (x * self.tile_size) + (self.tile_size // 2)
                        world_y = (y * self.tile_size) + (self.tile_size // 2)
                        enemy_spawns.append([world_x,world_y])

                    elif color.r > 200 and color.g < 50 and color.b < 50:
                        row.append('barrier')
                        barrier_count += 1

                    elif color.r < 128 and color.g < 128 and color.b < 128:
                        row.append('wall')
                        wall_count += 1
                    else:
                        row.append('empty')

                grid.append(row)

            if player_spawn is None:
                print("Did not create a spawn or did not use right color")
                player_spawn = [(width * self.tile_size) // 2,(height * self.tile_size) // 2]

            
            # Create JSON data
            map_data = {
                'metadata': {
                    'source_file': os.path.basename(png_path),
                    'width': width,
                    'height': height,
                    'tile_size': self.tile_size,
                    'world_width': width * self.tile_size,
                    'world_height': height * self.tile_size,
                    'wall_pixel_count': wall_count,
                    'barrier_pixel_count': barrier_count,
                    'player_spawn': player_spawn,
                    'enemy_spawns': enemy_spawns,
                    'converted_at': datetime.now().isoformat()
                },
                'grid': grid
            }
            
            # Save JSON
            with open(json_path, 'w') as f:
                json.dump(map_data, f, indent=2)
            
            print(f"   Walls: {wall_count} pixels")
            print(f"   Barriers: {barrier_count} pixels")
            print(f"   Player spawn: {player_spawn}")  # ADD THIS
            print(f"   Enemy spawns: {len(enemy_spawns)} locations")  # ADD THIS
            print(f"   ✅ Saved: {os.path.basename(json_path)}")
            return True, 'converted'
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False, 'error'


def find_png_files(directory):
    """Find all PNG files in directory"""
    if not os.path.exists(directory):
        return []
    return sorted([f for f in os.listdir(directory) if f.endswith('.png')])


def main():
    # Check for --force flag
    force = '--force' in sys.argv or '-f' in sys.argv
    args = [arg for arg in sys.argv[1:] if arg not in ['--force', '-f']]
    
    converter = MapConverter(tile_size=50)
    
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    png_dir = os.path.join(base_dir, 'assets', 'maps', 'png')
    
    print("=" * 60)
    print("🗺️  PNG → JSON Map Converter")
    if force:
        print("   [FORCE MODE: Will reconvert all files]")
    print("=" * 60)
    
    # Check if PNG directory exists
    if not os.path.exists(png_dir):
        print(f"\n❌ PNG directory not found: {png_dir}")
        print("   Creating directory...")
        os.makedirs(png_dir, exist_ok=True)
        print(f"   ✅ Created: {png_dir}")
        print("\n   Place your PNG maps here, then run this script again.")
        return
    
    # Parse command line arguments
    if len(args) > 0:
        arg = args[0]
        
        # Convert all PNGs
        if arg == "--all" or arg == "-a":
            png_files = find_png_files(png_dir)
            if not png_files:
                print(f"\n❌ No PNG files found in {png_dir}")
                return
            
            print(f"\nFound {len(png_files)} PNG file(s)")
            
            converted = 0
            skipped = 0
            errors = 0
            
            for png_file in png_files:
                png_path = os.path.join(png_dir, png_file)
                success, status = converter.convert(png_path, force=force)
                
                if status == 'converted':
                    converted += 1
                elif status == 'skipped':
                    skipped += 1
                elif status == 'error':
                    errors += 1
            
            print(f"\n{'='*60}")
            print(f"Summary:")
            print(f"  ✅ Converted: {converted}")
            print(f"  ⏭️  Skipped: {skipped}")
            if errors > 0:
                print(f"  ❌ Errors: {errors}")
            print(f"{'='*60}")
            
            if skipped > 0 and not force:
                print("\n💡 Tip: Use --force to reconvert all files")
        
        # Convert specific file
        else:
            filename = arg if arg.endswith('.png') else arg + '.png'
            png_path = os.path.join(png_dir, filename)
            
            if not os.path.exists(png_path):
                print(f"\n❌ File not found: {png_path}")
                print(f"   Available files:")
                for f in find_png_files(png_dir):
                    print(f"     - {f}")
                return
            
            success, status = converter.convert(png_path, force=force)
            
            print(f"\n{'='*60}")
            if status == 'converted':
                print("✅ Conversion complete!")
            elif status == 'skipped':
                print("⏭️  File already up-to-date")
                print("   Use --force to reconvert anyway")
            elif status == 'error':
                print("❌ Conversion failed")
            print(f"{'='*60}")
    
    # Interactive mode
    else:
        png_files = find_png_files(png_dir)
        
        if not png_files:
            print(f"\n❌ No PNG files found in {png_dir}")
            print("\n💡 Place PNG maps in that folder, then run:")
            print("   python tools/convert_map.py --all")
            return
        
        print(f"\nFound PNG files in {png_dir}:")
        
        # Check which files need conversion
        for i, filename in enumerate(png_files, 1):
            png_path = os.path.join(png_dir, filename)
            json_path = png_path.replace('/png/', '/json/').replace('.png', '.json')
            needs_conv, _ = converter.needs_conversion(png_path, json_path)
            status = "🔄 needs update" if needs_conv else "✅ up-to-date"
            print(f"  {i}. {filename:<30} {status}")
        
        print("\nOptions:")
        print("  [number] - Convert specific file")
        print("  [a]      - Convert all files that need updating")
        print("  [f]      - Force convert all files")
        print("  [q]      - Quit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            print("Cancelled.")
            return
        
        elif choice == 'a':
            converted = 0
            skipped = 0
            errors = 0
            
            for png_file in png_files:
                png_path = os.path.join(png_dir, png_file)
                success, status = converter.convert(png_path, force=False)
                
                if status == 'converted':
                    converted += 1
                elif status == 'skipped':
                    skipped += 1
                elif status == 'error':
                    errors += 1
            
            print(f"\n{'='*60}")
            print(f"Summary:")
            print(f"  ✅ Converted: {converted}")
            print(f"  ⏭️  Skipped: {skipped}")
            if errors > 0:
                print(f"  ❌ Errors: {errors}")
            print(f"{'='*60}")
        
        elif choice == 'f':
            converted = 0
            errors = 0
            
            for png_file in png_files:
                png_path = os.path.join(png_dir, png_file)
                success, status = converter.convert(png_path, force=True)
                
                if status in ['converted', 'skipped']:
                    converted += 1
                elif status == 'error':
                    errors += 1
            
            print(f"\n{'='*60}")
            print(f"✅ Force converted {converted}/{len(png_files)} file(s)")
            if errors > 0:
                print(f"❌ Errors: {errors}")
            print(f"{'='*60}")
        
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(png_files):
                png_path = os.path.join(png_dir, png_files[idx])
                success, status = converter.convert(png_path, force=force)
                
                print(f"\n{'='*60}")
                if status == 'converted':
                    print("✅ Conversion complete!")
                elif status == 'skipped':
                    print("⏭️  File already up-to-date")
                    print("   Run with --force to reconvert")
                elif status == 'error':
                    print("❌ Conversion failed")
                print(f"{'='*60}")
            else:
                print("❌ Invalid number")
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
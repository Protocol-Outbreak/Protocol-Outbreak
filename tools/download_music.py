#!/usr/bin/env python3
"""
Download free royalty-free music for Protocol Outbreak
Uses Incompetech's free music (CC BY 4.0 license)
"""

import urllib.request
import os

def download_music():
    """Download background music from Incompetech"""
    
    # Kevin MacLeod - Cyborg Ninja (Perfect for cyberpunk tank game)
    # CC BY 4.0 License: https://creativecommons.org/licenses/by/4.0/
    
    music_url = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cyborg%20Ninja.mp3"
    output_path = "assets/sounds/background_music.mp3"
    
    print("🎵 Downloading background music...")
    print(f"   Source: Incompetech.com")
    print(f"   Track: Cyborg Ninja by Kevin MacLeod")
    print(f"   License: CC BY 4.0")
    print()
    
    try:
        # Create directory if it doesn't exist
        os.makedirs("assets/sounds", exist_ok=True)
        
        # Download the file
        print(f"   Downloading to: {output_path}")
        urllib.request.urlretrieve(music_url, output_path)
        
        print()
        print("✅ Download complete!")
        print(f"   File saved: {output_path}")
        print(f"   Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        print()
        print("📝 Attribution Required:")
        print('   Music: "Cyborg Ninja" by Kevin MacLeod')
        print("   License: CC BY 4.0")
        print("   Source: incompetech.com")
        print()
        print("🎮 Music is now ready to use!")
        print("   Uncomment the music line in src/game.py to enable it")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading music: {e}")
        print()
        print("📌 Alternative: Manual Download")
        print("   1. Visit: https://incompetech.com/music/royalty-free/")
        print('   2. Search for "Cyborg Ninja"')
        print("   3. Download MP3")
        print("   4. Save as: assets/sounds/background_music.mp3")
        return False

if __name__ == "__main__":
    print("="*60)
    print("  Protocol Outbreak - Music Downloader")
    print("="*60)
    print()
    download_music()
    print()
    print("="*60)

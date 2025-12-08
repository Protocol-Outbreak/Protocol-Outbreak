import pygame
import os
from src.utils.constants import *

class SoundManager:
    """Manages all game sounds and music"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Sound volumes (0.0 to 1.0)
        self.sfx_volume = 0.5
        self.music_volume = 0.3
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Load sound effects
        self._load_sounds()
        
        # Music state
        self.current_music = None
        self.music_enabled = True
        self.sfx_enabled = True
    
    def _load_sounds(self):
        """Load all sound effects"""
        sound_path = "assets/sounds/"
        
        # Define sound files (we'll create placeholder sounds if files don't exist)
        sound_files = {
            'shoot': 'shoot.wav',
            'enemy_hit': 'enemy_hit.wav',
            'enemy_death': 'enemy_death.wav',
            'player_hit': 'player_hit.wav',
            'level_complete': 'level_complete.wav',
            'powerup': 'powerup.wav',
            'boss_hit': 'boss_hit.wav',
        }
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(sound_path, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                    print(f"✓ Loaded sound: {sound_name}")
                except:
                    print(f"✗ Failed to load sound: {sound_name}")
                    self.sounds[sound_name] = None
            else:
                # Create a simple beep sound using pygame.mixer
                self.sounds[sound_name] = self._generate_placeholder_sound(sound_name)
    
    def _generate_placeholder_sound(self, sound_name):
        """Generate a simple placeholder sound"""
        try:
            # Create a short beep sound
            duration = 0.1  # seconds
            sample_rate = 22050
            
            # Different frequencies for different sounds
            frequencies = {
                'shoot': 440,  # A note
                'enemy_hit': 330,  # E note
                'enemy_death': 220,  # A (lower octave)
                'player_hit': 165,  # E (lower octave)
                'level_complete': 523,  # C (high)
                'powerup': 659,  # E (high)
                'boss_hit': 277,  # C# note
            }
            
            freq = frequencies.get(sound_name, 440)
            
            # Generate sine wave
            import numpy as np
            t = np.linspace(0, duration, int(sample_rate * duration))
            wave = np.sin(2 * np.pi * freq * t)
            
            # Add envelope to prevent clicks
            envelope = np.linspace(1, 0, len(wave))
            wave = wave * envelope
            
            # Convert to 16-bit
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_wave = np.column_stack((wave, wave))
            
            # Create pygame sound
            sound = pygame.mixer.Sound(buffer=stereo_wave)
            sound.set_volume(self.sfx_volume)
            return sound
        except ImportError:
            # If numpy is not available, return None
            print(f"  → Using silent placeholder for {sound_name} (install numpy for beep sounds)")
            return None
        except Exception as e:
            print(f"  → Could not generate placeholder for {sound_name}: {e}")
            return None
    
    def play_sound(self, sound_name, volume_multiplier=1.0):
        """Play a sound effect"""
        if not self.sfx_enabled:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name]:
            # Adjust volume for this specific play
            vol = self.sfx_volume * volume_multiplier
            self.sounds[sound_name].set_volume(vol)
            self.sounds[sound_name].play()
    
    def play_music(self, music_name, loops=-1):
        """Play background music (loops=-1 means infinite loop)"""
        if not self.music_enabled:
            return
        
        music_path = f"assets/sounds/{music_name}"
        
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.current_music = music_name
                print(f"♪ Playing music: {music_name}")
            except Exception as e:
                print(f"✗ Failed to play music: {e}")
        else:
            print(f"✗ Music file not found: {music_path}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sfx_volume)
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_sfx(self):
        """Toggle sound effects on/off"""
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.unpause_music()
        else:
            self.pause_music()
        return self.music_enabled
    
    def cleanup(self):
        """Clean up mixer"""
        pygame.mixer.music.stop()
        pygame.mixer.quit()

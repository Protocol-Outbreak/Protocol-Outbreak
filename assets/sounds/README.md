# Sound Effects Guide

## 🎵 Adding Sounds to Your Game

This directory is where you'll place your sound effect and music files for the game.

### Required Sound Files

The game currently uses these sound effects:

1. **shoot.wav** - Player firing weapon
2. **enemy_hit.wav** - Enemy taking damage
3. **enemy_death.wav** - Enemy destroyed
4. **player_hit.wav** - Player taking damage
5. **level_complete.wav** - Level completed successfully
6. **powerup.wav** - Powerup collected (future use)
7. **boss_hit.wav** - Boss taking damage (future use)

### Background Music

- **background_music.mp3** or **background_music.ogg** - Main gameplay music (loops infinitely)

### File Formats Supported

- **Sound Effects**: `.wav` (recommended for short sounds)
- **Music**: `.mp3`, `.ogg`, `.wav` (recommended: `.ogg` for better compression)

### Where to Find Free Sound Effects

1. **Freesound.org** - https://freesound.org/
2. **OpenGameArt.org** - https://opengameart.org/
3. **Zapsplat** - https://www.zapsplat.com/
4. **Kenney.nl** - https://kenney.nl/assets (Game assets including sounds)
5. **JFXR** - https://jfxr.frozenfractal.com/ (Generate retro game sounds)

### Placeholder Sounds

If sound files are not found, the game will:
- Try to generate simple beep sounds (requires numpy)
- Or use silent placeholders

### Volume Levels

Current volume settings (can be adjusted in sound_manager.py):
- **SFX Volume**: 0.5 (50%)
- **Music Volume**: 0.3 (30%)
- Individual sound multipliers:
  - Shoot: 0.3x
  - Enemy hit: 0.4x
  - Enemy death: 0.6x
  - Player hit: 0.7x
  - Level complete: 0.8x

### Tips for Sound Effects

- Keep sound effects short (0.1 - 2 seconds)
- Use consistent volume levels
- Avoid harsh or loud sounds
- Match the game's retro/digital theme
- Test in-game to ensure they don't get repetitive

### Adding Your Own Sounds

1. Place sound files in this directory
2. Make sure filenames match exactly (case-sensitive)
3. Restart the game to load new sounds
4. Adjust volumes in `src/systems/sound_manager.py` if needed

### Future Enhancements

Consider adding sounds for:
- Menu navigation
- Tank upgrades
- Critical hits
- Player death
- Boss attacks
- Shield activation
- Special abilities

# Void Core Boss - Implementation Guide

## Overview
The Void Core is a menacing final boss enemy for Level 4 of Protocol Outbreak. It features:
- **Rotating corruption tendrils** that lash out at the player
- **Orbiting corruption entities** that circle the boss
- **Three phases** that increase in difficulty as health decreases
- **Spawning mechanics** that create minion enemies during the fight
- **Pulsing organic visual effects** with a threatening red color scheme

## How It Works

### Automatic Spawning
The boss automatically spawns on **Level 4** (the last level). When you load level 4, instead of spawning regular enemies, the game will:
1. Spawn the Void Core boss in the center of the map
2. Show a warning notification: "⚠ WARNING: VOID CORE DETECTED ⚠"
3. Display the boss health bar at the top of the screen

### Boss Stats (Level 4 Base)
- **Health**: 2000 (scales with difficulty multiplier)
- **Size**: 80 (much larger than normal enemies)
- **Speed**: 0.6 (slower but methodical)
- **XP Value**: 500 (massive reward for defeating)
- **Aggro Range**: 600 (detects player from far away)

### Three Phase System

#### Phase 1 (100% - 66% Health)
- Shoots 5-bullet radial bursts
- Spawns 2 corruption enemies every 8 seconds
- Tendrils attack every 3 seconds

#### Phase 2 (66% - 33% Health) 🔶
- Shoots 8-bullet radial bursts (faster)
- Spawns 3 corruption enemies every 6 seconds
- Tendrils attack every 2 seconds
- Console message: "🔴 THE VOID CORE ENTERS PHASE 2!"

#### Phase 3 (33% - 0% Health) 🔴
- Shoots 12-bullet radial bursts (very fast)
- Spawns 4 corruption enemies every 4 seconds
- Tendrils attack every 1.5 seconds
- Moves faster (speed increases to 1.0)
- Console message: "🔴 THE VOID CORE ENTERS FINAL PHASE!"

### Visual Features

#### Main Body
- Irregular, organic shape (9-sided polygon with sine wave variation)
- Pulsing animation using sine waves
- Dark red center with bright red outlines
- Glowing effects for menacing appearance

#### Tendrils (8 total)
- Rotate around the boss continuously
- Extend and retract with sine wave animation
- **Lash out** during tendril attacks (extend to 150 units)
- Deal contact damage to player when extended
- Glow bright red when attacking

#### Corruption Orbiters (5 entities)
- Small red entities that orbit the boss
- Create glowing trails
- Purely visual (don't deal damage)
- Add to the chaotic, threatening feel

#### Boss Health Bar
- Displayed at the top center of the screen
- Shows boss name "THE VOID CORE"
- Current phase indicator
- Color changes based on phase:
  - Phase 1: Dark red
  - Phase 2: Orange-red
  - Phase 3: Bright red
- Shows exact health numbers

### Attack Patterns

#### Radial Bullet Bursts
- Fires bullets in a spread pattern
- Number of bullets increases with each phase
- Bullets are larger (radius 8) and more damaging than normal enemy bullets

#### Tendril Slam Attack
- All 8 tendrils extend rapidly
- Creates screen shake effect
- Deals damage on contact with player
- Triggers every 1.5-3 seconds depending on phase

#### Corruption Spawning
- Spawns normal enemies (Square Turret, Triangle Blade, or Pentagon Gunner)
- Spawns in random positions around the boss
- Spawn rate increases with each phase
- Maximum of 5 spawned enemies at once

### Boss AI Behavior

#### Movement
- Keeps optimal distance from player (250-400 units)
- If player gets too close (< 250): Boss backs away
- If player is too far (> 400): Boss approaches
- Slow, methodical movement creates tension

#### Targeting
- Always faces and aims at the player
- Shoots at player position
- Tendrils rotate independently for unpredictability

### Collision & Damage

#### Player vs Boss
- **Bullet hits**: Player bullets damage the boss
- **Tendril hits**: Tendrils deal 5-15 damage per frame based on attack state
- **Body contact**: Boss body deals 0.5 damage per frame on contact

#### Boss vs Player
- **Boss bullets**: Standard enemy bullet damage (12 base * difficulty multiplier)
- **Spawned enemies**: Use normal enemy damage values
- **Contact damage**: Constant damage while touching boss or tendrils

### Level Completion
The level is marked complete when:
1. Boss health reaches 0 or below
2. `self.level_complete = True` is set
3. Boss instance is cleared from memory
4. "NEXT LEVEL" button appears (or victory screen if it's the final level)

## Testing the Boss

### Quick Test Instructions
1. Run your game
2. Navigate to Level 4 (or set `self.current_level_number = 4` in game.py)
3. The boss should spawn automatically in the center
4. You'll see the warning notification
5. Boss health bar appears at top of screen

### What to Watch For
- ✅ Boss spawns in center of map
- ✅ Health bar shows at top with "THE VOID CORE" text
- ✅ Warning notification appears
- ✅ Tendrils rotate and animate
- ✅ Boss shoots radial bullet patterns
- ✅ Phase transitions at 66% and 33% health
- ✅ Spawned enemies appear periodically
- ✅ Level completes when boss is defeated

## Customization Options

### Difficulty Tweaking
In `boss.py`, you can adjust:
- `self.max_health`: Change boss HP
- `self.shoot_delay`: Change firing rate
- `self.tendril_attack_delay`: Change tendril frequency
- `self.spawn_delay`: Change spawn rate

### Visual Tweaking
- `self.size`: Change boss size
- Number of tendrils: Modify the `for i in range(8)` loop
- Colors: Change RGB values in draw methods
- Pulse intensity: Modify `math.sin(self.animation_frame * 0.15) * 15`

### Phase Thresholds
In `take_damage()` method:
- Change `health_percent <= 0.33` for Phase 3 threshold
- Change `health_percent <= 0.66` for Phase 2 threshold

## Files Modified
1. ✅ `src/entities/boss.py` - New boss class
2. ✅ `src/utils/enums.py` - Added VOID_CORE_BOSS enum
3. ✅ `src/game.py` - Boss spawning, updating, rendering, and collision handling

## Concept Origin
Based on "The Void Core" concept from your React visualization:
- ✅ Writhing mass of corruption
- ✅ Irregular, threatening shape
- ✅ Corruption tendrils that lash out unpredictably
- ✅ Spawns corruption entities
- ✅ Pulsing, organic animation
- ✅ Multiple vulnerable points (tendril timing)
- ✅ Screen shake effects
- ✅ Menacing red/corruption color scheme

Enjoy your final boss battle! 🔴⚡

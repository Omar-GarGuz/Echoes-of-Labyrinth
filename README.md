# 🌀 Echoes of the Labyrinth

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)

*A puzzle-platformer where memories are your key to escape*

</div>

---

## 📖 About

**Echoes of the Labyrinth** is a 2D puzzle-platformer game built with Python and Pygame. Players navigate through mysterious rooms, collecting **Memory Orbs** that temporary unlock doors and activate mechanisms.

### 🎮 Core Concept

In a world where memories hold physical power, you must: 
- Collect colored Memory Orbs (cassettes) scattered throughout each level
- Use memories to unlock doors and interact with the environment
- Race against time before temporary memories fade away
- Solve puzzles using levers, switches, and moving platforms
- Avoid ghost enemies that patrol the rooms and send you back to the start

---

## ✨ Features

- **Memory System** — Collect orbs with different durations: 
  | Memory Type | Color |
  |-------------|-------|
  | Red | 🔴 |
  | Blue | 🔵 |
  | Purple | 🟣 |
  | Green | 🟢 |
  | Yellow | 🟡 |

- **Interactive Objects** — Doors, levers, switches, and moving platforms
- **Enemy System** — Ghost enemies that patrol horizontally and trigger player death on contact
- **Death & Respawn** — Player respawns at the room's start point after dying (falling or touching an enemy)
- **Story Screen** — Intro screen displayed before the level begins
- **Environmental Signs** — Image-based signs placed throughout rooms for storytelling hints
- **Room-Based Levels** — Multiple interconnected rooms/puzzles per level
- **Smooth Platforming** — Responsive controls with moving platform support
- **Atmospheric Audio** — Background music and sound effects for each level
- **Animated Graphics** — Player animations and visual feedback

---

## 🚀 Getting Started

### Installation

1. **Clone the repository or Download the Project**
   ```bash
   git clone https://github.com/Omar-GarGuz/Echoes-of-Labyrinth.git
   cd Echoes-of-Labyrinth
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install pygame
   ```

4. **Run the game**
   ```bash
   python main.py
   ```

---

## 🎮 Controls

| Action | Keys |
|--------|------|
| Move Left | `←` |
| Move Right | `→` |
| Jump | `Space` |
| Interact | `E` |
| Pause | `Esc` |

---

## 📁 Project Structure

```
Echoes-of-Labyrinth/
├── main.py                 # Game entry point and main loop
├── player.py               # Player class with movement, collision, and death/respawn
├── level.py                # Level loading, room management, and enemy handling
├── interactive_objects.py  # Doors, levers, switches, platforms
├── memory_orb.py           # Memory orb (cassette) collectibles
├── ghost.py                # Ghost enemy with horizontal patrol AI
├── menu.py                 # Main menu and UI buttons
├── ui.py                   # In-game UI (memory/cassette display)
├── settings.py             # Game constants and configuration
└── assets/
    ├── levels/             # Level data (JSON format)
    ├── music/              # Background music tracks
    ├── sounds/             # Sound effects
    ├── player/             # Player sprite animations
    ├── tiles/              # Tileset images
    ├── objects/            # Interactive object sprites (doors, levers, signs)
    ├── enemies/            # Enemy sprite sheets
    │   └── enemy_ghost/    # Ghost enemy frames (horizontal/, down/, up/)
    └── ui/                 # UI elements (cassette icon, etc.)
```

---

## 🔧 Configuration

Game settings can be modified in `settings.py`:

```python
# Display
WIDTH = 1280          # Window width
HEIGHT = 705          # Window height
FPS = 60              # Target framerate

# Player
PLAYER_SPEED = 5           # Horizontal movement speed
PLAYER_JUMP_STRENGTH = 15  # Jump power
PLAYER_GRAVITY = 0.8       # Gravity strength

# Level
TILE_SIZE = 64        # Size of each tile in pixels
```

---

## 🗺️ Creating Custom Levels

Levels are defined in JSON format in the `assets/levels/` directory. 

### Level Structure

```json
{
  "player_start": { "x": 100, "y": 500 },
  "rooms": {
    "start": {
      "layers": {
        "background": [... ],
        "foreground": [...]
      },
      "tile_mapping": {
        "1": "stone",
        "2": "brick"
      },
      "memory_orbs": [
        { "x":  200, "y": 300, "memory_type": "blue" }
      ],
      "doors": [
        {
          "x": 500, "y": 400,
          "width": 64, "height": 128,
          "required_memory": "blue",
          "target_room": "room2",
          "target_x": 100, "target_y": 500
        }
      ],
      "enemies": [
        {
          "x": 600, "y": 530,
          "patrol_left": 400,
          "patrol_right": 900,
          "speed": 2
        }
      ],
      "signs": [
        { "x": 800, "y": 550, "width": 210, "height": 50, "image": "objects/sign.png" }
      ]
    }
  }
}
```

---

## 🎨 Adding Custom Assets

### Player Animations

Place sprite frames in `assets/player/<animation>/`:
- `idle/` — 4 frames default
- `walk/` — 6 frames default
- `jump/` — 3 frames default
- `fall/` — 2 frames default

### Enemy Sprites

Place ghost frames in `assets/enemies/enemy_ghost/horizontal/`:
- `0.png`, `1.png` — two-frame walk cycle (scaled to 50×60 px)

Additional subdirectories (`down/`, `up/`) are reserved for future movement directions.

### Sound Effects

Add `.wav` files to `assets/sounds/`:
- `jump.wav`
- `collect.wav`
- `door_open.wav`
- `memory_fade.wav`
- `switch.wav`

### Music

Add `.mp3` files to `assets/music/`:
- `menu_theme.mp3`
- `level1.mp3`, `level2.mp3`, `level3.mp3`

---

## 🛠️ Development

### Running in Debug Mode

Uncomment debug lines in `player.py` to visualize hitboxes: 

```python
# In Player.draw():
pygame.draw.rect(screen, RED, self.rect.move(offset.x, offset.y), 2)
```

### Key Classes

| Class | File | Description |
|-------|------|-------------|
| `Game` | main.py | Main game loop, state management, and story screen |
| `Player` | player.py | Movement, collision, memory collection, death/respawn |
| `Level` | level.py | Room loading, tile management, enemy spawning, and collision logic |
| `Ghost` | ghost.py | Patrol-based horizontal enemy with 2-frame animation |
| `MemoryOrb` | memory_orb.py | Collectible cassettes with per-type durations |
| `Door` | interactive_objects.py | Memory-locked doors with open animation |
| `Lever` | interactive_objects.py | Toggle switches for moving platforms |
| `Switch` | interactive_objects.py | Memory-gated switches for activating platforms |
| `MovingPlatform` | interactive_objects.py | Moving platforms with waypoints |

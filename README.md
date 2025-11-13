# Basic-Mechanics
The basic mechanics of our game; the user, shooting, other UI

A top-down tank shooter inspired by diep.io with a sci-fi corruption narrative.

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python main.py`

## Controls

- WASD/Arrows: Move
- Mouse: Aim
- Left Click: Shoot
- 1/2: Switch tank types
- ESC: Quit

## Project Structure
```
nano_drone_combat/
├── main.py
├── src/
│   ├── entities/
│   ├── levels/
│   ├── ui/
│   └── utils/
```

## Contributors

- Cristian
- Ian
- Josh
- Jason

## For Playtesters:

How to run:

1. Scroll down to the "Assets" section
2. Click on "Source code (zip)" to download
3. Extract the zip file on your computer
4. Open terminal/command prompt in that folder
5. Install pygame (if you don't already have it):
    pip install pygame
6. Run the game:
    python main.py or python -m src.main

If accessing via Visual Studio Code (easiest way):

1. Download the zip
2. Extract it to a folder
3. Open VS Code
4. File -> Open Folder -> Select the extracted folder
5. Open the terminal in VS Code
6. Near the top right of the terminal, there is a + and a down arrow. Press the down arrow, and open powershell, and download pygame (if you haven't already)
7. Type pip install pygame into the powershell window
8. Find main.py and run it, or type run main.py or python -m src.main into the terminal
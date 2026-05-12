# Arcade Games

A modular arcade game collection built in Python with Pygame, designed to host multiple beginner-friendly games inside one shared launcher.

## Overview

This project implements a lightweight arcade platform with a focus on real-time game loops, responsive controls, collision handling, and structured state management. The codebase uses a multi-game architecture where each title lives in its own module under `games/` while `main.py` handles the shared menu flow and application state.

Currently implemented:
- Pong
- Snake
- Breakout
- Sudoku
- Space Invaders

Planned:
- Flappy Bird
- Additional arcade-style games

## Tech Stack

- Language: Python
- Library: Pygame
- Testing: pytest
- Architecture: modular game modules under `games/`

## Features

### Gameplay
- Pong with adjustable CPU difficulty and local versus mode
- Snake with grid-based movement and score tracking
- Breakout with lives, brick collision, and paddle angle control
- Sudoku with selectable difficulty, notes, hints, auto-check feedback, and full-solution reveal
- Space Invaders with expanding waves, larger shots, friendlier counterfire, and difficulty presets
- Time-based movement using delta time for smooth gameplay
- Accurate collision detection and response

### System Design
- State-based architecture for menu, setup, play, pause, and game-over screens
- Separate game modules under `games/`
- Shared launcher and centralized input routing in `main.py`

### Visuals
- Brighter layered background with card-style menus
- Particle effects on collisions
- Screen shake for feedback
- Ball trail for motion clarity
- Custom color palette for a more polished presentation

## Controls

| Context | Keys | Action |
|-----|-----|--------|
| Global | `Q` | Quit the application |
| Menus | `1-5` | Choose Pong, Snake, Breakout, Sudoku, or Space Invaders |
| Setup screen | `1-4` | Select the visible preset or mode |
| Shared gameplay | `P` | Pause or resume |
| Shared navigation | `Esc` | Return to the menu or back out of the current screen |
| Pong | `W` / `S` | Move the left paddle |
| Pong | `Up` / `Down` | Move the right paddle in versus mode |
| Snake | `Arrow Keys` or `WASD` | Change direction |
| Breakout | `Arrow Keys` or `A` / `D` | Move the paddle |
| Space Invaders | `Arrow Keys` or `A` / `D` | Move the ship |
| Space Invaders | `Space` | Fire |
| Sudoku | Mouse or `Arrow Keys` | Select cells |
| Sudoku | `1-9` | Enter a value |
| Sudoku | `Backspace` / `Delete` | Clear a cell |
| Sudoku | `A` / `N` / `H` / `S` | Toggle auto-check, toggle notes, reveal hint, reveal solution |

## Project Structure

```text
arcade-games/
├── games/
│   ├── __init__.py
│   ├── breakout.py
│   ├── pong.py
│   ├── snake.py
│   ├── space_invaders.py
│   └── sudoku.py
├── tests/
│   └── test_games.py
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

## Game Details

Breakout includes:
- Brick field destruction and score tracking
- Paddle-controlled bounce angles
- Life system with round resets

Pong includes:
- Difficulty levels: Easy, Medium, and Hard
- CPU paddle with adjustable tracking behavior
- Real-time score tracking and win condition
- Pause and settings menus accessible during gameplay

Snake includes:
- Grid-based movement with food spawning
- Score tracking and collision-based game over

Sudoku includes:
- A standard 9x9 board
- Easy, Medium, and Hard puzzle generation
- Mouse or keyboard cell selection with number entry
- Auto-check, notes mode, hint support, full-solution reveal, and mistake tracking

Space Invaders includes:
- Three difficulty presets
- Hold-to-fire shooting and enemy return fire
- Multi-wave formations with wider spacing and easier bullet interception

## What I Learned / Technical Highlights

- Building game loops that balance frame-based drawing with time-based updates
- Managing app state across menus, setup screens, active gameplay, pause flow, and game-over transitions
- Implementing collision detection for paddles, bricks, bullets, food, walls, and Sudoku validation feedback
- Organizing multiple games with a modular structure so each title can evolve without cluttering the shared launcher

## Future Improvements

- Add more games to the launcher while keeping the same shared menu flow
- Move more shared UI/configuration values into common modules if the project grows
- Add automated smoke tests for launcher startup and menu navigation
- Package the project for easier distribution and one-command setup

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

If `python -m venv .venv` hangs or takes too long on an Anaconda-managed Python, try:

```bash
conda deactivate
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

You can also skip the virtual environment and install locally with `python -m pip install -r requirements.txt` if you just want to run the project quickly.

## Testing

```bash
pytest
```

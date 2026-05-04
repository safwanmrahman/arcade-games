# Arcade Games

A modular arcade game system built in Python using Pygame, designed to support multiple interactive games within a shared framework.

## Overview

This project implements a lightweight arcade platform with a focus on real-time game loops, smooth physics, and structured state management. The goal is to build a reusable system that can host multiple classic arcade-style games.

Currently implemented:
- Pong
- Snake
- Breakout
- Sudoku
- Space Invaders

Planned:
- Flappy Bird
- Additional arcade-style games

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
- State-based architecture (menu, setup, play, pause, game over)
- Separate game modules under `games/`
- Centralized input handling

### Visuals
- Brighter layered background with card-style menus
- Particle effects on collisions
- Screen shake for feedback
- Ball trail for motion clarity
- Custom color scheme for improved visuals

## Controls

| Key | Action |
|-----|--------|
| 1 / 2 / 3 / 4 / 5 | Choose Pong / Snake / Breakout / Sudoku / Space Invaders from the main menu |
| 1 / 2 / 3 / 4 | Choose an option on the setup screen |
| W / S | Move left paddle |
| Up / Down | Move right paddle |
| Arrow Keys / WASD | Control Snake or Breakout |
| Space | Fire in Space Invaders |
| Mouse / Arrow Keys | Select Sudoku cells |
| 1-9 / Backspace | Fill or clear Sudoku cells |
| A / N / H / S | Toggle Sudoku auto-check, notes, hint, or reveal the full solution |
| P | Pause / Resume |
| ESC | Go back / Exit menu |
| Q | Quit game |

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
├── .gitignore
├── LICENSE
├── README.md
└── main.py
```

## Game Details

Breakout includes:
- Brick field destruction and score tracking
- Paddle-controlled bounce angles
- Life system with round resets

Pong includes:
- Difficulty levels (Easy, Medium, Hard)
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

## Installation

```bash
pip install pygame
python main.py

# Arcade Games

A modular arcade game system built in Python using Pygame, designed to support multiple interactive games within a shared framework.

## Overview

This project implements a lightweight arcade platform with a focus on real-time game loops, smooth physics, and structured state management. The goal is to build a reusable system that can host multiple classic arcade-style games.

Currently implemented:
- Pong

Planned:
- Snake
- Breakout
- Additional arcade-style games

## Features

### Gameplay
- Player vs CPU with adjustable difficulty
- Player vs Player mode (W/S vs Arrow Keys)
- Time-based movement using delta time for smooth gameplay
- Accurate collision detection and response

### System Design
- State-based architecture (menu, play, pause, settings, game over)
- Modular design for adding new games
- Centralized input handling

### Visuals
- Particle effects on collisions
- Screen shake for feedback
- Ball trail for motion clarity
- Custom color scheme for improved visuals

## Controls

| Key | Action |
|-----|--------|
| W / S | Move left paddle |
| Up / Down | Move right paddle |
| P | Pause / Resume |
| O | Open settings |
| ESC | Go back / Exit menu |
| Q | Quit game |

## Pong Details

The Pong implementation includes:
- Difficulty levels (Easy, Medium, Hard)
- CPU paddle with adjustable tracking behavior
- Real-time score tracking and win condition
- Pause and settings menus accessible during gameplay

## Installation

```bash
pip install pygame
python main.py
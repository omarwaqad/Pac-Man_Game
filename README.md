Pac-Man with AI Ghosts (Python + Pygame)

This project is a simple Pac-Man clone built with Pygame
, featuring AI-controlled ghosts that chase Pac-Man using different strategies:

🟥 A* Ghost – uses the A* pathfinding algorithm to always find the shortest path to Pac-Man.

🟦 Minimax Ghost – uses a basic minimax search to predict Pac-Man’s moves and try to corner him.

The grid is fully wrapped (toroidal), so Pac-Man and the ghosts can move seamlessly off one edge and appear on the opposite side.

Features

Classic Pac-Man gameplay (movement with arrow keys).

Ghost AI powered by A* and Minimax algorithms.

Grid-based game world with smooth rendering using Pygame.

Modular code structure (PacMan and Ghost classes).

Requirements

Python 3.x

pygame

Install dependencies: pip install pygame

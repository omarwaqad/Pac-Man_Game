#!/usr/bin/env python3
"""
Main entry point for the Pac-Man game
"""
import pygame
import sys
from game import Game
from constants import GameState

def main():
    """Main function to run the Pac-Man game"""
    # Initialize pygame
    pygame.init()
    
    # Create and run the game
    game = Game()
    
    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.state in [GameState.GAME_OVER, GameState.WON]:
                    game.reset_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        if game.state == GameState.PLAYING:
            game.handle_input()
            game.update()
        
        game.draw()
        pygame.display.flip()
        game.clock.tick(60)

if __name__ == "__main__":
    main()
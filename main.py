import os
import argparse
# import tkinter as tk # Not needed for AI training run
# from tkinter import filedialog # Not needed for AI training run

# Import your game components
from Game import Game
from functions import clear_moves, python_sort # Make sure these are properly imported
from settings import *
# This main.py is specifically for running the AI training.
# The original main.py to generate summary.txt should be kept separate or renamed.

# Define paths (ensure these match settings.py or are consistent)
# These should ideally be read from settings.py or passed through a config
# For simplicity, if settings.py already defines them, we don't need to redefine here
# Assuming settings.py is correctly setting map_path and moves_path

if __name__ == "__main__":
    # It's good practice to clear previous moves before a new training run
    print("Clearing previous moves data...")
    clear_moves()

    # Create an instance of the game
    game = Game()
    
    # Initialize the game with level 1
    # This will load the map, create enemies, etc.
    game.new(1) # Assuming you want to train on Level 1

    # Create the initial generation of players
    game.create_initial_players()

    # Start the game loop
    print(f"Starting AI training for 'Game khó nhất thế giới' on Level {game.level}...")
    game.run()

    print("AI training finished.")
    # You might want to print the final best_moves here or load it from moves.txt
    if game.run == False:
        print(f"Level was passed after {game.generation} generations!")
    else:
        print(f"Game ended after {game.generation} generations.")
    
    # Optionally, read and print the overall best move from the last generation
    try:
        with open(moves_path, 'r') as file:
            data = file.readlines()
            if data:
                # Find the last "END OF GENERATION" marker
                last_gen_end_index = -1
                for i in range(len(data) - 1, -1, -1):
                    if "END OF GENERATION" in data[i]:
                        last_gen_end_index = i
                        break
                
                if last_gen_end_index != -1:
                    # The sorted block for the last generation is *before* this marker
                    # The best move will be the last line of the sorted block
                    # Need to infer start_line_index for the *last completed* generation
                    # which is game.generation - 1
                    
                    # Assuming the last recorded generation is game.generation - 1
                    # and it has (player_count + 1) lines per block.
                    # Best move is at start_line_index + player_count - 1
                    
                    last_completed_gen_idx = game.generation - 1
                    if last_completed_gen_idx >= 0:
                        start_line_of_last_gen_moves = last_completed_gen_idx * (game.player_count + 1)
                        best_move_line_idx = start_line_of_last_gen_moves + game.player_count - 1
                        
                        if best_move_line_idx < len(data):
                            best_move_line = data[best_move_line_idx]
                            moves_start_index = best_move_line.find("Moves: ")
                            if moves_start_index != -1:
                                final_best_moves = best_move_line[moves_start_index + len("Moves: "):].strip()
                                print(f"\nOverall best moves found: {final_best_moves}")
                            else:
                                print("\nCould not find 'Moves:' in the overall best move line.")
                        else:
                            print("\nNo recorded best moves for the last completed generation.")
                    else:
                        print("\nNo generations completed yet.")
                else:
                    print("\nNo 'END OF GENERATION' markers found in moves.txt.")
            else:
                print("\nmoves.txt is empty.")
    except FileNotFoundError:
        print(f"moves.txt not found at {moves_path}")
    except Exception as e:
        print(f"Error reading moves.txt for final best move: {e}")
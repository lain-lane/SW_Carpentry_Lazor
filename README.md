# SW_Carpentry_Lazor
##Midterm Lazor Project for SW Carpentry course spring 2025

# How to Use:
Configure a level from the game into the appropriate board file format (see handout for explanation).
Use the read_bff function from the reader module to convert a bff to the arguments game_grid, num_blocks, lasers, points.
Input these args into the game_solver function from the solver module. game_solver returns **solution**: the solved grid as a numpy array and **lasers_trajs**: a list of all points hit by lasers. 
To visualize the solution in matplotlib, use the game_plotter function from the solver module. Input the **lasers_trajs** and **solution** from the game_solver along with the points that were read earlier. You can also specify a savename if you wish to save the image. 

Alternatively you can use solve_bff to get the solution and trajectories directly from the bff file. Then you can use write_solution from the solver module to write the solved positions of the blocks to a text file. 

#SW_Carpentry_Lazor
Midterm Lazor Project for SW Carpentry Course, Spring 2025

#What This Project Does
This is a Python program that solves a puzzle game called "Lazors." In the game, you have a grid with lasers, targets (points the lasers need to hit), and blocks you can place. The goal is to position the blocks so the lasers bounce or pass through to hit all the targets. This repo reads puzzle files (.bff format), figures out where to put the blocks, tracks the laser paths, and shows you the solution—both as a file and a picture!

#How It Works
The program is split into different files, each doing a specific job to solve the puzzle. Here’s what each file does in simple terms:

block.py: This file figures out what happens when a laser hits a block. There are three types of blocks:
A: Bounces the laser back (like a mirror).
B: Stops the laser (like a wall).
C: Bounces the laser and lets it pass through (like a half-mirror).
It checks the block type and says, “Does it bounce? Does it keep going?”
grid.py: This is the grid master! It takes the game board, finds empty spots where blocks can go, randomly places blocks (like A, B, C), and turns the small grid into a bigger “mesh” grid. The mesh is like a zoomed-in version so the laser can move between blocks.
exporter.py: Once the puzzle is solved, this file saves the solution. It writes the grid with blocks to a new .bff file and makes a picture (.png) showing where the blocks are, using colors (blue for A, black for B, orange for C).
config.py: This file reads the puzzle file (.bff) and pulls out all the important stuff: the grid layout, how many blocks you have, where the lasers start, which way they go, and the targets they need to hit.
__init__.py: This is like a welcome sign for the program. It says, “Hey, here are the main tools you can use!” so other files can grab what they need easily.
lightpath.py: This tracks the laser’s journey. It starts where the laser begins, follows its path, and figures out what happens when it hits blocks—bouncing, splitting, or stopping. It keeps a list of every spot the laser touches.
new_solver.py: This is the testing file. It checks if everything works right by running 8 mini-tests (e.g., “Does the grid load? Do lasers hit targets?”). If all tests pass, you know the program is solid.
solver.py: The brain of the operation! It takes a .bff file, tries tons of random block placements (up to 500,000 tries), checks if the lasers hit all targets, and if it works, saves the solution using exporter.py.

#How to Use
Here’s how to play with this solver:

Set Up a Puzzle: Make a .bff file describing your puzzle (check the course handout for the format). It includes the grid, blocks, lasers, and targets.
Run the Solver:
Use solver.py directly: Put your .bff file in the bff_files folder, run python solver.py, and it’ll try to solve all .bff files there. If it works, you’ll get a solution file and picture in the solution folder. The code is designed in such a way that it automatically looks for the bff files in the bff_files directory, so no need to specify the name anywhere. 

Or, use pieces manually:
LazorConfig reads the .bff file into parts: grid, block counts, lasers, and targets.
Feed those into GridBuilder and LightPath to solve it step-by-step.
Use export_solution to save the result.
See the Solution: Open the .png file to see the grid with blocks, or check the new .bff file for the solved layout.
Example
Put my_puzzle.bff in bff_files, run python solver.py, and look in solution for my_puzzle_solution.bff and my_puzzle_solution.png. Done!

#Notes
The solver guesses block positions randomly, so it might take a few tries (or 500,000!) to crack tough puzzles.
The tests in new_solver.py make sure everything’s working—run python new_solver.py to check.

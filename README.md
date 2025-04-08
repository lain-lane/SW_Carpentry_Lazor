# SW_Carpentry_Lazor
Midterm Lazor Project for SW Carpentry Course, Spring 2025

## What This Project Does
This is a Python program that solves a puzzle game called "Lazors." In the game, you have a grid with lasers, targets (points the lasers need to hit), and blocks you can place. The goal is to position the blocks so the lasers bounce or pass through to hit all the targets. This repo reads puzzle files (.bff format), figures out where to put the blocks, tracks the laser paths, and shows you the solution—both as a file and a picture!

## How It Works
The program is split into different files, each doing a specific job to solve the puzzle. Here’s what each file does in simple terms:

- **block.py**: Figures out what happens when a laser hits a block. There are three types: `A` bounces the laser (like a mirror), `B` stops it (like a wall), `C` bounces and lets it pass (like a half-mirror). It decides: “Bounce? Keep going? Both?”
- **grid.py**: The grid master! It takes the game board, finds empty spots for blocks, randomly places them (like `A`, `B`, `C`), and makes a bigger “mesh” grid so lasers can move between blocks.
- **exporter.py**: Saves the solution once solved. It writes the grid to a new `.bff` file and makes a picture (`.png`) with colors: blue for `A`, black for `B`, orange for `C`.
- **config.py**: Reads the `.bff` puzzle file and grabs the grid layout, block counts, laser starts, directions, and targets.
- **__init__.py**: A welcome sign for the program, listing the main tools so other files can use them easily.
- **lightpath.py**: Tracks the laser’s journey—where it starts, how it moves, and what happens when it hits blocks (bouncing, splitting, or stopping).
- **new_solver.py**: The testing file. Runs 8 mini-tests to check if everything works (e.g., “Does the grid load? Do lasers hit targets?”). All tests passing means it’s good!
- **solver.py**: The brain! Takes a `.bff` file, tries tons of random block placements (up to 500,000 tries), checks if lasers hit all targets, and saves the solution.

## How to Use
Here’s how to play with this solver:

1. **Set Up a Puzzle**: Make a `.bff` file for your puzzle (see the course handout for the format). It needs the grid, blocks, lasers, and targets. The code is designed in such a way that you can upload the file into bff_files directory and the code will automatically look for the file, there's no need to specify the name anywhere.
2. **Run the Solver**: 
   - **Easy Way**: Put your `.bff` file in the `bff_files` folder, run `python solver.py`, and it’ll solve all `.bff` files there. If it works, check the `solution` folder for a new `.bff` file and picture.
   - **Manual Way**: Use `LazorConfig` to read the `.bff` file into parts (grid, blocks, lasers, targets). Feed those into `GridBuilder` and `LightPath` to solve it step-by-step. Save with `export_solution`.
3. **See the Solution**: Open the `.png` file to see the grid with blocks, or check the new `.bff` file for the solved layout.

### Example
Put `my_puzzle.bff` in `bff_files`, run `python solver.py`, and look in `solution` for `my_puzzle_solution.bff` and `my_puzzle_solution.png`. Done!

## Notes
- The solver guesses block positions randomly, so it might take a few tries (or 500,000!) for tough puzzles.
- Run `python new_solver.py` to test everything—8 passing tests mean it’s working great!

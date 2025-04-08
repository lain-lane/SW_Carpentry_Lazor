"""
Main solver module for the Lazor Puzzle.

This script iteratively attempts to solve all .bff puzzle files in a specified folder using randomized block placement.
If a valid solution is found (i.e., all laser paths hit all target points), it exports the resulting grid and generates a visualization.

Modules Used:
- LazorConfig: Parses and loads puzzle configuration from .bff file.
- GridBuilder: Generates and manages the grid layout with blocks.
- LightPath: Simulates laser behavior through the grid.
- export_solution: Outputs the solved configuration to a file and image.

"""

from lazor.config import LazorConfig
from lazor.grid import GridBuilder
from lazor.lightpath import LightPath
from lazor.exporter import export_solution

import os
import random


def run_solver(file_path, max_trials=500000):
    """
    Attempt to solve a Lazor puzzle using randomized block placement.

    Parameters:
        file_path (str): Path to the .bff puzzle file.
        max_trials (int): Maximum number of randomized attempts allowed before giving up.

    Returns:
        None
        - Exports solution to the 'solution' directory if successful.
        - Prints a message to console indicating success or failure.
    """

    # Load puzzle configuration from file
    config = LazorConfig(file_path)

    # Try multiple random configurations up to the allowed number of trials
    for _ in range(max_trials):
        
        # Create a fresh board from the original layout
        board = GridBuilder(config.grid_layout)

        # Attempt to assign movable blocks randomly into open slots
        candidate = board.assign_blocks_randomly(config.available_blocks)

        # If assignment fails (more blocks than spaces), skip this trial
        if candidate is None:
            continue

        # Convert the board into a mesh format used for laser simulation
        mesh = board.generate_mesh()

        # Create a LightPath object to simulate laser movement
        sim = LightPath(config.lazor_start, config.lazor_path)

        # Trace the laser paths and collect hit points and split hits
        hit_points, _, extra_hits = sim.trace(config.lazor_path, config.grid_layout, mesh)

        # Check if all target points are hit by any laser path
        if all(target in hit_points + extra_hits for target in config.targets):

            # Generate output filename for solution
            output_name = os.path.basename(file_path).replace('.bff', '_solution.bff')

            # Export solved board to file and image
            export_solution(mesh, output_name, config.metadata_lines)
            return

    # If no valid configuration found after all trials
    print(f"\n‼️ Unable to solve: {file_path} after {max_trials} trials")


if __name__ == '__main__':
    """
    Automatically run the solver on all .bff files inside the 'bff_files' directory.
    """
    
    input_dir = 'bff_files'

    # Iterate through all .bff files in the input directory
    for file in os.listdir(input_dir):
        if file.endswith('.bff'):
            print(f"\n🧩 Processing {file}...")
            run_solver(os.path.join(input_dir, file))
            print("\n")

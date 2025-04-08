import random

class GridBuilder:
    """
    A class to handle grid manipulation and block placement for the Lazor puzzle.

    This class provides utilities to:
    - Identify available positions for placing blocks.
    - Randomly assign blocks based on given counts.
    - Expand the grid into a "mesh" format that includes both block and path nodes.

    Attributes:
        grid (list of list of str): The original game grid layout.
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
    """

    def __init__(self, grid):
        """
        Initializes the GridBuilder with a copy of the input grid.

        Args:
            grid (list of list of str): The 2D list representing the puzzle board layout.
        """
        self.grid = [row[:] for row in grid]  # Deep copy to avoid mutating original grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def get_open_slots(self):
        """
        Finds all coordinates in the grid where blocks can be placed.

        Returns:
            list of tuple: Coordinates (x, y) of open slots marked as 'o' in the grid.
        """
        return [
            (x, y)
            for y in range(self.rows)
            for x in range(self.cols)
            if self.grid[y][x] == 'o'
        ]

    def assign_blocks_randomly(self, block_counts):
        """
        Randomly assigns blocks to available open slots on the grid.

        Blocks are prioritized in the order: C > A > B to maximize solution chances.

        Args:
            block_counts (dict): Dictionary with keys 'A', 'B', 'C' and integer counts.

        Returns:
            list of list of str or None: Updated grid with blocks placed, or None if not enough space.
        """
        # Get all available open positions
        open_positions = self.get_open_slots()

        # Build a list of blocks to be placed
        block_list = (
            ['C'] * block_counts['C'] +
            ['A'] * block_counts['A'] +
            ['B'] * block_counts['B']
        )

        # If more blocks than open slots, return failure
        if len(block_list) > len(open_positions):
            return None

        # Randomly assign blocks to positions
        chosen_positions = random.sample(open_positions, len(block_list))
        for (x, y), block in zip(chosen_positions, block_list):
            self.grid[y][x] = block

        return self.grid

    def generate_mesh(self):
        """
        Expands the current grid into a mesh representation.

        The mesh is (2*rows+1)x(2*cols+1) to support laser travel through midpoints.

        Returns:
            list of list of str: Mesh grid with empty spaces and placed blocks.
        """
        # Initialize mesh with default 'o' for all positions
        mesh = [['o' for _ in range(2 * self.cols + 1)] for _ in range(2 * self.rows + 1)]

        # Place the blocks in the correct mesh coordinates
        for y in range(self.rows):
            for x in range(self.cols):
                mesh[2 * y + 1][2 * x + 1] = self.grid[y][x]

        return mesh

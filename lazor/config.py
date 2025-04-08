class LazorConfig:
    """
    LazorConfig parses a .bff input file to extract all configuration data required
    to simulate the Lazors game. It identifies the grid layout, available blocks,
    laser starting positions and directions, and target points.

    Attributes:
        grid_layout (list of list of str): Grid containing layout symbols ('x', 'o', 'A', etc.).
        available_blocks (dict): Dictionary holding counts of block types {'A': int, 'B': int, 'C': int}.
        lazers (list of tuples): Each element is ((x, y), (dx, dy)) describing a laser's origin and direction.
        targets (list of tuples): Coordinates that lasers must pass through to solve the puzzle.
        lazor_start (list of tuples): Laser starting positions.
        lazor_path (list of tuples): Laser initial directions.
        metadata_lines (list of str): All lines in the BFF file excluding the grid, used for exporting solutions.
    """

    def __init__(self, file_path):
        """
        Initializes the LazorConfig by parsing the given .bff file.

        Args:
            file_path (str): Path to the .bff configuration file.
        """
        self.grid_layout = []
        self.available_blocks = {'A': 0, 'B': 0, 'C': 0}
        self.lazers = []
        self.targets = []
        self.lazor_start = []
        self.lazor_path = []
        self.metadata_lines = []

        # Parse and load file data
        self._load_bff(file_path)

    def _load_bff(self, file_path):
        """
        Private method to load and parse the .bff file into usable data structures.

        Args:
            file_path (str): Path to the .bff file.

        Raises:
            ValueError: If 'GRID START' or 'GRID STOP' is missing in the file.
        """
        with open(file_path, 'r') as file:
            # Read all non-empty, non-comment lines
            lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]

        # Check for required markers
        if 'GRID START' not in lines or 'GRID STOP' not in lines:
            raise ValueError("Missing GRID START/STOP in BFF file")

        # Identify where the grid starts and ends
        grid_start = lines.index('GRID START') + 1
        grid_end = lines.index('GRID STOP')

        # Extract the grid layout between GRID START and GRID STOP
        self.grid_layout = [[char for char in row if char != ' '] for row in lines[grid_start:grid_end]]

        # Collect remaining lines as metadata (block counts, lasers, targets)
        self.metadata_lines = lines[:grid_start - 1] + lines[grid_end + 1:]

        for line in self.metadata_lines:
            key = line[0]

            # Parse available block counts
            if key in 'ABC':
                self.available_blocks[key] = int(line.split()[1])

            # Parse laser data (starting point and direction)
            elif key == 'L':
                nums = list(map(int, line[1:].split()))
                start, direction = (nums[0], nums[1]), (nums[2], nums[3])
                self.lazers.append((start, direction))
                self.lazor_start.append(start)
                self.lazor_path.append(direction)

            # Parse target points
            elif key == 'P':
                self.targets.append(tuple(map(int, line[1:].split())))

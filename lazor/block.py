class BlockBehavior:
    """
    Represents the behavior of a block located on the mesh grid.

    This class determines how a laser beam interacts with a block
    based on its type ('A', 'B', 'C'), by checking if it reflects and/or transmits light.

    Attributes:
        x (int): The x-coordinate of the block in the mesh.
        y (int): The y-coordinate of the block in the mesh.

    Methods:
        get_properties(mesh):
            Returns reflection and transmission behavior based on block type.
    """

    def __init__(self, x, y):
        """
        Initializes the BlockBehavior instance with block coordinates.

        Args:
            x (int): The x-coordinate of the block on the mesh.
            y (int): The y-coordinate of the block on the mesh.
        """
        self.x = x
        self.y = y

    def get_properties(self, mesh):
        """
        Determines how the block at (x, y) interacts with a laser beam.

        Based on the block type at the current mesh position:
        - 'A': Reflective only (no transmission).
        - 'B': Opaque (neither reflect nor transmit).
        - 'C': Refractive (both reflect and transmit).
        - Any other value (like 'o' or 'x'): Treated as transparent space.

        Args:
            mesh (list of list): The full laser interaction mesh grid.

        Returns:
            tuple: A pair (reflect, transmit) as booleans.
        """
        # Identify the block type at the specified mesh coordinates
        block = mesh[self.y][self.x]

        # Default: transparent space (not a block)
        reflect, transmit = False, True

        # Assign behavior based on block type
        if block == 'A':
            reflect, transmit = True, False
        elif block == 'B':
            reflect, transmit = False, False
        elif block == 'C':
            reflect, transmit = True, True

        return reflect, transmit

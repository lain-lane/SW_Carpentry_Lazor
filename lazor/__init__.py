"""
Lazor Puzzle Solver Package Initialization

This module makes key classes and functions from individual modules within the
`lazor` package available for external import. It defines the public API
via the `__all__` variable, which specifies the symbols to be exposed when
`from lazor import *` is used.

Available Components:
- LazorConfig: Parses and holds configuration data from .bff puzzle files.
- GridBuilder: Manages the game grid and block placement logic.
- BlockBehavior: Determines how blocks interact with laser beams.
- LightPath: Handles simulation of laser paths through the grid.
- export_solution: Outputs the solved board configuration and visualizations.

"""

# Import all key components of the lazor solver package
from lazor.config import LazorConfig
from lazor.grid import GridBuilder
from lazor.block import BlockBehavior
from lazor.lightpath import LightPath
from lazor.exporter import export_solution

# Define public API for package-level imports
__all__ = [
    "LazorConfig",
    "GridBuilder",
    "BlockBehavior",
    "LightPath",
    "export_solution"
]

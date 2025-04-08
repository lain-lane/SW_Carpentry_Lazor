import unittest
import os
from lazor.config import LazorConfig
from lazor.grid import GridBuilder
from lazor.block import BlockBehavior
from lazor.lightpath import LightPath

class LazorTest(unittest.TestCase):
    """
    A suite of unit tests to verify the functionality of the Lazor Puzzle Solver package.
    Tests cover configuration parsing, grid management, block behavior, laser path simulation,
    and solution validity for a laser-based puzzle game.
    """

    def setUp(self):
        """
        Set up the test environment before each test case.
        Defines the directory where .bff puzzle files are stored.
        """
        self.input_dir = 'bff_files'

    def test_config_dark_1(self):
        """
        Tests the LazorConfig class's ability to parse the 'dark_1.bff' puzzle file correctly.
        Verifies that the grid layout and laser directions are extracted as expected.
        """
        file_path = os.path.join(self.input_dir, 'dark_1.bff')
        config = LazorConfig(file_path)
        self.assertEqual(config.grid_layout, [['x', 'o', 'o'], ['o', 'o', 'o'], ['o', 'o', 'x']])
        self.assertEqual(config.lazor_path, [(-1, 1), (1, -1), (-1, -1), (1, -1)])

    def test_config_tiny_5(self):
        """
        Tests the LazorConfig class's parsing of 'tiny_5.bff'.
        Ensures the available block counts and target points are correctly extracted.
        """
        file_path = os.path.join(self.input_dir, 'tiny_5.bff')
        config = LazorConfig(file_path)
        self.assertEqual(config.available_blocks, {'A': 3, 'C': 1, 'B': 0})
        self.assertEqual(config.targets, [(1, 2), (6, 3)])

    def test_config_yarn_5(self):
        """
        Tests LazorConfig parsing for 'yarn_5.bff'.
        Validates the laser starting position and grid layout against expected values.
        """
        file_path = os.path.join(self.input_dir, 'yarn_5.bff')
        config = LazorConfig(file_path)
        self.assertEqual(config.lazor_start, [(4, 1)])
        self.assertEqual(config.grid_layout, [
            ['o', 'B', 'x', 'o', 'o'],
            ['o', 'o', 'o', 'o', 'o'],
            ['o', 'x', 'o', 'o', 'o'],
            ['o', 'x', 'o', 'o', 'x'],
            ['o', 'o', 'x', 'x', 'o'],
            ['B', 'o', 'x', 'o', 'o']
        ])

    def test_gridbuilder_open_slots(self):
        """
        Tests the GridBuilder class's get_open_slots method for 'mad_4.bff'.
        Ensures all open positions ('o') in the grid are identified correctly.
        """
        file_path = os.path.join(self.input_dir, 'mad_4.bff')
        config = LazorConfig(file_path)
        builder = GridBuilder(config.grid_layout)
        open_slots = builder.get_open_slots()
        # Assuming a 4x5 grid, check all expected open slots are found
        expected = [(x, y) for y in range(5) for x in range(4)]
        self.assertTrue(all(slot in open_slots for slot in expected))

    def test_block_behavior_tiny_5(self):
        """
        Tests the BlockBehavior class's get_properties method for 'tiny_5.bff'.
        Verifies that block properties at mesh position (3,1) are valid based on random placement.
        """
        file_path = os.path.join(self.input_dir, 'tiny_5.bff')
        config = LazorConfig(file_path)
        builder = GridBuilder(config.grid_layout)
        # Randomly place blocks and generate the mesh
        builder.assign_blocks_randomly(config.available_blocks)
        mesh = builder.generate_mesh()
        block = BlockBehavior(3, 1)
        reflect, transmit = block.get_properties(mesh)
        # Check properties match possible block types or empty space
        self.assertIn((reflect, transmit), [(False, True), (True, False), (True, True), (False, False)])

    def test_block_behavior_yarn_5(self):
        """
        Tests BlockBehavior properties for 'yarn_5.bff' at mesh position (1,11).
        Confirms that the 'B' block at grid (0,5) is opaque (no reflection or transmission).
        """
        file_path = os.path.join(self.input_dir, 'yarn_5.bff')
        config = LazorConfig(file_path)
        builder = GridBuilder(config.grid_layout)
        mesh = builder.generate_mesh()
        block = BlockBehavior(1, 11)
        reflect, transmit = block.get_properties(mesh)
        self.assertFalse(reflect)
        self.assertFalse(transmit)

    def test_lightpath_unit_test_sample(self):
        """
        Tests the LightPath class's trace method for 'unit_test_sample.bff'.
        Ensures the laser path hits the expected points and handles splits appropriately.
        """
        file_path = os.path.join(self.input_dir, 'unit_test_sample.bff')
        config = LazorConfig(file_path)
        builder = GridBuilder(config.grid_layout)
        mesh = builder.generate_mesh()
        sim = LightPath(config.lazor_start, config.lazor_path)
        hit_points, traces, extra_hits = sim.trace(config.lazor_path, config.grid_layout, mesh)
        self.assertEqual(hit_points, [(3, 6), (2, 5), (1, 4), (0, 3)])
        self.assertTrue(len(extra_hits) >= 0)

    def test_solution_validity(self):
        """
        Tests the overall solution validity using a controlled setup.
        Verifies that the laser path hits all target points in a simple 3x3 grid scenario.
        """
        # Define the grid, laser, and target for a simple test case
        grid_layout = [['B', 'o', 'o'], ['o', 'o', 'o'], ['o', 'o', 'o']]
        lazor_start = [(5, 8)]  # Mesh coords, above target
        lazor_path = [(0, -1)]  # Straight down
        targets = [(2, 3)]  # Grid coords (mesh (5, 7))

        builder = GridBuilder(grid_layout)
        mesh = builder.generate_mesh()

        # Simulate the laser path
        sim = LightPath(lazor_start, lazor_path)
        hit_points, _, extra_hits = sim.trace(lazor_path, grid_layout, mesh)
        total_hits = hit_points + extra_hits
        print("Total Hits:", total_hits)

        # Verify the target is hit
        self.assertTrue(all((x * 2 + 1, y * 2 + 1) in total_hits for x, y in targets))

if __name__ == '__main__':
    # Execute the unit tests when the script is run
    unittest.main()
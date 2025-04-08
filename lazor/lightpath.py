from lazor.block import BlockBehavior

class LightPath:
    """
    Simulates the path of lasers as they traverse the game board mesh.

    Attributes:
        starts (list of tuple): Starting coordinates of all lasers.
        directions (list of tuple): Initial direction vectors for each laser.
    """

    def __init__(self, starts, paths):
        """
        Initializes a LightPath object with laser start positions and directions.

        Args:
            starts (list of tuple): Starting points for each laser.
            paths (list of tuple): Initial direction vectors for each laser.
        """
        self.starts = starts
        self.directions = paths

    def _advance_laser(self, path, hits, grid, mesh, split_dirs, split_hits):
        """
        Advances a single laser beam one step based on block interactions.

        Depending on block properties (reflection, transmission), the beam may:
        - Reflect
        - Transmit (continue)
        - Split into two beams

        Args:
            path (list): The path of the laser (direction vectors).
            hits (list): The points the laser has visited.
            grid (list): Original grid layout (not directly used here).
            mesh (list): The expanded mesh of the board.
            split_dirs (list): Direction vectors of newly split beams (refracted).
            split_hits (list): Starting hit points for split beams.

        Returns:
            tuple: Updated path, hits, split_dirs, and split_hits.
        """
        (dx, dy), (x, y) = path[-1], hits[-1]
        options, transmit = [], []

        # Check for adjacent block interaction in all 4 cardinal directions
        for vx, vy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            nx, ny = x + vx, y + vy
            if 0 < nx < len(mesh[0]) and 0 < ny < len(mesh):
                dxn, dyn = nx - x, ny - y
                reflect, transmit_thru = BlockBehavior(nx, ny).get_properties(mesh)

                # Case 1: Reflect block (A)
                if mesh[ny][nx] == 'A':
                    options.append((-dx if dxn else dx, -dy if dyn else dy))

                # Case 2: Opaque block (B)
                elif not reflect and not transmit_thru:
                    options.append((0, 0) if dxn == dx or dyn == dy else (dx, dy))

                # Case 3: Refract block (C)
                elif reflect and transmit_thru:
                    if dxn == dx or dyn == dy:
                        options.append((-dx if dxn else dx, -dy if dyn else dy))
                        transmit.append((dx, dy))
                    else:
                        options.append((dx, dy))

        # Update laser direction and hit position
        path.append(options[-1] if options else (dx, dy))
        if transmit:
            split_dirs.append(transmit[-1])
            split_hits.append((x, y))
        hits.append((x + path[-1][0], y + path[-1][1]))

        return path, hits, split_dirs, split_hits

    def trace(self, directions, grid, mesh):
        """
        Traces the paths of all lasers, including refracted beams from C blocks.

        Args:
            directions (list of tuple): Initial laser direction vectors.
            grid (list of list): Original grid layout.
            mesh (list of list): Expanded grid for laser movement.

        Returns:
            tuple:
                flat_hits (list): All hit points of all lasers.
                traces (list): Direction vectors for each laser.
                split_hits (list): Points from which new beams were split.
        """
        traces = [[p] for p in directions]
        hits = [[s] for s in self.starts]
        split_dirs, split_hits = [], []

        # Process each laser beam from origin
        for i in range(len(traces)):
            if len(hits[i]) == 1:
                traces[i], hits[i], split_dirs, split_hits = self._advance_laser(
                    traces[i], hits[i], grid, mesh, split_dirs, split_hits
                )

            # Continue advancing until laser hits boundary or gets absorbed
            while 0 < hits[i][-1][0] < len(mesh[0])-1 and 0 < hits[i][-1][1] < len(mesh)-1:
                if traces[i][-1] != (0, 0):
                    traces[i], hits[i], split_dirs, split_hits = self._advance_laser(
                        traces[i], hits[i], grid, mesh, split_dirs, split_hits
                    )
                else:
                    break

        # Process any split beam caused by refractive blocks
        if split_dirs:
            dx, dy = split_dirs[-1]
            x, y = split_hits[-1]
            x_next, y_next = x + dx, y + dy
            split_hits.append((x_next, y_next))

            sub_dirs, sub_hits = [], []
            while 0 < x_next < len(mesh[0])-1 and 0 < y_next < len(mesh)-1:
                if split_dirs[-1] != (0, 0):
                    split_dirs, split_hits, sub_dirs, sub_hits = self._advance_laser(
                        split_dirs, split_hits, grid, mesh, sub_dirs, sub_hits
                    )
                else:
                    break
                x_next, y_next = split_hits[-1]

        # Flatten hit positions from all beams
        flat_hits = [pt for trail in hits for pt in trail]
        return flat_hits, traces, split_hits

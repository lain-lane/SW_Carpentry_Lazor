import os
import matplotlib.pyplot as plt

def export_solution(mesh, name, metadata):
    """
    Exports the final Lazor puzzle solution by writing it to a `.bff` file
    and generating a corresponding visual grid image.

    Args:
        mesh (list of list of str): The 2D mesh representation of the puzzle grid,
                                    including blocks and positions.
        name (str): Output filename (e.g., 'puzzle_solution.bff').
        metadata (list of str): List of configuration lines (e.g., block definitions, lasers)
                                to include before and after the grid section.

    Output:
        - A `.bff` file saved in the `solution/` directory representing the solved board.
        - A `.png` plot image showing the block layout visually.

    Example Output:
        solution/puzzle_solution.bff
        solution/puzzle_solution.png
    """

    # Ensure the solution directory exists
    os.makedirs('solution', exist_ok=True)

    # Flatten the mesh into a list of only block cells (ignore even-indexed rows/cols)
    result = [mesh[j][i] for j in range(1, len(mesh), 2)
                           for i in range(1, len(mesh[0]), 2)]

    # Determine the number of columns in the original grid
    width = (len(mesh[0]) - 1) // 2

    # Convert the flattened result back into 2D rows
    formatted = [result[i:i + width] for i in range(0, len(result), width)]

    # Write the solution grid to a .bff file
    with open(os.path.join('solution', name), 'w') as f:
        for line in metadata:
            f.write(line + '\n')
        f.write("GRID START\n")
        for row in formatted:
            f.write(' '.join(row) + '\n')
        f.write("GRID STOP\n")

    print(f"\n✅ Solution exported: solution/{name}\n")

    # Plot the grid with matplotlib
    plt.figure(figsize=(width, len(formatted)))
    ax = plt.gca()

    # Iterate over each cell and draw the appropriate rectangle
    for y, row in enumerate(formatted):
        for x, cell in enumerate(row):
            if cell in 'ABC':
                color = {'A': 'blue', 'B': 'black', 'C': 'orange'}[cell]
                ax.add_patch(plt.Rectangle((x, y), 1, 1, color=color, edgecolor='gray'))
            else:
                ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor='white', edgecolor='gray'))

    # Set plot bounds and remove tick labels
    ax.set_xlim(0, width)
    ax.set_ylim(0, len(formatted))
    ax.set_xticks(range(width + 1))
    ax.set_yticks(range(len(formatted) + 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal')
    ax.grid(True, which='both', color='gray', linestyle='-', linewidth=0.5)

    # Invert the y-axis to match traditional grid orientation
    plt.gca().invert_yaxis()

    # Save the plot to file
    plot_path = os.path.join('solution', name.replace('.bff', '.png'))
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()

# SW_Carpentry_Lazor
Midterm Lazor Project for SW Carpentry course spring 2025

# How to Use:
Configure a level from the game into the appropriate board file format (see handout for explanation).
Use the read_bff function from the reader module to convert a bff to the arguments game_grid, num_blocks, lasers, points.
Input these args into the game_solver function from the solver module. game_solver returns **solution**: the solved grid as a numpy array and **lasers_trajs**: a list of all points hit by lasers. 
To visualize the solution in matplotlib, use the game_plotter function from the solver module. Input the **lasers_trajs** and **solution** from the game_solver along with the points that were read earlier. You can also specify a savename if you wish to save the image. 

Alternatively you can use solve_bff to get the solution and trajectories directly from the bff file. Then you can use write_solution from the solver module to write the solved positions of the blocks to a text file. 


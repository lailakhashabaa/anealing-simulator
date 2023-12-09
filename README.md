# Simulated Annealing Placement Algorithm

## Overview

This Python script implements a simulated annealing placement algorithm for cell-based VLSI design. The algorithm aims to optimize the Wirelength (Total Wirelength - TWL) of the design by iteratively swapping cell positions on a grid. Simulated annealing is used as a probabilistic optimization technique to escape local minima and explore the solution space efficiently.

## How to Use

### Prerequisites
- Python 3.x
- Tkinter
- Matplotlib

### Instructions

1. Clone the repository or download the script.
2. Ensure the required dependencies are installed (`tkinter` and `matplotlib`).
3. Run the script using the command `python script_name.py` in your terminal.

## Code Structure

The code is divided into several functions, each serving a specific purpose:

- **`final_temp(initial_hpwl, netlist_size)`**: Calculates the final temperature for simulated annealing.

- **`initial_temp(initial_hpwl)`**: Calculates the initial temperature for simulated annealing.

- **`cells_in_which_netlist(netlist, n)`**: Defines netlists in which each cell is present.

- **`HPWL(netlist, cells_position, num_rows, num_cols)`**: Computes the Half-Perimeter Wirelength (HPWL) and a table of individual netlist HPWLs.

- **`new_HPWL_cell1(HPWL_table, initial_HPWL, netlist, cell_position, places, cell1)`**: Calculates new HPWL when swapping with an empty cell.

- **`new_HPWL_cell12(HPWL_table, initial_HPWL, netlist, new_cell_position, places, cell1, cell2)`**: Calculates new HPWL when swapping two cells.

- **`cell1_changes(HPWL_table, new_HPWL, places, cell1)`**: Updates HPWL table when a single cell is moved.

- **`cell12_changes(HPWL_table, new_HPWL, places, cell1, cell2)`**: Updates HPWL table when two cells are moved.

- **`random_placement(path)`**: Randomly places cells on the grid based on the input netlist.

- **`annealing(initial_temperature, temp_final, grid, num_cells, cells_position, netlist, num_rows, num_cols, cooling_rate, places)`**: Simulated annealing optimization process.

- **`bin_grid(grid, num_rows, num_cols)`**: Converts the grid to binary representation (occupied or empty).

- **`main()`**: The main function that orchestrates the entire simulated annealing process and includes GUI code for visualization.

## GUI and Visualization

The script includes a simple graphical user interface (GUI) using Tkinter for visualizing the initial and final placements of cells on the grid. Additionally, the script generates a graph of wirelength versus cooling rate to analyze the effect of different cooling rates on the optimization process.

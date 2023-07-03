# anealing simulator
import random
import numpy as np
import math
from tkinter import *
from tkinter import ttk
import time
import matplotlib.pyplot as plt
import csv



def final_temp(initial_hpwl, netlist_size):
    return 5e-6 * (initial_hpwl/netlist_size)


def initial_temp(initial_hpwl):
    return 500 * initial_hpwl


def cells_in_which_netlist(netlist, n):
    # defininng all the netlists where each cell is present
    where = 0
    places = [[] for j in range(n)]
    for net in netlist:
        for cell in net:
            places[cell].append(where)
        where = where + 1
    return places


def HPWL(netlist, cells_position, num_rows, num_cols):
    total_HPWL = 0
    # HPWL_table is a dictionary that contains the HPWL of each netlist
    HPWL_table = {}
    index = 0
    for net in netlist:
        length = []
        width = []
        for cell in net:
            #cell_index = int(cell)
            length.append(cells_position[cell][0])
            width.append(cells_position[cell][1])
        current = (max(length)-min(length)) + (max(width) - min(width))
        HPWL_table[index] = current
        total_HPWL += current
        index += 1
    return HPWL_table, total_HPWL

# if swapping with an empty cell, calculate the HPWL of the netlist of the cell that is being moved with new position


def new_HPWL_cell1(HPWL_table, initial_HPWL, netlist, cell_position, places, cell1):
    index = 0
    # new_HPWL is a dictionary that contains the HPWL of each netlist after the cell is moved
    new_HPWL = {}

    for net in places[int(cell1)]:
        length = []
        width = []
        for cell in netlist[net]:
            length.append(cell_position[cell][0])
            width.append(cell_position[cell][1])

        HPWL = (max(length)-min(length))+(max(width)-min(width))
        # convert the HPWL of the netlist to int to be able to subtract it from the initial HPWL
        initial_HPWL = initial_HPWL - HPWL_table[net] + HPWL
        new_HPWL[index] = HPWL
        index += 1

    return new_HPWL, initial_HPWL
# if swapping with a cell, calculate the HPWL of the netlist of the cell that is being moved
# with new position and the cell that is being swapped with


def new_HPWL_cell12(HPWL_table, initial_HPWL, netlist, new_cell_position, places, cell1, cell2):
    index = 0
    # new_HPWL is a dictionary that contains the HPWL of each netlist after the cell is moved
    new_HPWL = {}
    for net in places[int(cell1)]:
        length = []
        width = []
        for cell in netlist[net]:
            length.append(new_cell_position[cell][0])
            width.append(new_cell_position[cell][1])
        HPWL = (max(length)-min(length))+(max(width)-min(width))
        initial_HPWL = initial_HPWL - HPWL_table[net] + HPWL
        new_HPWL[index] = HPWL
        index += 1

    for net in places[int(cell2)]:
        # to not recalculate the half parameter that was calculated before
        if net not in places[int(cell1)]:
            length = []
            width = []
            for cell in netlist[net]:
                length.append(new_cell_position[cell][0])
                width.append(new_cell_position[cell][1])
            HPWL = (max(length)-min(length))+(max(width)-min(width))
            initial_HPWL = initial_HPWL - HPWL_table[net] + HPWL
            new_HPWL[index] = HPWL
            index += 1
    return new_HPWL, initial_HPWL

# update the HPWL_table if the cell is moved


def cell1_changes(HPWL_table, new_HPWL, places, cell1):
    index = 0
    for net in places[int(cell1)]:
        HPWL_table[net] = new_HPWL[index]
        index += 1

# update the HPWL_table if the two cells are moved


def cell12_changes(HPWL_table, new_HPWL, places, cell1, cell2):
    index = 0
    for net in places[int(cell1)]:
        HPWL_table[net] = new_HPWL[index]
        index += 1

    for net in places[int(cell2)]:
        if net not in places[int(cell1)]:
            HPWL_table[net] = new_HPWL[index]
            index += 1


def random_placement(path):
    with open(path, 'r') as file:
        lines = file.readlines()
        num_cells = int(lines[0].split()[0])
        num_connections = int(lines[0].split()[1])
        num_rows = int(lines[0].split()[2])
        num_cols = int(lines[0].split()[3])

        # create a list of lists to represent the grid
        grid = {}
        for r in range(0, num_rows, 1):
            for c in range(0, num_cols, 1):
                grid[r, c] = '---'
        cells_position = {}
        # place the cells randomly in the grid and save their positions
        for i in range(num_cells):
            row_rand = random.randint(0, num_rows-1)
            col_rand = random.randint(0, num_cols-1)
            while grid[row_rand, col_rand] != '---':
                row_rand = random.randint(0, num_rows-1)
                col_rand = random.randint(0, num_cols-1)
            grid[row_rand, col_rand] = str(i).zfill(3)
            cells_position[i] = (row_rand, col_rand)

        netlist = [list(map(int, line.strip().split()[1:]))
                   for line in lines[1:]]
        cells_netlists = cells_in_which_netlist(netlist, num_cells)

    return grid, cells_position, netlist, num_cells, num_connections, num_rows, num_cols, cells_netlists


def annealing(initial_temperature, temp_final, grid, num_cells, cells_position, netlist, num_rows, num_cols, cooling_rate, places):
    current_temperature = initial_temperature
    final_temperature = temp_final
    moves_per_temp = 10 * num_cells
    initial_vec, wirelength = HPWL(netlist, cells_position, num_rows, num_cols)
    plotting_one = {}
    plotting_two = {}
    
    while current_temperature > final_temperature:
        for i in range(0, moves_per_temp):
            # pick 2 random rows and columns
            row1 = random.randint(0, num_rows-1)
            col1 = random.randint(0, num_cols-1)
            row2 = random.randint(0, num_rows-1)
            col2 = random.randint(0, num_cols-1)
            # check if the rows and columns are the same and if they are empty
            while (row1 == row2 and col1 == col2) or (grid[row1, col1] == '---' and grid[row2, col2] == '---'):
                row2 = random.randint(0, num_rows-1)
                col2 = random.randint(0, num_cols-1)
            # swap the cells
            cell1 = grid[row1, col1]
            cell2 = grid[row2, col2]
            grid[row1, col1] = cell2
            grid[row2, col2] = cell1
            # update the cells_position
            if cell1 != '---' and cell2 != '---':  # if both cells are not empty
                cells_position[int(cell1)] = (row2, col2)
                cells_position[int(cell2)] = (row1, col1)
                new_list, new_hpwl = new_HPWL_cell12(
                    initial_vec, wirelength, netlist, cells_position, places, cell1, cell2)
                delta = new_hpwl - wirelength
                if delta < 0:
                    wirelength = new_hpwl
                    cell12_changes(initial_vec, new_list, places, cell1, cell2)
                else:
                    probability = np.exp(-delta/current_temperature)
                    random_number = random.random()
                    if random_number < probability:
                        wirelength = new_hpwl
                        cell12_changes(initial_vec, new_list,
                                       places, cell1, cell2)
                    else:
                        grid[row1, col1] = cell1
                        grid[row2, col2] = cell2
                        cells_position[int(cell1)] = (row1, col1)
                        cells_position[int(cell2)] = (row2, col2)

            elif cell1 != '---' and cell2 == '---':
                cells_position[int(cell1)] = (row2, col2)
                newlist, new_hpwl = new_HPWL_cell1(
                    initial_vec, wirelength, netlist, cells_position, places, cell1)
                delta = new_hpwl - wirelength
                if delta < 0:
                    cell1_changes(initial_vec, newlist, places, cell1)
                    wirelength = new_hpwl
                else:
                    probability = np.exp(-delta/current_temperature)
                    random_number = random.random()
                    if random_number < probability:
                        cell1_changes(initial_vec, newlist, places, cell1)
                        wirelength = new_hpwl
                    else:
                        grid[row1, col1] = cell1
                        grid[row2, col2] = cell2
                        cells_position[int(cell1)] = (row1, col1)
            elif cell1 == '---' and cell2 != '---':
                cells_position[int(cell2)] = (row1, col1)
                new_list, new_hpwl = new_HPWL_cell1(
                    initial_vec, wirelength, netlist, cells_position, places, cell2)
                delta = new_hpwl - wirelength
                if delta < 0:
                    cell1_changes(initial_vec, new_list, places, cell2)
                    wirelength = new_hpwl
                else:
                    probability = np.exp(-delta/current_temperature)
                    random_number = random.random()
                    if random_number < probability:
                        cell1_changes(initial_vec, new_list, places, cell2)
                        wirelength = new_hpwl
                    else:
                        grid[row1, col1] = cell1
                        grid[row2, col2] = cell2
                        cells_position[int(cell2)] = (row2, col2)

        # decrease the temperature
        current_temperature = current_temperature * cooling_rate
        plotting_one[current_temperature] = wirelength
        plotting_two[cooling_rate] = wirelength

    return grid, current_temperature, wirelength, plotting_one, plotting_two


def bin_grid(grid, num_rows, num_cols):
    # if the cell is empty, assign 1
    # if the cell is occupied, assign 0
    bin_grid = {}
    for r in range(0, num_rows, 1):
        for c in range(0, num_cols, 1):
            if grid[r, c] == '---':
                bin_grid[r, c] = 1
            else:
                bin_grid[r, c] = 0
    return bin_grid


def main():
    # GUI
    # make window scrollable
    root = Tk()
    root.title("Simulated Annealing")
    root.geometry('1000x1000')

    # create main frame
    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=1)
    # create canvas
    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
    # add scrollbar to canvas
    my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL,
                                 command=my_canvas.yview)
    my_scrollbar.pack(side=RIGHT, fill=Y)
    # configure the canvas
    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(
        scrollregion=my_canvas.bbox("all")))
    # ceate another frame inside the canvas
    second_frame = Frame(my_canvas)
    # add that frame to a window in the canvas
    my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

    # call the random placement function
    random.seed(10)
    file_name = 't3'
    grid, cells_position, netlist, num_cells, num_connections, num_rows, num_cols, places = random_placement(
        't3.txt')
    initial_table, initial_wirelength = HPWL(netlist,
                                             cells_position, num_rows, num_cols)
    # print initial wirelength in GUI
    Label(second_frame, text="Initial Wirelength: " +
          str(initial_wirelength)).grid(row=0, column=0)

    # print grid in GUI
    for r in range(0, num_rows, 1):
        for c in range(0, num_cols, 1):
            if grid[r, c] == '---':
                Label(second_frame, text=grid[r, c], borderwidth=2, relief="groove", width=5).grid(
                    row=r+1, column=c+2)
            else:
                Label(second_frame, text=grid[r, c], borderwidth=2, relief="groove", width=5).grid(
                    row=r+1, column=c+2)

    binary_grid = bin_grid(grid, num_rows, num_cols)
    # print binary_grid in CLI
    print("Initial Binary Grid:")
    for r in range(0, num_rows, 1):
        for c in range(0, num_cols, 1):
            print(binary_grid[r, c], end=" ")
        print()

    initial_table, wirelength = HPWL(
        netlist, cells_position, num_rows, num_cols)
    initial_temperature = initial_temp(wirelength)
    final_temperature = final_temp(wirelength, num_connections)

    TWL_vs_cooling_rate = []
    temperatures = []
    wirelengths = []
    cooling_rate = [0.95, 0.9, 0.85, 0.8, 0.75, 0.7]
    x = 1
    start_time = time.time()
    for i in range(0, len(cooling_rate), 1):
        new_grid, new_temperature, final_wirelength,plotting_one,plotting_two = annealing(
            initial_temperature, final_temperature, grid, num_cells, cells_position, netlist, num_rows, num_cols, cooling_rate[i], places)
        TWL_vs_cooling_rate.append(new_temperature/final_wirelength)
        temperatures.append(new_temperature)
        wirelengths.append(final_wirelength)
        #print temperature and wirelength in csv file for each cooling rate in a separate file
        # with open('cooling_rate_'+str(cooling_rate[i])+'.csv', 'w', newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(["Temperature", "Wirelength"])
        #     for key in plotting_one.keys():
        #         writer.writerow([key, plotting_one[key]])
        
        #print cooling rate and wirelength in csv file for each cooling rate in same file name "filename.csv"
        # with open(file_name+'.csv', 'a', newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(["Cooling Rate", "Wirelength"])
        #     for key in plotting_two.keys():
        #         writer.writerow([key, plotting_two[key]])
        
        print("Final Wirelength: ", final_wirelength)
        print("Cooling Rate: ", cooling_rate[i])
        binary_grid = bin_grid(grid, num_rows, num_cols)
        for r in range(0, num_rows, 1):
            for c in range(0, num_cols, 1):
                print(binary_grid[r, c], end=" ")
            print()
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            elapsed_time = elapsed_time / 60
            print("Elapsed time:", elapsed_time, "minutes")
        else:
            print("Elapsed time:", elapsed_time, "seconds")

        # Add empty space before each new grid
        root.grid_rowconfigure((num_rows+1)*(x), minsize=10)
        # print new wirelength in GUI
        Label(second_frame, text="Final Wirelength: " + str(final_wirelength)).grid(
            row=(num_rows+1)*(x) + 1, column=0)
        # print cooling rate in GUI
        Label(second_frame, text="Cooling Rate: " + str(cooling_rate[i])).grid(
            row=(num_rows+1)*(x), column=0)

        for r in range(0, num_rows, 1):
            for c in range(0, num_cols, 1):
                if new_grid[r, c] == '---':
                    Label(second_frame, text=new_grid[r, c], borderwidth=2, relief="groove", width=5).grid(
                        row=r+(x*num_rows)+(x+1), column=c+2)
                else:
                    Label(second_frame, text=new_grid[r, c], borderwidth=2, relief="groove", width=5).grid(
                        row=r+(x*num_rows)+(x+1), column=c+2)
        x += 1
        # Add empty space after each grid
        second_frame.grid_rowconfigure((num_rows+1)*(x+1), minsize=10)
        #print plotting_one dictionary
        # print("Plotting One Dictionary:")
        # for key, value in plotting_one.items():
        #     print(key, ":", value)
        # print()
        #plot the graph
        # plt.plot(plotting_one.keys(), plotting_one.values())
        # plt.xlabel('temperature')
        # plt.ylabel('wirelength')
        # plt.title('Temperature vs Wirelength')
        # plt.show()
        #print plotting one in csv file
    #print plotting two dictionary to csv file
    
    #plot the graph
    plt.plot(plotting_two.keys(), plotting_two.values())
    
            
        
        
                
        

    root.mainloop()


if __name__ == '__main__':
    main()

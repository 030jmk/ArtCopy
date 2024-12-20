import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib.patches import Wedge

# Initialize the size of the matrix
rows, cols = 5,5

# Initialize the matrix with all cells set to 1 (white)
matrix = np.ones((rows, cols), dtype=int)

# Semicircle options for each cell, initialized to option 1
semi_options = np.full((rows, cols), 1)

# Create the figure and axis
fig, ax = plt.subplots()


def get_cell_color(value):
    """Returns the color of a cell based on its value."""
    return "black" if value == 0 else "white"


def get_random_color():
    """Returns a random color, either black or white."""
    return random.choice(["black", "white"])


def ensure_different_colors(cell_color):
    """
    Generates two semicircle colors ensuring they are not both the same
    and are not the same as the cell color.
    """
    while True:
        semi_color1 = get_random_color()
        semi_color2 = get_random_color()
        # Ensure the colors are not identical to each other and at least one differs from the cell color
        if not (semi_color1 == semi_color2 == cell_color):
            return semi_color1, semi_color2


def draw_semicircles(i, j, option, color1, color2):
    """
    Draws two semicircles for a given cell at position (i, j).
    """
    if option == 1:
        semicircle1 = Wedge(center=(j, i), r=0.489, theta1=0, theta2=180, color=color1)
        semicircle2 = Wedge(center=(j, i), r=0.489, theta1=180, theta2=360, color=color2)
    elif option == 2:
        semicircle1 = Wedge(center=(j, i), r=0.489, theta1=90, theta2=270, color=color1)
        semicircle2 = Wedge(center=(j, i), r=0.489, theta1=270, theta2=90, color=color2)
    elif option == 3:
        semicircle1 = Wedge(center=(j, i - 0.5), r=0.489, theta1=0, theta2=180, color=color1)
        semicircle2 = Wedge(center=(j, i + 0.5), r=0.489, theta1=180, theta2=0, color=color2)
    elif option == 4:
        semicircle1 = Wedge(center=(j + 0.5, i), r=0.489, theta1=90, theta2=270, color=color1)
        semicircle2 = Wedge(center=(j - 0.5, i), r=0.489, theta1=270, theta2=90, color=color2)
    ax.add_artist(semicircle1)
    ax.add_artist(semicircle2)


def initialize_display():
    """Initializes the display with all cells using option 1."""
    for i in range(rows):
        for j in range(cols):
            # Assign option 1 to all cells
            semi_options[i, j] = 1


def update_display():
    """Updates the display by drawing the current state of the matrix and semicircles."""
    ax.clear()
    cmap = plt.cm.gray
    norm = plt.Normalize(vmin=0, vmax=1)
    ax.imshow(matrix, cmap=cmap, norm=norm)

    for i in range(rows):
        for j in range(cols):
            if semi_options[i, j] != -1:
                option = semi_options[i, j]
                color1, color2 = ensure_different_colors(get_cell_color(matrix[i, j]))
                draw_semicircles(i, j, option, color1, color2)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.draw()
    plt.pause(1)


def process_cell(i, j):
    """Processes a randomly selected cell by determining its color and updating it accordingly."""
    # Get the current cell color
    cell_color = get_cell_color(matrix[i, j])

    # Generate two semicircle colors ensuring they meet the condition
    semi_color1, semi_color2 = ensure_different_colors(cell_color)

    # Flip the cell color and update the semicircle option
    matrix[i, j] = 1 - matrix[i, j]  # Flip the cell color
    semi_options[i, j] = random.choice([1, 2, 3, 4])  # Update semicircle option


# Initialize the display with all cells using option 1
initialize_display()

# Display the initial state
update_display()

# Main loop
while True:
    # Randomly select a single cell to change
    i, j = random.randint(0, rows - 1), random.randint(0, cols - 1)

    # Process the selected cell
    process_cell(i, j)

    # Update the display
    update_display()

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np

# Function to safely get integer input
def safe_input(prompt, cast_type=int):
    while True:
        try:
            return cast_type(input(prompt))
        except ValueError:
            print(f"Invalid input. Please enter a {cast_type.__name__}.")

# User inputs the number of stars
numOfStars = safe_input("Enter the number of stars: ", int)

# Array to store all star details in a nested format
stars_data = []

# Loop to collect data for each star
for i in range(numOfStars): 
    # Input: Name, x, y, z
    name = input(f"Enter name of star {i+1}: ")
    x = safe_input(f"Enter x-coordinate (Right Ascension (degrees)) of star {i+1}: ", float)
    y = safe_input(f"Enter y-coordinate (Declination (degrees)) of star {i+1}: ", float)
    z = safe_input(f"Enter z-coordinate (distance from exoplanet) of star {i+1}: ", float)
    
    # Append the star details as a list to the nested array
    stars_data.append([name, x, y, z])
lw1 = safe_input("Enter the width of the line: ", float)
MS = safe_input("Enter the size of the star: ", float)
# Output for testing
print("Stars entered:")
for star in stars_data:
    print(f"Name: {star[0]}, X: {star[1]}, Y: {star[2]}, Z: {star[3]}")



# Function to plot stars on a chart and allow interaction
def plot_star_chart(stars_data):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Set the background colors
    fig.patch.set_facecolor('#3C3C3C')  # Dark gray for figure
    ax.set_facecolor('#000000')          # Black for axes

    # Set title, x-label, and y-label colors to white
    ax.set_title('Exoplanet Star Chart', color='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

    # Create a TextBox for title input (smaller and positioned at the bottom left)
    ax_title = plt.axes([0.1, 0.01, 0.3, 0.05])  # [left, bottom, width, height]
    text_box = TextBox(ax_title, 'Rename Your Constellations:', initial='(insert name) constellation')

    def submit_title(title):
        ax.set_title(title, color='white')  # Set the title color to white
        plt.draw()

    text_box.on_submit(submit_title)

    # Store the coordinates of plotted stars for interaction
    star_coords = []
    lines = []  # List to store lines between stars

    for star in stars_data:
        # Use the star's x and y as RA and Dec, respectively
        coord = SkyCoord(ra=star[1]*u.degree, dec=star[2]*u.degree)
        ax.plot(coord.ra.deg, coord.dec.deg, marker='.', color='#FFFFFF', markersize=MS)  # White star-shaped point
        # Annotate star name and distance (z coordinate)
        ax.annotate(f"{star[0]} (z: {star[3]} ly)", (coord.ra.deg, coord.dec.deg), fontsize=6, color='white')  # Set annotation color to white
        
        # Store the coordinates for click detection
        star_coords.append((coord.ra.deg, coord.dec.deg))

    ax.set_xlabel('Right Ascension (degrees)', color='white')  # Set x-axis label color to white
    ax.set_ylabel('Declination (degrees)', color='white')  # Set y-axis label color to white

    plt.grid(False)  # Disable the grid

    selected_stars = []  # List to store selected stars
    line_objects = []  # To keep track of lines and their coordinates

    # Function to handle mouse clicks
    def on_click(event):
        if event.inaxes != ax:
            return
        
        click_x, click_y = event.xdata, event.ydata
        
        # Check if user clicked near a line
        for line, (star1, star2) in zip(line_objects, lines):
            # Check if the click is close to the line (using a small tolerance)
            d = np.abs((star2[1] - star1[1]) * click_x - (star2[0] - star1[0]) * click_y + star2[0] * star1[1] - star2[1] * star1[0]) / np.sqrt((star2[1] - star1[1]) ** 2 + (star2[0] - star1[0]) ** 2)
            if d < 0.07:  # Tolerance to detect click near the line
                # Remove the line and redraw
                line.remove()
                line_objects.remove(line)
                lines.remove((star1, star2))
                plt.draw()
                return
        
        # If no line was clicked, find the closest star to the click
        distances = [np.sqrt((click_x - sx)**2 + (click_y - sy)**2) for sx, sy in star_coords]
        closest_star_idx = np.argmin(distances)

        # The star remains white regardless of being clicked
        ax.plot(star_coords[closest_star_idx][0], star_coords[closest_star_idx][1], marker='.', color='#FFFFFF', markersize=MS)  # Mark with a white star-shaped point
        selected_stars.append(closest_star_idx)

        # Draw lines between all selected stars
        if len(selected_stars) > 1:
            star1 = star_coords[selected_stars[-2]]
            star2 = star_coords[selected_stars[-1]]
            # Draw light gray line between selected stars
            line, = ax.plot([star1[0], star2[0]], [star1[1], star2[1]], color='lightgray', lw=lw1)
            lines.append((star1, star2))  # Store the star coordinates of the line
            line_objects.append(line)  # Store the actual line object for later removal

        plt.draw()  # Update the plot

    # Connect the click event to the on_click function
    fig.canvas.mpl_connect('button_press_event', on_click)

    # Show the plot
    plt.show()

# Call the function to display the chart and enable interaction
plot_star_chart(stars_data)

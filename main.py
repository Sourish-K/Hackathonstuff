import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from astropy.coordinates import SkyCoord
import astropy.units as u
from matplotlib.backend_tools import Cursors as CU

def detect_stars(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_blur = cv2.GaussianBlur(img, (7, 7), 0)

    # Canny edge detection
    edges = cv2.Canny(img_blur, threshold1=50, threshold2=150)

    # Dilate the edges to connect nearby edges
    kernel = np.ones((5, 5), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    star_coordinates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:  # Adjusted area threshold
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                # Filter based on circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = (4 * np.pi * area) / (perimeter ** 2)
                    if circularity > 0.4:  # Adjust this value based on your image
                        star_coordinates.append((cX, cY))

    return star_coordinates

# Function to safely get integer input
def safe_input(prompt, cast_type=int):
    while True:
        try:
            return cast_type(input(prompt))
        except ValueError:
            print(f"Invalid input. Please enter a {cast_type.__name__}.")

# Get image path from user
image_path = input("Enter the path to your image file: ")  # User inputs the file directory
stars = detect_stars(image_path)

# Get star data in desired format
numOfStars = len(stars)
stars_data = []

for i, (x, y) in enumerate(stars):
    z = np.random.randint(100, 250)  # Random z-coordinate for now
    stars_data.append([f'Star{i+1}', x, y, z])

# Print star data
print(numOfStars)
for star in stars_data:
    print("*****************************")
    print(f"Star Name:    ", star[0])
    print(f"Star X-Cords: ", star[1])
    print(f"Star Y-Cords: ", star[2])
    print(f"Star Z-Cords: ", star[3])
    print("*****************************")

# Now plot the stars
def plot_star_chart(stars_data):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Set the background colors
    fig.patch.set_facecolor('#3C3C3C')  # Dark gray for figure
    ax.set_facecolor('#000000')          # Black for axes

    # Set title, x-label, and y-label colors to white
    ax.set_title('Exoplanet Star Chart', color='white')

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
    line_objects = []  # To keep track of line objects

    for star in stars_data:
        # Use the star's x and y as RA and Dec, respectively
        ax.plot(star[1], star[2], marker='.', color='#FFFFFF', markersize=5)  # White star-shaped point
        # Annotate star name and distance (z coordinate)
        ax.annotate(f"{star[0]} (z: {star[3]} ly)", (star[1], star[2]), fontsize=6, color='white')  # Set annotation color to white
        
        # Store the coordinates for click detection
        star_coords.append((star[1], star[2]))

    ax.set_xlabel('Right Ascension (degrees)', color='white')  # Set x-axis label color to white
    ax.set_ylabel('Declination (degrees)', color='white')  # Set y-axis label color to white

    plt.grid(False)  # Disable the grid

    selected_stars = []  # List to store selected stars

    # Function to handle mouse clicks
    def on_click(event):
        if event.inaxes != ax:
            return
        
        click_x, click_y = event.xdata, event.ydata
        
        # Check if user clicked near a line
        for i, (line, (star1, star2)) in enumerate(zip(line_objects, lines)):
            # Check if the click is close to the line (using a larger tolerance)
            d_numerator = (star2[1] - star1[1]) * click_x - (star2[0] - star1[0]) * click_y + star2[0] * star1[1] - star2[1] * star1[0]
            d_denominator = np.sqrt((star2[1] - star1[1]) ** 2 + (star2[0] - star1[0]) ** 2)

            # Check if the denominator is zero
            if d_denominator == 0:
                continue

            d = np.abs(d_numerator) / d_denominator  # Compute distance to line

            if d < 1.5:  # Increased tolerance to detect click near the line
                # Remove the line and redraw
                line.remove()
                del line_objects[i]  # Remove the line from the list of line objects
                del lines[i]  # Remove the corresponding star coordinates
                plt.draw()
                return
        
        # If no line was clicked, find the closest star to the click
        distances = [np.sqrt((click_x - sx)**2 + (click_y - sy)**2) for sx, sy in star_coords]
        closest_star_idx = np.argmin(distances)

        # The star remains white regardless of being clicked
        ax.plot(star_coords[closest_star_idx][0], star_coords[closest_star_idx][1], marker='.', color='#FFFFFF', markersize=5)  # Mark with a white star-shaped point
        selected_stars.append(closest_star_idx)

        # Draw lines between all selected stars
        if len(selected_stars) > 1:
            star1 = star_coords[selected_stars[-2]]
            star2 = star_coords[selected_stars[-1]]

            # Avoid drawing a line if the two stars are the same
            if star1 != star2:
                # Draw light gray line between selected stars
                line, = ax.plot([star1[0], star2[0]], [star1[1], star2[1]], color='lightgray', lw=0.5)
                lines.append((star1, star2))  # Store the star coordinates of the line
                line_objects.append(line)  # Store the actual line object for later removal

        plt.draw()  # Update the plot

    # Function to change cursor when hovering over stars or lines
    def on_hover(event):
        if event.inaxes == ax:
            for star in star_coords:
                if np.sqrt((event.xdata - star[0]) ** 2 + (event.ydata - star[1]) ** 2) < 5:
                    fig.canvas.set_cursor(CU.HAND)  # Change cursor when hovering over a star
                    return
            for line, (star1, star2) in zip(line_objects, lines):
                d = np.abs((star2[1] - star1[1]) * event.xdata - (star2[0] - star1[0]) * event.ydata + star2[0] * star1[1] - star2[1] * star1[0]) / (np.sqrt((star2[1] - star1[1]) ** 2 + (star2[0] - star1[0]) ** 2) + 1)  # Adjusted calculation
                if d < 5:  # Tolerance for hovering over lines
                    fig.canvas.set_cursor(CU.HAND)  # Change cursor when hovering over a line
                    return

            fig.canvas.set_cursor(CU.POINTER)  # Reset cursor if not hovering over any stars or lines

    # Connect the hover event to the on_hover function
    fig.canvas.mpl_connect('motion_notify_event', on_hover)

    # Connect the click event to the on_click function
    fig.canvas.mpl_connect('button_press_event', on_click)

    # Show the plot
    plt.show()

# Call the function to display the chart and enable interaction
plot_star_chart(stars_data)

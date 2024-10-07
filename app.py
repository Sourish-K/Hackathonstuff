import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from matplotlib.widgets import TextBox
from matplotlib.backend_tools import Cursors as CU

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Function to detect stars in an image (auto mode)
def detect_stars(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_blur = cv2.GaussianBlur(img, (7, 7), 0)
    edges = cv2.Canny(img_blur, threshold1=50, threshold2=150)
    kernel = np.ones((5, 5), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    star_coordinates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = (4 * np.pi * area) / (perimeter ** 2)
                    if circularity > 0.4:
                        star_coordinates.append((cX, cY))
    return star_coordinates

# Function to safely get input from users (manual mode)
def safe_input(prompt, cast_type=int):
    while True:
        try:
            return cast_type(input(prompt))
        except ValueError:
            print(f"Invalid input. Please enter a {cast_type.__name__}.")

# Function to get star data from the user manually
def get_star_data(data):
    stars_data = []
    for star in data:
        name = star['name']
        x = star['ra']
        y = star['dec']
        z = star['dist']
        stars_data.append([name, x, y, z])
    return stars_data

# Function to plot stars and enable interaction
def plot_star_chart(stars_data, line_width, star_size):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Set background colors
    fig.patch.set_facecolor('#3C3C3C')
    ax.set_facecolor('#000000')
    ax.set_title('Exoplanet Star Chart', color='white')
    ax.set_xlabel('Right Ascension (degrees)', color='white')
    ax.set_ylabel('Declination (degrees)', color='white')

    # TextBox to rename constellations
    ax_title = plt.axes([0.1, 0.01, 0.3, 0.05])
    text_box = TextBox(ax_title, 'Rename Your Constellations:', initial='(insert name) constellation')

    def submit_title(title):
        ax.set_title(title, color='white')
        plt.draw()

    text_box.on_submit(submit_title)

    star_coords = []
    lines = []  # Store lines between stars
    line_objects = []
    selected_stars = []  # Track selected stars

    for star in stars_data:
        ax.plot(star[1], star[2], marker='.', color='#FFFFFF', markersize=star_size)
        ax.annotate(f"{star[0]} (z: {star[3]} ly)", (star[1], star[2]), fontsize=6, color='white')
        star_coords.append((star[1], star[2]))

    plt.grid(False)

    # Handling clicking and drawing lines between stars
    def on_click(event):
        if event.inaxes != ax:
            return

        click_x, click_y = event.xdata, event.ydata

        # Check if user clicked near a line (to remove it)
        for i, (line, (star1, star2)) in enumerate(zip(line_objects, lines)):
            d_numerator = (star2[1] - star1[1]) * click_x - (star2[0] - star1[0]) * click_y + star2[0] * star1[1] - star2[1] * star1[0]
            d_denominator = np.sqrt((star2[1] - star1[1]) ** 2 + (star2[0] - star1[0]) ** 2)
            if d_denominator == 0:
                continue
            d = np.abs(d_numerator) / d_denominator
            if d < 2.5:  # Tolerance to detect click near the line
                line.remove()
                del line_objects[i]
                del lines[i]
                plt.draw()
                return

        # If no line was clicked, find the closest star
        distances = [np.sqrt((click_x - sx) ** 2 + (click_y - sy) ** 2) for sx, sy in star_coords]
        closest_star_idx = np.argmin(distances)

        # Mark the closest star
        ax.plot(star_coords[closest_star_idx][0], star_coords[closest_star_idx][1], marker='.', color='#FFFFFF', markersize=star_size)
        selected_stars.append(closest_star_idx)

        # Draw lines between selected stars
        if len(selected_stars) == 2:
            star1 = star_coords[selected_stars[0]]
            star2 = star_coords[selected_stars[1]]
            if star1 != star2:
                line, = ax.plot([star1[0], star2[0]], [star1[1], star2[1]], color='lightgray', lw=line_width)
                lines.append((star1, star2))
                line_objects.append(line)
            selected_stars.clear()

        plt.draw()

    def on_hover(event):
        if event.inaxes == ax:
            for star in star_coords:
                if np.sqrt((event.xdata - star[0]) ** 2 + (event.ydata - star[1]) ** 2) < 5:
                    fig.canvas.set_cursor(CU.HAND)
                    return
            for line in line_objects:
                if line.contains(event):
                    fig.canvas.set_cursor(CU.HAND)
                    return
        fig.canvas.set_cursor(CU.POINTER)

    # Connect hover and click events
    fig.canvas.mpl_connect('motion_notify_event', on_hover)
    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show()

@app.route('/')
def index():
    return render_template('index.html')

# Manual mode route
@app.route('/manual', methods=['POST'])
def manual_mode():
    data = request.get_json()  # Get JSON data sent from the client
    stars_data = get_star_data(data['stars'])  # Pass star data to get_star_data()
    line_width = float(data['lineWidth'])  # Get line width from the data
    star_size = float(data['starSize'])  # Get star size from the data
    plot_star_chart(stars_data, line_width, star_size)
    return jsonify({"status": "success"})

# Auto mode route
@app.route('/auto', methods=['POST'])
def auto_mode():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        stars = detect_stars(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        stars_data = []
        for i, (x, y) in enumerate(stars):
            z = np.random.randint(100, 250)
            stars_data.append([f'Star{i+1}', x, y, z])

        line_width = float(request.form.get('lineWidth'))
        star_size = float(request.form.get('starSize'))

        plot_star_chart(stars_data, line_width, star_size)
        return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)

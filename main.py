import matplotlib.pyplot as plt

class Star:
    def __init__(self, name, x, y, z):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

class Constellation:
    def __init__(self, name):
        self.name = name
        self.star_indices = []  # Indices of stars that form the constellation

def plot_star_chart(stars_data, lines=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title('Exoplanet Star Chart')
    
    for star in stars_data:
        ax.plot(star.x, star.y, 'ro')  # Plot star as a red point
        ax.annotate(f"{star.name} (z: {star.z})", (star.x, star.y), fontsize=12)
    
    # Draw lines for constellations
    if lines:
        for line in lines:
            ax.plot(line[0], line[1], 'b-')  # Blue lines for constellations
    
    ax.set_xlabel('Right Ascension (degrees)')
    ax.set_ylabel('Declination (degrees)')
    plt.grid(True)
    plt.show()

def main():
    continue_plotting = 'y'
    constellations = []

    while continue_plotting.lower() == 'y':
        numOfStars = int(input("Enter the number of stars: "))
        stars_data = []

        # Get star data from the user
        for i in range(numOfStars):
            name = input(f"Enter name of star {i + 1}: ")
            x = float(input(f"Enter x-coordinate (right ascension) of star {i + 1}: "))
            y = float(input(f"Enter y-coordinate (declination) of star {i + 1}: "))
            z = float(input(f"Enter z-coordinate (distance from exoplanet) of star {i + 1}: "))
            stars_data.append(Star(name, x, y, z))

        # Plot the stars
        plot_star_chart(stars_data)

        # Create lines between stars
        selected_stars = []
        lines = []
        
        # User can click on stars to create lines
        def on_click(event):
            if event.inaxes is not None:
                # Check if a star is clicked
                clicked_x, clicked_y = event.xdata, event.ydata
                for i, star in enumerate(stars_data):
                    if abs(star.x - clicked_x) < 0.5 and abs(star.y - clicked_y) < 0.5:
                        if i not in selected_stars:
                            selected_stars.append(i)
                        else:
                            selected_stars.remove(i)
                        if len(selected_stars) == 2:
                            # Draw line between the two stars
                            x_values = [stars_data[selected_stars[0]].x, stars_data[selected_stars[1]].x]
                            y_values = [stars_data[selected_stars[0]].y, stars_data[selected_stars[1]].y]
                            lines.append((x_values, y_values))
                            selected_stars.clear()
                        break
                plt.clf()  # Clear the plot to redraw
                plot_star_chart(stars_data, lines)  # Redraw stars and lines

        # Connect the click event
        cid = plt.gcf().canvas.mpl_connect('button_press_event', on_click)

        # Keep the plot open until closed
        plt.show()

        # Ask if user wants to create a constellation
        create_constellation = input("Do you want to create a constellation? (y/n): ")
        if create_constellation.lower() == 'y':
            constellation_name = input("Enter name for the constellation: ")
            new_constellation = Constellation(constellation_name)

            # Select stars for the constellation
            stars_in_constellation = int(input("How many stars do you want to include in the constellation? "))
            for _ in range(stars_in_constellation):
                star_index = int(input(f"Enter index of the star (0 to {numOfStars - 1}): "))
                if 0 <= star_index < numOfStars:
                    new_constellation.star_indices.append(star_index)

            constellations.append(new_constellation)

            # Output the created constellations
            print("Constellations created:")
            for constellation in constellations:
                print(f"Name: {constellation.name}, Stars: {[stars_data[i].name for i in constellation.star_indices]}")

        continue_plotting = input("Do you want to plot more stars? (y/n): ")

    print("Exiting program. Goodbye!")

if __name__ == "__main__":
    main()

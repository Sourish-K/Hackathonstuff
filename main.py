import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u



# User inputs the number of stars
numOfStars = int(input("Enter the number of stars: "))

# Array to store all star details in a nested format
stars_data = []

# Loop to collect data for each star
for i in range(numOfStars): 
    # Input: Name, x, y, z
    name = input(f"Enter name of star {i+1}: ")
    x = float(input(f"Enter x-coordinate (right ascension) of star {i+1}: "))
    y = float(input(f"Enter y-coordinate (declination) of star {i+1}: "))
    z = float(input(f"Enter z-coordinate (distance from exoplanet) of star {i+1}: "))
    
    # Append the star details as a list to the nested array
    stars_data.append([name, x, y, z])

# Output for testing
print("Stars entered:")
for star in stars_data:
    print(f"Name: {star[0]}, X: {star[1]}, Y: {star[2]}, Z: {star[3]}")



       

# Function to plot stars on a chart
def plot_star_chart(stars_data):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title('Exoplanet Star Chart')

    for stars_data in stars_data:
        coord = SkyCoord(ra=stars_data['ra']*u.degree, dec=stars_data['dec']*u.degree)
        ax.plot(coord.ra.deg, coord.dec.deg, 'ro')  # Plot star as a red point
        # Annotate star name and distance (z coordinate)
        ax.annotate(f"{stars_data['name']} (z: {stars_data['distance']} ly)", 
                    (coord.ra.deg, coord.dec.deg), fontsize=12)

    ax.set_xlabel('Right Ascension (degrees)')
    ax.set_ylabel('Declination (degrees)')
    plt.grid(True)
    plt.show()

# Call the function to display the chart
plot_star_chart(stars_data)


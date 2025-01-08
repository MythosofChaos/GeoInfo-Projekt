# https://blog.finxter.com/5-best-ways-to-color-identification-in-images-using-python-and-opencv/
# Method 2: Using KMeans Clustering
#pip install opencv-python
#pip install scikit-learn
#pip install matplotlib
# NEEDS A PICTURE IN CURRENT DIRECTORY NAMED "image.jpg"
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def find_dominant_colors(image, k=4): #k = number of clusters / colors
    # resize image to reduce computation time
    image = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA)
    # reshape image to a list of pixels
    pixels = image.reshape((-1, 3))
    
    # perform KMeans
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_ # get colors as RGB values
    
    # calculate percentage of each color
    labels = kmeans.labels_
    label_counts = np.bincount(labels) # count amount of each label
    percentages = label_counts / len(labels) * 100

    return colors.astype(int), percentages

def get_color_description(color):
    # RGB range color descriptions
    color_descriptions = [
        {"range": ((90, 50, 40), (160, 90, 70)), "name": "Reddish-Brown"},
        {"range": ((140, 100, 80), (200, 160, 130)), "name": "Light Brown"},
        {"range": ((50, 30, 20), (120, 90, 70)), "name": "Dark Brown"},
        {"range": ((60, 60, 60), (160, 160, 160)), "name": "Gray"},
        {"range": ((10, 10, 10), (60, 60, 60)), "name": "Black"},
        {"range": ((160, 80, 50), (210, 120, 80)), "name": "Reddish-Orange"},
        {"range": ((170, 140, 90), (220, 180, 120)), "name": "Yellowish-Brown"},
        {"range": ((180, 180, 180), (255, 255, 255)), "name": "Light Gray"},
        {"range": ((100, 120, 200), (255, 255, 255)), "name": "Blue"},
    ]
    # return the color description if available
    for desc in color_descriptions:
        lower, upper = desc["range"]
        if all(lower[i] <= color[i] <= upper[i] for i in range(3)):
            return desc["name"]
    return "Unknown"

def is_desert_pavement(colors, percentages):
    # RGB ranges for desert pavement definitions
    desert_ranges = [
        ((90, 50, 40), (160, 90, 70)),   # Reddish-brown
        ((140, 100, 80), (200, 160, 130)), # Light brown
        ((50, 30, 20), (120, 90, 70)),  # Dark brown
        ((60, 60, 60), (150, 150, 150)),  # Gray
        ((10, 10, 10), (60, 60, 60)),  # Black
        ((160, 80, 50), (210, 120, 80)),  # Reddish-Orange
        ((170, 140, 90), (220, 180, 120)),  # Yellowish-Brown
        ((180, 180, 180), (255, 255, 255)),  # Light Gray
        #((100, 120, 200), (255, 255, 255)),  # Sky
        #((0, 80, 0), (100, 255, 100)),       # Vegetation
        #((0, 0, 0), (50, 50, 50)),           # Shadows
        #((0, 50, 100), (70, 150, 200)),      # Water
        #((200, 200, 200), (255, 255, 255))   # Bright highlights
    ]

    desert_percentage = 0
    for color, percentage in zip(colors, percentages):
        # check if the color falls within any of the desert ranges
        in_range = any( # in_range = bool
            all(lower[i] <= color[i] <= upper[i] for i in range(3))
            for lower, upper in desert_ranges
        )
        if in_range:
            desert_percentage += percentage

    return desert_percentage > 50  # If > 70% of the image is desert pavement its considered a match
    #TODO: find threshold for desert pavement needed in picture

# filepath
image_path = os.path.join(os.path.dirname(__file__), 'image.jpg')
image = cv2.imread(image_path) # load the image

# Check if the image was loaded successfully
if image is None:
    raise FileNotFoundError(f"Image file '{image_path}' not found.")

# find dominant colors and their percentages
dominant_colors, percentages = find_dominant_colors(image)

print("Dominant colors and their percentages:")
for color, percentage in zip(dominant_colors, percentages):
    description = get_color_description(color)
    print(f"Color: {color} || Percentage: {percentage:.2f}% || Description: {description}")

# check if the image resembles desert pavements
if is_desert_pavement(dominant_colors, percentages):
    print("This image resembles desert pavements.")
else:
    print("This image does not resemble desert pavements.")

# Plot the dominant colors with their percentages
def plot_colors(colors, percentages):
    # create a figure and set of subplots
    fig, ax = plt.subplots(1, len(colors), figsize=(12, 2))
    
    for i, (color, percentage) in enumerate(zip(colors, percentages)):
        # make a rectangle filled with the color for visualization
        rect = np.zeros((100, 100, 3), dtype=np.uint8)
        rect[:, :] = color
        ax[i].imshow(rect)
        ax[i].axis('off')
        ax[i].set_title(f"{percentage:.2f}%")
    
    plt.show()

plot_colors(dominant_colors, percentages) #plot colors
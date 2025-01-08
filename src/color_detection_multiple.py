# https://blog.finxter.com/5-best-ways-to-color-identification-in-images-using-python-and-opencv/
# Method 2: Using KMeans Clustering
#pip install opencv-python
#pip install scikit-learn
#pip install matplotlib
#TODO: TEST WITH ONLY DESERT PAVEMENT PICTURES AND ADJUST ITERATIVE
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import shutil
from pathlib import Path
from sklearn.cluster import KMeans

def find_dominant_colors(image, k=4): # k = number of clusters / colors
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

    return desert_percentage > 70  # If > 70% of the image is desert pavement its considered a match

# Define the input and output directories
base_dir = Path(__file__).parent.parent
input_dir = base_dir / 'out' / 'downloaded_photos'
output_dir_desert = base_dir / 'out' / 'possible_desert_pavements'
output_dir_no_desert = base_dir / 'out' / 'no_desert_pavement'

# Create the output directories if they do not exist
os.makedirs(output_dir_desert, exist_ok=True)
os.makedirs(output_dir_no_desert, exist_ok=True)

# iterate through all images in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.jpg'):
        image_path = input_dir / filename
        image = cv2.imread(str(image_path)) # load the image

        # check if image was loaded successfully
        if image is None:
            print(f"Failed to load image: {image_path}")
            continue

        # find dominant colors and their percentages
        dominant_colors, percentages = find_dominant_colors(image)

        # Check if the image resembles desert pavements
        if is_desert_pavement(dominant_colors, percentages):
            print(f"{filename} resembles desert pavements.")
            shutil.move(str(image_path), str(output_dir_desert / filename))
        else:
            print(f"{filename} does not resemble desert pavements.")
            shutil.move(str(image_path), str(output_dir_no_desert / filename))
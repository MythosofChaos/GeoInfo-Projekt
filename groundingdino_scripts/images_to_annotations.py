import os
from PIL import Image
### RUN ONCE TO CREATE THE DATASET FOLDERS ###

base_dir = 'dataset' #base directory

# paths to dataset
image_dir = os.path.join(base_dir, 'images')
annotation_dir = os.path.join(base_dir, 'annotations')

os.makedirs(image_dir, exist_ok=True)
os.makedirs(annotation_dir, exist_ok=True)

# function to generate annotation file
def generate_annotation_file(image_filename, image_size):
    annotation_filename = image_filename.replace('.jpg', '.txt').replace('.png', '.txt')
    annotation_path = os.path.join(annotation_dir, annotation_filename)
    
    with open(annotation_path, 'w') as f:
        # Write the caption
        f.write("a picture containing desert pavements\n")
        
        # generate bounding box coordinates (x, y, width, height)
        #0,0 is the top left corner of the image > we want to capture the whole image
        width, height = image_size
        x_min, y_min = 0, 0
        x_max, y_max = width, height
        f.write(f"{x_min} {y_min} {x_max} {y_max}\n")

# iterate through all images and generate annotation files
for filename in os.listdir(image_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(image_dir, filename)
        
        # get image dimensions
        with Image.open(img_path) as img:
            width, height = img.size
        
        generate_annotation_file(filename, (width, height)) # generate annotation file

print("Annotation files generated successfully.")
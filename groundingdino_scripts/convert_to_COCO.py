import os
import json
from PIL import Image

# paths
image_dir = 'dataset/images'
annotation_dir = 'dataset/annotations'
output_dir = 'dataset'

# COCO format structure
coco_format = {
    "images": [],
    "annotations": [],
    "categories": []
}

category_id = 1  # Start category ID
category_name = 'desert pavement'  # category name, can be extended to multiple categories
coco_format["categories"].append({"id": category_id, "name": category_name})

annotation_id = 1  # Annotation ID
image_id = 0  # Start image IDs from 0

# iterate through all images and their corresponding annotations
for filename in os.listdir(image_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(image_dir, filename)
        ann_path = os.path.join(annotation_dir, filename.replace('.jpg', '.txt').replace('.png', '.txt'))

        # get image dimensions
        with Image.open(img_path) as img:
            width, height = img.size

        # add image metadata to COCO format
        coco_format["images"].append({
            "id": image_id,
            "file_name": filename,
            "width": width,
            "height": height
        })

        # read and process annotations for the current image
        with open(ann_path, 'r') as ann_file:
            lines = ann_file.readlines()
            if len(lines) >= 2:
                try:
                    # first line: caption (string)
                    caption = lines[0].strip()

                    # second line: bounding box in the form "x y width height"
                    #.strip().split() removes leading/trailing whitespaces and splits by whitespaces
                    bbox = lines[1].strip().split() 

                    # ensure all bbox values are integers
                    if len(bbox) == 4:
                        x, y, w, h = map(int, bbox)
                    else:
                        raise ValueError(f"Invalid bbox format in file {ann_path}.")

                    # add annotation to COCO format
                    coco_format["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": category_id,
                        "bbox": [x, y, w, h],
                        "area": w * h,
                        "caption": caption
                    })
                    annotation_id += 1

                except ValueError as e:
                    print(f"Skipping annotation due to error in file {ann_path}: {e}")

        # increment img id
        image_id += 1

# ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# save to JSON
json_output_path = os.path.join(output_dir, 'COCO.json')
with open(json_output_path, 'w') as json_file:
    json.dump(coco_format, json_file)

print(f"Annotations saved to {json_output_path}")

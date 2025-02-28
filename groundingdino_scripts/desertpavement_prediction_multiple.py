import os
import json
from groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2
import matplotlib.pyplot as plt
import torch
import numpy as np

base_dir = os.getcwd()

# Define paths relative to the base directory
model_config_path = os.path.join(base_dir, "GroundingDINO", "groundingdino", "config", "GroundingDINO_SwinT_OGC.py")
model_weights_path = os.path.join(base_dir, "GroundingDINO", "weights", "groundingdino_swint_ogc.pth")
downloaded_photos_dir = os.path.join(base_dir, "out", "downloaded_photos")
annotated_desert_pavements_dir = os.path.join(base_dir, "out", "annotated_desert_pavements")
output_dir_desert = os.path.join(base_dir, "out", "annotated_desert_pavements")
output_dir_no_desert = os.path.join(base_dir, "out", "annotated_not_desert_pavements")
output_json_path = os.path.join(base_dir, "groundingdino_scripts", "logits_phrases_all.json")

# create output directories if they do not exist
os.makedirs(output_dir_desert, exist_ok=True)
os.makedirs(output_dir_no_desert, exist_ok=True)

# TOGGLE FOR USING ANNOTATED FOLDER AS THE ORIGIN, might be useful for debugging
use_annotated_as_origin = False

# set the images directory based on the toggle
images_dir = annotated_desert_pavements_dir if use_annotated_as_origin else downloaded_photos_dir

# Load the model
model = load_model(model_config_path, model_weights_path)
print("Model loaded successfully.")

# define parameters
TEXT_PROMPT = "road markings . desert pavement . building . stick . pen . orange stripes"
#TEXT_PROMPT = "desert pavement"
BOX_THRESHOLD = 0.35  # If the box confidence is less than 0.35, remove the box
TEXT_THRESHOLD = 0.25  # If the text confidence is less than 0.25, show no text
# NMS_THRESHOLD = 0.5  # If overlap is more than 0.5, remove the box with lower confidence
# MAX_DETECTIONS = 100  # Keep the most confident 100 detections
# IMAGE_SIZE = (640, 640)  # Resize the image to 640x640 to speed up inference

### IF SEARCH IS DONE WITH MULTIPLE CLASSES ADJUST THE SIMILAR AND THE EXCLUDE ITEMS
### IT IS RECOMMENDED TO USE ONLY ONE TEXT PROMPT PER RUN AS THE MODEL GETS WORSE WITH MULTIPLE
### THEREFORE AN ITERATIVE APPROACH IS RECOMMENDED

# list of similar items that can be confused with desert pavement
similar = ["sand", "gravel"]
# those that should be excluded
exclude_items = ["asphalt", "building", "city", "water", "lawn", "road markings", "orange stripes", "concrete"]

# set desert_pavement_confidence to 100% if not directly looking for "desert pavement"
if "desert pavement" not in TEXT_PROMPT:
    desert_pavement_confidence_override = True
else:
    desert_pavement_confidence_override = False

loop = 0
# iterate over all images in the images directory
for image_filename in os.listdir(images_dir):
    if image_filename.endswith(".jpg") or image_filename.endswith(".png"):
        image_path = os.path.join(images_dir, image_filename)

        image_source, image = load_image(image_path) # load the image

        ## perform prediction
        boxes, logits, phrases = predict(
            model=model,
            image=image,
            caption=TEXT_PROMPT,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD
            # nms_threshold=NMS_THRESHOLD,
            # max_detections=MAX_DETECTIONS,
            # image_size=IMAGE_SIZE
        )

        # print(f"phrases: {phrases}")
        # print(f"logits: {logits}")
        # print(f"image_filename: {image_filename}")

        # check if "desert pavement" is present and compare with items in the "similar" list
        contains_desert_pavement = "desert pavement" in phrases
        desert_pavement_confidence = max([logit for logit, phrase in zip(logits, phrases) if phrase == "desert pavement"], default=0)
        similar_confidence = max([logit for logit, phrase in zip(logits, phrases) if phrase in similar], default=0)
        
        #override the desert pavement confidence if not directly looking for it
        if desert_pavement_confidence_override: 
            desert_pavement_confidence = 1.0

        # check if excluded items are present with high confidence
        exclude_confidences = {item: max([logit for logit, phrase in zip(logits, phrases) if phrase == item], default=0) for item in exclude_items}
        exclude_confidences = {item: float(conf) if isinstance(conf, torch.Tensor) else conf for item, conf in exclude_confidences.items()}
        road_confidence = exclude_confidences.get("road", 0)
        building_confidence = exclude_confidences.get("building", 0)
        city_confidence = exclude_confidences.get("city", 0)
        water_confidence = exclude_confidences.get("water", 0)
        lawn_confidence = exclude_confidences.get("lawn", 0)
        road_markings_confidence = exclude_confidences.get("road markings", 0)
        orange_stripes_confidence = exclude_confidences.get("orange stripes", 0)
        stick_confidence = exclude_confidences.get("stick", 0) # not excluded but used for debugging
        pen_confidence = exclude_confidences.get("pen", 0) # not excluded but used for debugging
        asphalt_confidence = exclude_confidences.get("asphalt", 0) # not excluded but used for debugging

        # convert logits to a list if it is a PyTorch tensor
        logits_list = logits.tolist() if isinstance(logits, torch.Tensor) else logits

        # ensure desert_pavement_confidence and similar_confidence are JSON-serializable
        desert_pavement_confidence = float(desert_pavement_confidence) if isinstance(desert_pavement_confidence, torch.Tensor) else desert_pavement_confidence
        similar_confidence = float(similar_confidence) if isinstance(similar_confidence, torch.Tensor) else similar_confidence
        
        # prepare the result for the current image
        result = {
            "image_filename": image_filename,
            "logits": logits_list,
            "phrases": phrases,
            "contains_desert_pavement": contains_desert_pavement,
            "desert_pavement_confidence": desert_pavement_confidence,
            "similar_confidence": similar_confidence,
            "exclude_confidences": exclude_confidences
        }


        with open(output_json_path, 'a') as json_file:  # write the result to the JSON file
            json_file.write(json.dumps(result) + "\n")

        # determine the output directory based on the conditions with 5% margin
        if desert_pavement_confidence >= 0.40 and desert_pavement_confidence >= (similar_confidence - 0.05):
            if road_confidence >= 0.40 or building_confidence >= 0.35 or city_confidence >= 0.35 or water_confidence >= 0.40 or lawn_confidence >= 0.40 or road_markings_confidence >= 0.30 or orange_stripes_confidence >= 0.30 or asphalt_confidence >= 0.30:
                output_dir = output_dir_no_desert
            else:
                output_dir = output_dir_desert
        elif stick_confidence >= 0.30 or pen_confidence >= 0.30:
            output_dir = output_dir_desert
        else:
            output_dir = output_dir_no_desert
        
        # output_image_path = os.path.join(output_dir, f"{image_filename}")
        # cv2.imwrite(output_image_path, np.array(image))  # Convert to NumPy before saving

        #change draw_boxes to False if you want to save the image without the boxes
        #adjustments for this functions were made in inference.py (/groundingdino/util/*.py)
        annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases, draw_boxes=True)

        output_image_path = os.path.join(output_dir, f"annotated_{image_filename}")
        cv2.imwrite(output_image_path, annotated_frame)

        loop += 1
        if loop % 10 == 0:
            print(f"loop: {loop}")
        

print("Predictions completed for all images.")
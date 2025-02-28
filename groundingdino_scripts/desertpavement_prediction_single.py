### CREATE A NEW FOLDER IN THE GROUNDING DINO DIRECTORY NAMED "in" AND PLACE THE IMAGE TO BE ANALYZED IN IT ###
import os
#import torch
from groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2
import matplotlib.pyplot as plt
import json
#OPTIONAL
import warnings
# import torch.profiler

# with torch.profiler.profile() as prof:
#     code
# print(prof.key_averages().table(sort_by="cuda_time_total"))

# suppress warnings
warnings.filterwarnings("ignore") #definitley good programming practice

# base directory and paths relative to the base directory
base_dir = os.getcwd()

model_config_path = os.path.join(base_dir, "GroundingDINO", "groundingdino", "config", "GroundingDINO_SwinT_OGC.py")
model_weights_path = os.path.join(base_dir, "GroundingDINO", "weights", "groundingdino_swint_ogc.pth")
image_path = os.path.join(base_dir, "GroundingDINO", "in", "image.jpg")
output_dir_desert = os.path.join(base_dir, "out", "annotated_desert_pavements")
output_dir_no_desert = os.path.join(base_dir, "out", "annotated_not_desert_pavements")

# create the output directories if not existing
os.makedirs(output_dir_desert, exist_ok=True)
os.makedirs(output_dir_no_desert, exist_ok=True)

model = load_model(model_config_path, model_weights_path) # load the model
print("Model loaded successfully.")

# define search parameters
TEXT_PROMPT = " desert pavement . dog . bush . sky . collar . mountain . clouds . desert grass . stone . tire . human . building . road . sign . car . shadow . tree . stick . pen . sand . gravel . city . water . lawn . dirt . cracked earth . concrete . dry mud . pebbles . rocky ground . wasteland rocks" 
#plant . stick . pen . greenery . sand . gravel . dirt . earth . desert pavement . human . road . street . road markings . orange stripes"
BOX_THRESHOLD = 0.35  # If the box confidence is less than 0.35, remove the box
TEXT_THRESHOLD = 0.25  # If the text confidence is less than 0.25, show no text
# NMS_THRESHOLD = 0.5  # If overlap is more than 0.5, remove the box with lower confidence
# MAX_DETECTIONS = 100  # Keep the most confident 100 detections
# IMAGE_SIZE = (640, 640)  # Resize the image to 640x640 to speed up inference

#list of similar items that can be confused with desert pavement
similar = ["sand", "gravel"]

# load the image
image_source, image = load_image(image_path)

# perform prediction
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

print(f"phrases: {phrases}")
print(f"logits: {logits}")

# save logits and phrases to a JSON file
output_json_path = os.path.join(base_dir, "groundingdino_scripts", "logits_phrases.json")
with open(output_json_path, 'w') as json_file:
    json.dump({"logits": logits.tolist(), "phrases": phrases}, json_file, indent=4)

# check if "desert pavement" is present and compare with items in the "similar" list
contains_desert_pavement = "desert pavement" in phrases
desert_pavement_confidence = max([logit for logit, phrase in zip(logits, phrases) if phrase == "desert pavement"], default=0)
similar_confidence = max([logit for logit, phrase in zip(logits, phrases) if phrase in similar], default=0)

print(f"Contains desert pavement: {contains_desert_pavement}")
print(f"Desert pavement confidence: {desert_pavement_confidence}")
print(f"Similar items confidence: {similar_confidence}")

# determine output directory based on conditions
if desert_pavement_confidence >= 0.5 and desert_pavement_confidence > similar_confidence:
    output_dir = output_dir_desert
else:
    output_dir = output_dir_no_desert

# annotate the image with boxes and phrases
annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases, draw_boxes=True)

# save the annotated image
output_image_path = os.path.join(output_dir, "annotated_image.jpg")
cv2.imwrite(output_image_path, annotated_frame)

# visualize the annotated image using matplotlib
plt.imshow(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()

# print(torch.__version__)
# print(torch.cuda.is_available())
# print(torch.version.cuda)


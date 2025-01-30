from groundingdino.util.inference import load_model, load_image, predict, annotate
import cv2
import matplotlib.pyplot as plt
import os
import time
#TODO: use prediction on non self trained model > use self trained model > compare results
#TODO: weitertrainieren, Tag-Liste, GPU ID, general tutorial in README, more GPU Power
#done?: relative paths, speicher logits and phrases in JSON, Apache License in README
start_time_ALL = time.time()
# Load the model

start_time_model = time.time()
model = load_model("GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py", "GroundingDINO/weights/groundingdino_swint_ogc.pth")
elapsed_time_model = time.time() - start_time_model
print(f"Model loading time: {elapsed_time_model} seconds")

# define paths and parameters
IMAGE_PATH = "GroundingDINO/in/image.jpg"
TEXT_PROMPT = "sun . plant . stick . pen . dog . greenery . sky . sand . gravel . desert pavement . human . shoe"
BOX_THRESHOLD = 0.35 # If the box confidence is less than 0.35, remove the box
TEXT_THRESHOLD = 0.25 # If the text confidence is less than 0.25, show no text
# NMS_THRESHOLD = 0.5 # If overlap is more than 0.5, remove the box with lower confidence
# MAX_DETECTIONS = 100 # Keep the most confident 100 detections
# IMAGE_SIZE = (640, 640) # Resize the image to 640x640 to speed up inference

# load image
image_source, image = load_image(IMAGE_PATH)

start_time = time.time()
# perform prediction
boxes, logits, phrases = predict(
    model=model,
    image=image,
    caption=TEXT_PROMPT,
    box_threshold=BOX_THRESHOLD,
    text_threshold=TEXT_THRESHOLD
    #nms_threshold=NMS_THRESHOLD,
    #max_detections=MAX_DETECTIONS,
    #image_size=IMAGE_SIZE
)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time Prediction: {elapsed_time} seconds")

print(f"phrases: {phrases}")
print(f"logits: {logits}")

contains_desert_pavement = "desert pavement" in phrases
print(f"Contains desert pavement: {contains_desert_pavement}")


start_time = time.time()
# annotate the image with boxes and phrases
annotated_frame = annotate(image_source=image_source, boxes=boxes, logits=logits, phrases=phrases)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time annotate: {elapsed_time} seconds")


output_dir = os.path.join("out")
os.makedirs(output_dir, exist_ok=True)

output_image_path = os.path.join(output_dir, "annotated_image.jpg")
cv2.imwrite(output_image_path, annotated_frame)

elapsed_time_ALL = time.time() - start_time_ALL
print(f"Elapsed time ALL: {elapsed_time_ALL} seconds")

# visualize the annotated image using matplotlib
plt.imshow(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.show()

# print(torch.__version__)
# print(torch.cuda.is_available())
# print(torch.version.cuda)

import flickrapi
import json
import requests
import glob
from pathlib import Path
import os
import time
from dotenv import load_dotenv
import csv

# flag for printing image URLs and metadata
PRINT_DEBUG_INFO = False
PRINT_DEBUG_INFO_PHOTO_NAMES = False

#obfuscate API keys
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'FlickrAPI_keys.env'))
api_key = os.getenv('FLICKR_API_KEY')
secret_key = os.getenv('FLICKR_SECRET_KEY')

# Check if API keys are loaded correctly
if not api_key or not secret_key:
    raise ValueError("API key and secret key must be set")

# hardcoded limit to the number of downloadable photos
DOWNLOAD_LIMIT = 3200 #max 3600 per hour
DOWNLOAD_LIMIT_BOUNDING_BOX = 47 #equal distribution among bounding boxes
download_count = 0
download_count_bounding_box = 0


# create directory to save images (exist_ok=True -> no error if directory already exists // from os.makedirs)
project_dir = Path(__file__).parent.parent
os.makedirs(os.path.join(project_dir, 'out'), exist_ok=True)
os.makedirs(Path.joinpath(Path.joinpath(project_dir, 'out'), 'downloaded_photos'), exist_ok=True)

# if there are already downloaded photos -> get list of all image names (to check for duplicates later)
image_filter = 'downloaded_photos/*.jpg'
image_names = {Path(x).stem for x in glob.glob(image_filter, root_dir="out/")}

if PRINT_DEBUG_INFO_PHOTO_NAMES:
    print(f"Already downloaded image names: {image_names}")

# read bounding boxes from csv (min_longitude,min_latitude,max_longitude,max_latitude)
with open(f'{project_dir}/output/bounding_boxes.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    bounding_boxes = []
    next(reader)  # Skip the header row
    for row in reader:
        bounding_box = ','.join(row)  # join the elements of the row into a single string
        bounding_boxes.append(bounding_box)
        if PRINT_DEBUG_INFO:
            print(f"Read bounding box: {bounding_box}")  # Debugging: Print each bounding box

# initialize the Flickr API
flickr_api = flickrapi.FlickrAPI(api_key, secret_key, format='parsed-json')

# iterate over each bounding box
for bounding_box in bounding_boxes:
    download_count_bounding_box = 0
    time.sleep(1)
    # search for the photos with specific tags inside the bounding box
    #search_result = flickr_api.photos.search(tags='desert pavement', per_page=60, extras='url_c,owner_name,geo', bbox=bounding_box)
    search_result = flickr_api.photos.search(text='desert pavement', per_page=60, extras='url_c,owner_name,geo', bbox=bounding_box) #- for 
    photos_list = search_result['photos']['photo']  # extract the list of photo metadata dictionaries for further processing

    if PRINT_DEBUG_INFO:
        print(f"Number of photos found in bounding box {bounding_box}: {len(photos_list)}")  # Debugging: print number of photos found inside bounding box

    # iterate through the list of photos: save metadata to a JSON file -> download images
    for photo in photos_list:
        if download_count_bounding_box >= DOWNLOAD_LIMIT_BOUNDING_BOX:
            break
        # check for duplicates 
        if photo['id'] in image_names:
            if PRINT_DEBUG_INFO:
                print(f"Skipping duplicate photo: {photo['id']}")
            continue
        
        # check if the photo is geotagged
        if 'latitude' not in photo or 'longitude' not in photo or photo['latitude'] == 0 or photo['longitude'] == 0:
            if PRINT_DEBUG_INFO:
                print(f"Skipping non-geotagged photo: {photo['id']}")
            continue

        # save photo metadata to a JSON file
        if PRINT_DEBUG_INFO:
            print(f"Processing photo: {photo['id']}")  # Debugging: check for photo metadata
        with open(f"{project_dir}/out/data.json", 'a', encoding='utf-8') as json_file:  # 'a' = append mode
            json.dump(photo, json_file, indent=4)
            json_file.write('\n')

        # == code for downloading images ==

        # Resizes the image to 800px on the longest side
        if 'url_c' in photo:  
            image_url = photo['url_c']
            # debugging: print image URL
            if PRINT_DEBUG_INFO:
                print(f"Downloading image: {image_url}")  
            # == download the image ==
            image_response = requests.get(image_url)  
            if image_response.status_code == 200:
                #  -- save the image as a jpg --
                with open(f"{project_dir}/out/downloaded_photos/{photo['id']}.jpg", 'wb') as image_file:  
                    image_file.write(image_response.content)
                download_count += 1
                download_count_bounding_box += 1
            else:
                #debugging: check for failed downloads
                if PRINT_DEBUG_INFO:
                    print(f"Failed to download image: {image_url}")  
        else:
            # debugging: print if 'url_c' tag is missing // not available for all photos
            if PRINT_DEBUG_INFO:
                print("No 'url_c' field in photo metadata")  

        # avoid rate limiting
        time.sleep(0.5)

    if PRINT_DEBUG_INFO:
        print(f"Number of photos downloaded: {download_count}")  # debugging: print download count

    # break the outer loop if the download limit is reached
    if download_count >= DOWNLOAD_LIMIT:
        break

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
DOWNLOAD_LIMIT = 10 #max 3600 per hour
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

bounding_boxes = [
'-108.99999999999999,43.99999999493054,-107.5,44.99999999531906',
'-119.5,38.49999999242639,-118.00000000000001,40.49999999339933',
'73.99999999999999,37.99999999217516,75.0,38.999999992674816',
'49.99999999999999,36.999999991665824,76.49999999999999,47.4999999961854',
'75.0,35.99999999115037,113.5,48.49999999648924',
'53.49999999999999,35.49999999089155,56.5,36.499999991408615',
'73.5,35.49999999089155,74.5,36.499999991408615',
'-118.00000000000001,34.99999999063272,-113.5,38.49999999242639',
'3.4999999999999996,34.499999990374306,4.499999999999999,35.49999999089155',
'7.999999999999998,34.499999990374306,8.999999999999998,34.99999999063272',
'38.0,34.499999990374306,38.5,35.49999999089155',
'1.9999999999999996,33.49999998986119,3.4999999999999996,34.499999990374306',
'36.49999999999999,32.49999998935683,39.0,34.499999990374306',
'78.99999999999999,32.49999998935683,81.5,33.999999990116976',
'-5.0,31.49999998886598,0.9999999999999998,33.999999990116976',
'59.00000000000001,31.49999998886598,60.5,31.999999989109405',
'-104.0,30.999999988627234,-103.0,31.999999989109405',
'-106.49999999999999,30.49999998839376,-105.00000000000001,32.49999998935683',
'35.99999999999999,30.49999998839376,36.49999999999999,31.999999989109405',
'51.5,30.49999998839376,57.0,33.49999998986119',
'-107.99999999999999,29.999999988166167,-106.99999999999999,30.999999988627234',
'-106.99999999999999,29.999999988166167,-106.0,31.49999998886598',
'-105.5,28.99999998773135,-103.5,30.999999988627234',
'59.99999999999999,28.49999998752537,61.0,30.49999998839376',
'66.0,28.49999998752537,67.0,28.99999998773135',
'-14.500000000000002,27.99999998732793,-13.499999999999998,28.99999998773135',
'-15.499999999999996,27.499999987139617,-14.999999999999998,28.49999998752537',
'51.5,27.499999987139617,52.50000000000001,27.99999998732793',
'-109.50000000000001,24.999999986357583,-108.99999999999999,25.99999998663604',
'-104.49999999999999,24.999999986357583,-100.99999999999999,29.499999987945124',
'-102.49999999999999,23.999999986130508,-101.5,24.999999986357583',
'-117.0,22.49999998589583,-109.50000000000001,36.499999991408615',
'43.0,15.499999986796261,44.49999999999999,17.499999986177638',
'39.49999999999999,14.999999986997757,40.49999999999999,15.999999986613501',
'53.0,11.999999988594144,54.49999999999999,12.999999987989447',
'-70.5,11.499999988922841,-69.5,12.499999988282951',
'-17.499999999999996,2.9999999966793265,75.5,35.99999999115037',
'34.99999999999999,2.499999997224261,36.49999999999999,4.499999995081567',
'39.0,0.4999999994411112,41.0,1.9999999977737652',
'39.0,-0.4999999994411197,40.0,0.0',
'-81.5,-9.499999990403948,-78.0,-3.9999999956071406',
'-78.0,-11.499999988922845,-77.5,-10.499999989630966',
'-77.5,-11.499999988922845,-77.0,-10.499999989630966',
'-77.5,-12.499999988282944,-77.0,-11.499999988922845',
'-77.0,-12.499999988282944,-76.49999999999999,-11.499999988922845',
'-76.0,-13.999999987456722,-75.5,-12.999999987989431',
'-76.49999999999999,-15.499999986796267,-75.0,-12.999999987989431',
'-72.99999999999999,-16.999999986304243,-71.99999999999999,-16.499999986449517',
'-75.0,-17.999999986069582,-69.99999999999999,-14.499999987217967',
'11.5,-17.999999986069582,13.499999999999998,-11.99999998859415',
'-71.5,-18.499999985979976,-69.99999999999999,-17.49999998617763',
'11.5,-20.499999985801352,14.500000000000002,-16.999999986304243',
'-68.5,-21.499999985815894,-66.0,-19.4999999858552',
'29.000000000000004,-22.499999985895805,29.999999999999996,-21.999999985847925',
'23.0,-22.999999985959228,25.499999999999996,-19.99999998581951',
'13.0,-30.499999988393743,24.5,-17.49999998617763',
'-71.99999999999999,-30.999999988627227,-68.0,-17.999999986069582',
'14.500000000000002,-31.499999988865998,18.499999999999996,-24.49999998623733',
'127.00000000000001,-31.499999988865998,130.5,-30.999999988627227',
'133.0,-31.499999988865998,134.5,-30.999999988627227',
'125.00000000000001,-32.499999989356795,127.00000000000001,-31.499999988865998',
'136.0,-32.499999989356795,137.0,-31.999999989109426',
'-68.5,-32.999999989607616,-67.0,-31.499999988865998',
'113.0,-32.999999989607616,143.99999999999997,-19.4999999858552',
'-69.5,-33.4999999898612,-67.0,-26.999999986961164',
'19.5,-33.4999999898612,24.999999999999996,-30.499999988393743',
'139.5,-33.99999999011698,141.0,-31.999999989109426',
'-65.5,-42.999999994519044,-63.50000000000001,-41.99999999408594'
]

# # list of bounding boxes (min_longitude,min_latitude,max_longitude,max_latitude)
# with open('output/bounding_boxes.csv', newline='') as csvfile:
#     reader = csv.reader(csvfile, delimiter=',')
#     bounding_boxes = []
#     next(reader)  # Skip the header row
#     for row in reader:
#         bounding_boxes.append(row)

# initialize the Flickr API
flickr_api = flickrapi.FlickrAPI(api_key, secret_key, format='parsed-json')

# iterate over each bounding box
for bounding_box in bounding_boxes:
    download_count_bounding_box = 0
    time.sleep(1)
    # search for the photos with specific tags inside the bounding box
    search_result = flickr_api.photos.search(tags='desert', per_page=60, extras='url_c,owner_name,geo', bbox=bounding_box)
    #search_result = flickr_api.photos.search(text='desert pavement', per_page=60, extras='url_c,owner_name,geo', bbox=bounding_box) #- for 
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
        with open(f"{project_dir}/out/'data.json", 'a', encoding='utf-8') as json_file:  # 'a' = append mode
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

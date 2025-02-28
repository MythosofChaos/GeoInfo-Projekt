import geopandas as gpd
import pandas as pd
from shapely.geometry import box
import os
import json
from pathlib import Path
import folium

def load_multiple_json(file_path):
    """
    Reads a file containing multiple concatenated JSON objects and returns a list of JSON objects.
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    decoder = json.JSONDecoder()
    pos = 0
    objs = []
    while pos < len(content):
        # skip whitespaces between JSON objects
        content_strip = content[pos:].lstrip()
        if not content_strip:
            break
        try:
            obj, idx = decoder.raw_decode(content_strip)
            objs.append(obj)
            # advance pos by the amount of whitespace stripped plus the length of the decoded object
            pos += len(content[pos:]) - len(content_strip) + idx
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            break
    return objs

image_path = 'out/annotated_desert_pavements'
output_csv_path = os.path.join('output', "bounding_boxes.csv")
json_path = os.path.join('out', "data.json")
output_html_path = os.path.join('out', "map.html")

bounding_boxes_df = pd.read_csv(output_csv_path) # Load bounding boxes from CSV
print("CSV columns:", bounding_boxes_df.columns.tolist())

json_data = load_multiple_json(json_path)

# create a dictionary to map image IDs to their coordinates
image_coords = {item['id']: (float(item['latitude']), float(item['longitude'])) for item in json_data}

# check if the CSV has the expected bounding box columns
expected_columns = {'min_longitude', 'min_latitude', 'max_longitude', 'max_latitude'}
if expected_columns.issubset(bounding_boxes_df.columns):
    # calculate map center from the bounding boxes
    center_lat = bounding_boxes_df[['min_latitude', 'max_latitude']].mean().mean()
    center_lon = bounding_boxes_df[['min_longitude', 'max_longitude']].mean().mean()
else:
    # Fallback: use average of JSON image coordinates if bounding box columns are missing
    if image_coords:
        center_lat = sum(coord[0] for coord in image_coords.values()) / len(image_coords)
        center_lon = sum(coord[1] for coord in image_coords.values()) / len(image_coords)
    else:
        center_lat, center_lon = 0, 0
    print("CSV file does not contain the expected bounding box columns. Using JSON coordinates for centering.")

m = folium.Map(location=[center_lat, center_lon], zoom_start=3) # create folium map

show_number = False  # change to True to show the image ID instead of a dot

# add markers for images (ASSUMING(!) the image filename's last part is the image id)
for image_filename in os.listdir(image_path):
    if image_filename.endswith(".jpg") or image_filename.endswith(".png"):
        # extract the image ID from the filename (assumed to be the last part before the extension)
        image_id = image_filename.split('_')[-1].split('.')[0]
        if image_id in image_coords:
            lat, lon = image_coords[image_id]
            if show_number:
                icon = folium.DivIcon(html=f'<div style="font-size: 12pt; color: red;">{image_id}</div>')
            else:
                icon = folium.Icon(color='blue', icon='info-sign', prefix='fa')
            folium.Marker(
                location=[lat, lon],
                popup=image_filename,
                icon=icon
            ).add_to(m)

# draw bounding boxes on the map
if expected_columns.issubset(bounding_boxes_df.columns):
    for _, row in bounding_boxes_df.iterrows():
        # create a bounding box polygon using the CSV columns
        bbox = box(row['min_longitude'], row['min_latitude'], row['max_longitude'], row['max_latitude'])
        folium.GeoJson(bbox, name=row.get('image_filename', 'bbox')).add_to(m)
        # calculate the center of the bounding box
        center_box_lat = (row['min_latitude'] + row['max_latitude']) / 2
        center_box_lon = (row['min_longitude'] + row['max_longitude']) / 2
        folium.Marker(
            location=[center_box_lat, center_box_lon],
            popup=row.get('image_filename', ''),
            icon=folium.DivIcon(html='<div style="font-size: 12pt; color: red;"> </div>')
        ).add_to(m)
else:
    print("Skipping drawing bounding boxes due to missing columns.")

# save as HTML
m.save(output_html_path)
print(f"Map saved to {output_html_path}")
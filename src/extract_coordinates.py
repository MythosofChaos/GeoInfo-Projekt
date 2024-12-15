import geopandas as gpd
import pandas as pd
from shapely.geometry import box
import os
from pathlib import Path
#import folium
#https://pypi.org/project/flickrapi/
#https://geopandas.org/en/stable/getting_started/install.html

project_dir = Path(__file__).parent.parent
shapefile_path = os.path.join(project_dir, "in", "1976-2000.shp")
shapefile = gpd.read_file(shapefile_path)

print(f"Current CRS: {shapefile.crs}") # current Coordinate Reference System

# re-project to Web Mercator to convert lat/long -> degrees
if shapefile.crs.is_geographic: # is.geographic checks if coodinates are in lat/long
    projected_shapefile = shapefile.to_crs({'proj':'cea'})  # 3857 = Web Mercator
else:
    print("shapefile is already projected --> projected_shapefile = shapefile")
    projected_shapefile = shapefile

print(projected_shapefile.crs)
print("area: " + str(max(projected_shapefile['geometry'].area / 10 ** 6)) + " km²")
"""
# filter for specific climate types
filtered_df = projected_shapefile[projected_shapefile['climate'].isin(["BWh Arid-Desert-Hot", "BWk Arid-Desert-Cold"])]

# Debugging: Print the number of rows after filtering by climate type
#print(f"Number of rows after filtering by climate type: {len(filtered_df)}")

# Identify and print invalid geometries
invalid_geometries = filtered_df[~filtered_df.is_valid]
#print("Invalid geometries:")
#print(invalid_geometries)

# fixes minor topological errors, helps with north african & chinese bbox
filtered_df['geometry'] = filtered_df['geometry'].buffer(0)

# is_valid checks for valid geometries
filtered_df = filtered_df[filtered_df.is_valid]

# Debugging: Print the number of rows after ensuring valid geometries
#print(f"Number of rows after ensuring valid geometries: {len(filtered_df)}")

# calculate areas in km^2 
filtered_df['area_km2'] = filtered_df.geometry.area / 1e6  # leftshift by 6 to convert to km^2
# Debugging: Print the areas to check if they are calculated correctly
#print(filtered_df[['climate', 'area_km2']])

filtered_df = filtered_df[(filtered_df['area_km2'] >= 5000)] # filter by size

# Debugging: Print the number of rows after filtering by area
#print(f"Number of rows after filtering by area: {len(filtered_df)}")

# re-project the filtered geometries to WGS84 to project in the Folium map
filtered_df = filtered_df.to_crs(epsg=4326)

# create dataframe to store bounding box values
bounding_boxes = []

for idx, row in filtered_df.iterrows():
    bbox = row.geometry.bounds  # Get bounding box as (minx, miny, maxx, maxy)
    bounding_boxes.append({
        "xmin": bbox[0],
        "ymin": bbox[1],
        "xmax": bbox[2],
        "ymax": bbox[3]
    })

# convert to pandas DataFrame
bounding_boxes_df = pd.DataFrame(bounding_boxes) 

# Debugging: Print the DataFrame with geographic coordinates
#print(bounding_boxes_df)

# save the bounding boxes to a CSV file in "output" subdir
output_dir = os.path.join(os.getcwd(), "output")
os.makedirs(output_dir, exist_ok=True)
output_csv_path = os.path.join(output_dir, "bounding_boxes.csv")
bounding_boxes_df.to_csv(output_csv_path, index=False)
"""
"""
# create a Folium map centered on the averaged bbox coordinates
center_lat = bounding_boxes_df[['ymin', 'ymax']].mean().mean()
center_lon = bounding_boxes_df[['xmin', 'xmax']].mean().mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=3)

# draw bounding boxes as rectangles on the map
for bbox in bounding_boxes_df.itertuples():
    rectangle = [
        [bbox.ymin, bbox.xmin],  # bottom-left
        [bbox.ymax, bbox.xmax]   # top-right
    ]
    folium.Rectangle(rectangle, color="red", fill=True, fill_opacity=0.5).add_to(m)

# save map as html file in "output" subdir
output_html_path = os.path.join(output_dir, "bounding_boxes_map.html")
m.save(output_html_path)
"""
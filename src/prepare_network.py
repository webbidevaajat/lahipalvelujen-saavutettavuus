
import sys
import json
import geopandas as gpd
import numpy as np
import json
from shapely.ops import unary_union
import geopandas as gpd
from shapely.geometry import Point

# Set up config env -----

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

try:
  print("Use environment", sys.argv[1])
  config_env = config[sys.argv[1]]
except:
  print("No enviroment set. Using test enviroment ..")
  config_env = config["test"]

# Load data ----

print("Load network from {} ..".format(config_env["network"]))
network_gdf = gpd.read_file(config_env["network"], engine = "pyogrio")
network_gdf = network_gdf.to_crs(config["crs"])

# Operations ----

n = network_gdf.geometry.unary_union
lines = list(n.geoms)
points = list()
for line in lines:
    points.append(line.coords[0])
    points.append(line.coords[-1])
points = set(points)
points = [Point(c) for c in points]

points = gpd.GeoDataFrame({"geometry": points}, geometry="geometry", crs=config["crs"]) 
lines = gpd.GeoDataFrame({"geometry": lines}, geometry="geometry", crs=config["crs"]) 

# Remove isolated lines ----

line_overlaps = lines.sjoin(lines, predicate="intersects", lsuffix="")
line_overlaps = line_overlaps.loc[line_overlaps.index != line_overlaps.index_right]
overlaps_ids = np.unique(line_overlaps.index)
lines = lines.iloc[overlaps_ids].reset_index(drop=True)

# Set ids ----

lines["id"] = lines.index + 1
points["id"] = points.index + 1

# Get points and lines ----

start_points = list()
last_points = list()
for index, row in lines.iterrows():
    start_points.append(Point(row['geometry'].coords[0]))
    last_points.append(Point(row['geometry'].coords[-1]))

lines_start = gpd.GeoDataFrame({"geometry": start_points}, geometry="geometry", crs=config["crs"]) 
lines_start["id"] = lines_start.index + 1

lines_end = gpd.GeoDataFrame({"geometry": last_points}, geometry="geometry", crs=config["crs"]) 
lines_end["id"] = lines_end.index + 1

points.geometry = points.centroid.buffer(0.1)

lines_start = lines_start.sjoin(points, predicate='within', lsuffix='line', rsuffix='start')
lines_start = lines_start[["id_line", "id_start"]]

lines_end = lines_end.sjoin(points, predicate='within', lsuffix='line', rsuffix='end')
lines_end = lines_end[["id_line", "id_end"]]

points.geometry = points.centroid

lines = lines.merge(lines_start, left_on="id", right_on="id_line", how='left')
lines = lines.merge(lines_end, left_on="id", right_on="id_line", how='left')

keep_ids = lines.id_start.tolist() + lines.id_end.tolist()
points = points[points.id.isin(keep_ids)]

points["id"] = points["id"].astype("int")
lines["id"] = lines["id"].astype("int")
lines["id_end"] = lines["id_end"].astype("int")
lines["id_start"] = lines["id_start"].astype("int")

# Save to file ----

fpath_points = "results/points.gpkg"
print("Save to {} ..".format(fpath_points))
points.to_file(fpath_points)

fpath_lines = "results/lines.gpkg"
print("Save to {} ..".format(fpath_lines))
lines.to_file("results/lines.gpkg")

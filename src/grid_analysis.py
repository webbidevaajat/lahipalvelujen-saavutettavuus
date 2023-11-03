
import sys
import yaml
import geopandas as gpd
import matplotlib.pyplot as plt
from datatypes.origin import Origin
from datatypes.destination import Destination
from parameters.parameters import plot_map
import config

# Prepare data -----

# Open yaml config file
config = yaml.safe_load(open("config.yml"))

# Read files

try:
  print("Use environment", sys.argv[1])
  env = sys.argv[1]
except:
  print("No enviroment set. Using test enviroment.")
  env = "test"

grid = gpd.read_file(config[env]["origins"], engine = "pyogrio")
network = gpd.read_file(config[env]["network"], engine = "pyogrio")
schools = gpd.read_file(config[env]["services"]["school"], engine = "pyogrio")
kindergartens = gpd.read_file(config[env]["services"]["kindergarten"], engine = "pyogrio")
restaurants = gpd.read_file(config[env]["services"]["restaurant"], engine = "pyogrio")

# Transform to local coordinates
CRS = 'EPSG:3879'
grid = grid.to_crs(CRS)
network = network.to_crs(CRS)
schools = schools.to_crs(CRS)
kindergartens = kindergartens.to_crs(CRS)
restaurants = restaurants.to_crs(CRS)

# Add id to spatial data
grid["id"] = grid.index + 1
schools["id"] = schools.index + 1
kindergartens["id"] = kindergartens.index + 1
restaurants["id"] = restaurants.index + 1

# Create objects -----

# Create destination objects
destinations = []
for index, row in schools.iterrows():
    destinations.append(Destination(id = row["id"], geom = row["geometry"], 
                                    category = "school", provider = "goverment"))

for index, row in kindergartens.iterrows():
    destinations.append(Destination(id = row["id"], geom = row["geometry"], 
                                    category = "kindergarten", provider = "goverment"))

for index, row in restaurants.iterrows():
    destinations.append(Destination(id = row["id"], geom = row["geometry"], 
                                    category = "restaurant", provider = "private"))

# Create origin objects
origins = []
for index, row in grid.iterrows():
    origins.append(
        Origin(
            id = row["id"], 
            geom = row["geometry"]
    ))

for o in origins:
    o.set_destinations(destinations, 3000)

# Perform analysis -----

res = gpd.GeoDataFrame({"geometry": [o.geom for o in origins],
                        "a_index1": [o.accessibility_index1() for o in origins],
                        "a_index2": [o.accessibility_index2(categories = list(["school", "kindergarten", "restaurant"])) for o in origins]
                        }, 
                        geometry="geometry", crs=CRS)

# Plot ----
plot_map(res, ["index_1", "index_2"], network, legend=True)

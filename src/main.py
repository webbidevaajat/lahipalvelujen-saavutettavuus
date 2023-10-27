
import yaml
import geopandas as gpd
from datatypes.origin import Origin
from datatypes.destination import Destination

# Prepare data -----

# Open yaml config file
config = yaml.safe_load(open("config.yml"))

# Read files
network = gpd.read_file(config["test"]["network"], engine = "pyogrio")
schools = gpd.read_file(config["test"]["services"]["school"], engine = "pyogrio")
kindergartens = gpd.read_file(config["test"]["services"]["kindergarten"], engine = "pyogrio")
restaurants = gpd.read_file(config["test"]["services"]["restaurant"], engine = "pyogrio")
zones = gpd.read_file(config["test"]["zones"], engine = "pyogrio")

# Tranform to local coordinates
network = network.to_crs('EPSG:3879')
schools = schools.to_crs('EPSG:3879')
zones = zones.to_crs('EPSG:3879')

# Add id to zones
zones["id"] = zones.index + 1
kindergartens["id"] = kindergartens.index + 1
schools["id"] = schools.index + 1
restaurants["id"] = restaurants.index + 1

# Create objects -----

# Create origin objects
origins = []
for index, row in zones.iterrows():
    origins.append(
        Origin(
            id = row["id"], 
            geom = row["geometry"],
    ))

# Create destination objects
destinations = []
for index, row in schools.iterrows():
    destinations.append(Destination(id = row["id"], geom = row["geometry"], category = "school"))

for index, row in kindergartens.iterrows():
    destinations.append(Destination(id = row["id"], geom = row["geometry"], category = "kindergarten"))

for index, row in restaurants.iterrows():
    destinations.append(Destination(id = row["id"], geom = row["geometry"], category = "restaurant"))

# Perform analysis -----

print(origins[1].get_distances(destinations))

print(destinations[1].usage)

print(destinations[-1].usage)

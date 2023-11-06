
import sys
import json
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from plotting import plot_grid
from datatypes.origin import Origin
from datatypes.destination import Destination

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

# Load admin regions ----

admin_regions = gpd.read_file(config_env["admin_regions"]["regions"], engine = "pyogrio")
admin_regions["admin_name"] = admin_regions[config_env["admin_regions"]["name_column"]]
admin_regions = admin_regions.to_crs(config["crs"])

# Create destination objects ----

print("Create destination objects ..")
destinations = list()
for service_type in config_env["services"]:
    gdf = gpd.read_file(config_env["services"][service_type], engine = "pyogrio")
    gdf = gdf.to_crs(config["crs"])
    gdf = gdf.sjoin(admin_regions, predicate='within')
    for index, row in gdf.iterrows():
      destinations.append(
         Destination(
            category = service_type, 
            geometry = row["geometry"],
            usage = config_env["usage"][service_type],
            provider = "goverment",
            admin_matters = config_env["admin_matters"][service_type],
            admin_region = row["admin_name"]
        )
    )

d_geom = gpd.GeoDataFrame({
            "geometry": [d.centroid for d in destinations], 
            "id": [d.id for d in destinations]}, 
            geometry="geometry", crs=config["crs"])

# Prepare origins -----

print("Create origin objects ..")
grid = gpd.read_file(config_env["origins"], engine = "pyogrio")
grid = grid.to_crs(config["crs"])
grid = grid.sjoin(admin_regions, predicate='within')

origins = []
for index, row in grid.iterrows():
    origins.append(
        Origin(
            geom = row["geometry"],
            admin_region = row["admin_name"]
    ))

print("Add destinations to origins ..")
for o in origins:
    # Only add if within buffer
    o.set_destinations(destinations)

# Network to calculate distances ----

#network = gpd.read_file(config["network"], engine = "pyogrio")
#network = network.to_crs(config["crs"])

# Perform analysis -----

print("Perform analysis ..")
res = gpd.GeoDataFrame({
   "geometry": [o.geom for o in origins],
   "a1_school": [o.accessibility_index1("school") for o in origins],
   "a1_restaurant": [o.accessibility_index1("restaurant") for o in origins],
   "a1_sports": [o.accessibility_index1("sports") for o in origins],
   "a1_health": [o.accessibility_index1("health") for o in origins],
   "a1_total": [o.accessibility_index1(config_env["services"]) for o in origins],
   "a2_school": [o.accessibility_index2("school") for o in origins],
   "a2_sports": [o.accessibility_index2("sports") for o in origins],
   "a2_total": [o.accessibility_index2(config_env["services"]) for o in origins]
   }, geometry="geometry", crs=config["crs"])

cols = res.columns[res.columns.str.startswith('a1')]
for column in cols:
    res[column] = 100 * res[column] / max(res[column])

# Plot ----

print("Plot analysis ..")
plot_grid(res, "a1_school", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Koulut")
plot_grid(res, "a1_restaurant", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Ravintolat")
plot_grid(res, "a1_sports", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Liikuntapaikat")
plot_grid(res, "a1_health", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Terveyspalvelut")
plot_grid(res, "a1_total", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Yhdistelmä")

plot_grid(res, "a2_sports", "viridis_r", label = "Lyhin matka-aika palveluun", title = "Liikuntapaikat")
plot_grid(res, "a2_school", "viridis_r", label = "Lyhin matka-aika palveluun", title = "Koulut")
plot_grid(res, "a2_total", "viridis_r", label = "Lyhin matka-aika palveluun", title = "Yhdistelmä")
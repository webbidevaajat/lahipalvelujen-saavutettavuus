
import sys
import json
import geopandas as gpd
import os
import numpy

from utils.plotting import plot_grid
from datatypes.origin import Origin
from datatypes.destination import Destination
from datatypes.network import Network

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

admin_regions = gpd.read_file(config_env["admin_regions"]["file"], engine = "pyogrio")
admin_regions["admin_name"] = admin_regions[config_env["admin_regions"]["column"]]
admin_regions = admin_regions.to_crs(config["crs"])

# Network to calculate distances ----

print("Create network object ..")
network_lines = gpd.read_file("results/lines.gpkg", engine = "pyogrio")
network_lines = network_lines.to_crs(config["crs"])
network_points = gpd.read_file("results/points.gpkg", engine = "pyogrio")
network_points = network_points.to_crs(config["crs"])
network = Network(network_lines, network_points)

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

# Prepare origins -----

print("Create origin objects ..")
grid = gpd.read_file(config_env["origins"]["file"], engine = "pyogrio")
grid = grid.to_crs(config["crs"])
grid = grid.sjoin(admin_regions, predicate='within')


origins = []
for index, row in grid.iterrows():
    origins.append(
        Origin(
            geom = row["geometry"],
            admin_region = row["admin_name"]
    ))

print("Search reachable destinations for origins ..")
for o in origins:
    o.set_destinations(destinations)

print("Add access nodes ..")
for d in destinations:
   d.set_access_node(network)

for o in origins:
    o.set_access_node(network)

print("Get distances nodes ..")
i = 0
for o in origins:
    o.set_distances(network)
    i += 1
    if i % 10 == 0:
       print(i, "/", len(origins))

# Perform analysis -----

print("Perform analysis ..")
res = gpd.GeoDataFrame({
   "geometry": [o.geom for o in origins],
   "a1_school": [o.accessibility_index1(["school"]) for o in origins],
   "a1_restaurant": [o.accessibility_index1(["restaurant"]) for o in origins],
   "a1_sports": [o.accessibility_index1(["sports"]) for o in origins],
   "a1_health": [o.accessibility_index1(["health"]) for o in origins],
   "a1_total": [o.accessibility_index1(list(config_env["services"])) for o in origins],
   "a2_school": [o.accessibility_index2(["school"]) for o in origins],
   "a2_sports": [o.accessibility_index2(["sports"]) for o in origins],
   "a2_total": [o.accessibility_index2(list(config_env["services"])) for o in origins]
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
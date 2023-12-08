
import sys
import json
import geopandas as gpd
import os
import numpy
import time
start_time = time.time()

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
  config_env = config["Vantaa"]

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
grid = grid.sjoin(admin_regions, predicate='intersects')
#grid = grid.iloc[1:100,]

origins = []
for index, row in grid.iterrows():
    origins.append(
        Origin(
            geom = row["geometry"],
            admin_region = row["admin_name"]
    ))

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
    if i % 100 == 0:
       print(i, "/", len(origins))

print("Search reachable destinations for origins ..")
for o in origins:
    o.set_destinations(destinations)

# Perform analysis -----

print("Perform analysis ..")
res = gpd.GeoDataFrame({
   "geometry": [o.geom for o in origins],

   # Accessibility index 1: Valinnanvara
   "a1_school_kolmasaste": [o.accessibility_index1(["school_kolmasaste"]) for o in origins],
   "a1_restaurant": [o.accessibility_index1(["restaurant"]) for o in origins],
   "a1_other_shops": [o.accessibility_index1(["grocery_store"]) for o in origins],
   "a1_public_transport_stops": [o.accessibility_index1(["public_transport_stops"]) for o in origins],
   "a1_sports": [o.accessibility_index1(["sports"]) for o in origins],
   "a1_total": [o.accessibility_index1(list(config_env["services"])) for o in origins],

   # Accessibility index 2: Lähin palvelu
   "a2_kindergarten": [o.accessibility_index1(["kindergarten"]) for o in origins],
   "a2_school_perusaste": [o.accessibility_index1(["school_perusaste"]) for o in origins],
   "a2_school_toinenaste": [o.accessibility_index1(["school_toinenaste"]) for o in origins],
   "a2_groceries": [o.accessibility_index1(["grocery_store"]) for o in origins],
   "a2_health_public": [o.accessibility_index1(["health_public"]) for o in origins],
   "a2_health_private": [o.accessibility_index1(["health_private"]) for o in origins],
   "a2_total": [o.accessibility_index2(list(config_env["services"])) for o in origins]
   }, geometry="geometry", crs=config["crs"])

cols = res.columns[res.columns.str.startswith('a1')]
for column in cols:
    res[column] = 100 * res[column] / max(res[column])

# Plot ----

print("Plot analysis ..")
plot_grid(res, "a1_school_kolmasaste", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Koulut: Kolmasaste")
plot_grid(res, "a1_restaurant", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Ravintolat")
plot_grid(res, "a1_other_shops", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Muu kauppa​")
plot_grid(res, "a1_public_transport_stops", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Joukkoliikennepysäkit")
plot_grid(res, "a1_sports", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Liikuntapaikat")
plot_grid(res, "a1_total", "viridis", label = "Valintamahdollisuuksien indeksi", title = "Yhdistelmä")

plot_grid(res, "a2_kindergarten", "viridis", label = "Lyhin matka-aika palveluun", title = "Päivähoito")
plot_grid(res, "a2_school_perusaste", "viridis", label = "Lyhin matka-aika palveluun", title = "Koulut: Perusaste")
plot_grid(res, "a2_school_toinenaste", "viridis", label = "Lyhin matka-aika palveluun", title = "Koulut: Toinenaste")
plot_grid(res, "a2_health_public", "viridis", label = "Lyhin matka-aika palveluun", title = "Julkiset terveyspalvelut​")
plot_grid(res, "a2_health_private", "viridis", label = "Lyhin matka-aika palveluun", title = "Yksityiset terveyspalvelut​")
plot_grid(res, "a2_groceries", "viridis", label = "Lyhin matka-aika palveluun", title = "Päivittäistavara​")
plot_grid(res, "a2_total", "viridis_r", label = "Lyhin matka-aika palveluun", title = "Yhdistelmä")

print("Process finished --- %s seconds ---" % (time.time() - start_time))
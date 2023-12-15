
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
    gdf = gdf.sjoin(admin_regions, how="inner", predicate="intersects")
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

origins = []
for index, row in grid.iterrows():
    origins.append(
        Origin(
            geom = row["geometry"],
            admin_region = row["admin_name"]
    ))

print("Add destination access nodes ..")
i = 0
for d in destinations:
   d.set_access_node(network)
   i += 1
   if i % 1000 == 0:
      print(i, "/", len(destinations))

print("Add origin access nodes ..")
i = 0
for o in origins:
   o.set_access_node(network)
   i += 1
   if i % 1000 == 0:
      print(i, "/", len(origins))

print("Get distances nodes ..")
i = 0
for o in origins:
    o.set_distances(network)
    i += 1
    if i % 1000 == 0:
       print(i, "/", len(origins))

print("Search reachable destinations for origins ..")
for o in origins:
    o.set_destinations(destinations)

# Perform analysis -----

def rescale1(col):
   return 100 * (col - min(col)) / (max(col) - min(col))

def rescale2(col):
   return 100 * (col - max(col)) / (min(col) - max(col))

print("Perform analysis ..")
res = gpd.GeoDataFrame({"geometry": [o.geom for o in origins]}, geometry="geometry", crs=config["crs"])

a1 = ["school_kolmasaste", "restaurant", "other_shops", "public_transport_stops", "sports", "culture"]
for service_type in a1:
    res[service_type] = [o.aindex_choice(service_type) for o in origins]
    res["s_" + service_type] = rescale1(res[service_type])

a2 = ["school_perusaste", "school_toinenaste", "health_public", "health_private"]
for service_type in a2:
    res[service_type] = [o.aindex_closest(service_type) for o in origins]
    res["s_" + service_type] = rescale2(res[service_type])

a3 = ["kindergarten", "grocery_store"]
for service_type in a3:
    res[service_type] = [o.aindex_closest(service_type, 3) for o in origins]
    res["s_" + service_type] = rescale2(res[service_type])

res["total_index"] = 0
for service_type in config_env["services"]:
   res["total_index"] += res["s_" + service_type] * config_env["usage"][service_type]

# Plot ----

# Get category destinations geometry
def get_geom(service_type):
    gdf = gpd.read_file(config_env["services"][service_type], engine = "pyogrio")
    gdf = gdf.to_crs(config["crs"])
    return gdf.geometry

print("Plot analysis ..")
plot_grid(res, "s_school_kolmasaste", get_geom("school_kolmasaste"), "viridis", label = "Valintaindeksi", title = "Koulut: Kolmas aste")
plot_grid(res, "s_restaurant", get_geom("restaurant"), "viridis", label = "Valintaindeksi", title = "Ravintolat")
plot_grid(res, "s_other_shops", get_geom("other_shops"), "viridis", label = "Valintaindeksi", title = "Muu kauppa​")
plot_grid(res, "s_public_transport_stops", get_geom("public_transport_stops"), "viridis", label = "Valintaindeksi", title = "Joukkoliikennepysäkit")
plot_grid(res, "s_sports", get_geom("sports"), "viridis", label = "Valintaindeksi", title = "Liikuntapaikat")
plot_grid(res, "s_culture", get_geom("culture"), "viridis", label = "Valintaindeksi", title = "Virkistys- tai kulttuurikohde")

plot_grid(res, "kindergarten", get_geom("kindergarten"), "viridis_r", label = "Etäisyys kolmeen palveluun", title = "Päivähoito")
plot_grid(res, "school_perusaste", get_geom("school_perusaste"), "viridis_r", label = "Etäisyys palveluun", title = "Koulut: Perusaste")
plot_grid(res, "school_toinenaste", get_geom("school_toinenaste"), "viridis_r", label = "Etäisyys palveluun", title = "Koulut: Toinen aste")
plot_grid(res, "health_public", get_geom("health_public"), "viridis_r", label = "Etäisyys palveluun", title = "Julkiset terveyspalvelut​")
plot_grid(res, "health_private", get_geom("health_private"), "viridis_r", label = "Etäisyys palveluun", title = "Yksityiset terveyspalvelut​")
plot_grid(res, "grocery_store", get_geom("grocery_store"), "viridis_r", label = "Etäisyys kolmeen palveluun", title = "Päivittäistavara​")

plot_grid(res, "total_index", None, "viridis", label = "Yhdistelmäindeksi", title = "Yhdistelmäindeksi")

print("Process finished --- %s seconds ---" % round(time.time() - start_time))

res.to_file("results/results.gpkg")

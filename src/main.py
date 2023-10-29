
import yaml
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
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
CRS = 'EPSG:3879'
network = network.to_crs(CRS)
schools = schools.to_crs(CRS)
zones = zones.to_crs(CRS)

# Add id to zones
zones["id"] = zones.index + 1
kindergartens["id"] = kindergartens.index + 1
schools["id"] = schools.index + 1
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
for index, row in zones.iterrows():
    origins.append(
        Origin(
            id = row["id"], 
            geom = row["geometry"]
    ))

for o in origins:
    o.set_destinations(destinations, 3000)

# Perform analysis -----

res = gpd.GeoDataFrame({"geometry": [o.geom for o in origins],
                        "access_prob": [o.access_prob() for o in origins]}, 
                        geometry="geometry", crs=CRS)


# Plot ----

# Create one subplot. Control figure size in here.
fig, ax = plt.subplots(figsize=(12, 8))

# Visualize the travel times into 9 classes using "Quantiles" classification scheme
res.plot(
    ax=ax,
    column="access_prob", 
    linewidth=0.03,
    cmap="viridis",
    alpha=0.9,
    legend=True,
    legend_kwds={"label": "Accessibility Index", "orientation": "vertical"},
)

# Add roads on top of the grid
# (use ax parameter to define the map on top of which the second items are plotted)
network.plot(ax=ax, color="white", linewidth=0.1)

# Remove the empty white-space around the axes
ax.set_axis_off()
plt.tight_layout()

# Save the figure as png file with resolution of 300 dpi
outfp = "results/static_map.png"
plt.savefig(outfp, dpi=300)

plt.show()

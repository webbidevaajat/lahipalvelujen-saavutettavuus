
import sys
import yaml
import geopandas as gpd
import matplotlib.pyplot as plt
from datatypes.origin import Origin
from datatypes.destination import Destination

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

# Create one subplot. Control figure size in here.
fig, ax = plt.subplots(figsize=(12, 8))

# Visualize the travel times into 9 classes using "Quantiles" classification scheme
res.plot(
    ax=ax,
    column="a_index2", 
    linewidth=0.03,
    cmap="viridis_r",
    alpha=0.9,
    legend=True,
    legend_kwds={"label": "Accessibility Index2", "orientation": "vertical"},
)

# Add roads on top of the grid
# (use ax parameter to define the map on top of which the second items are plotted)
network.plot(ax=ax, color="white", linewidth=0.1)

# Remove the empty white-space around the axes
ax.set_axis_off()
plt.tight_layout()

# Save the figure as png file with resolution of 300 dpi
outfp = "results/a_index1.png"
plt.savefig(outfp, dpi=300)

plt.show()

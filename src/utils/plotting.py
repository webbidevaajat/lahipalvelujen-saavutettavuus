
import matplotlib.pyplot as plt
import geopandas as gpd
import json

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

config_map = config["basemap"]

def plot_grid(data, colname, cmap = "viridis", label = "Accessibility Index", title = ""):
    """
    Plot function for accessibility graphs.
    """
    
    print("Exported {} accessibility map ..".format(colname))

    # Create one subplot. Control figure size in here.
    fig, ax = plt.subplots(figsize=(12, 8))

    # Visualize the travel times into 9 classes using "Quantiles" classification scheme
    data.plot(
        ax=ax,
        column=colname, 
        linewidth=0.03,
        cmap=cmap,
        alpha=0.9,
        legend=True,
        legend_kwds={"label": label, "orientation": "vertical"},
    )

    # Add roads on top of the grid
    # (use ax parameter to define the map on top of which the second items are plotted)

    paths = gpd.read_file(config_map["paths"], engine = "pyogrio")
    paths = paths.to_crs(config["crs"])
    highway = gpd.read_file(config_map["roads"], engine = "pyogrio")
    highway = highway.to_crs(config["crs"])
    railways = gpd.read_file(config_map["railways"], engine = "pyogrio")
    railways = railways.to_crs(config["crs"])

    paths.plot(ax=ax, color="white", linewidth=0.1)
    highway.plot(ax=ax, color="white", linewidth=0.5)
    railways.plot(ax=ax, color="white", linestyle="-", linewidth=0.6)
    railways.plot(ax=ax, color="black", linestyle="--", linewidth=0.6)

    # Remove the empty white-space around the axes
    ax.set_axis_off()
    plt.title(title, fontdict = {'fontsize':15})
    plt.tight_layout()

    # Set axis bb
    xmin, ymin, xmax, ymax = data.total_bounds
    pad = 0.05  # add a padding around the geometry
    ax.set_xlim(xmin-pad, xmax+pad)
    ax.set_ylim(ymin-pad, ymax+pad)

    # Save the figure as png file with resolution of 300 dpi
    outfp = "results/" + colname + ".png"
    plt.savefig(outfp, dpi=300)

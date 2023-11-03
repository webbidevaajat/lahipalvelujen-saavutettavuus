import matplotlib.pyplot as plt
import geopandas as gpd

def plot_grid(config, data, colname, cmap = "viridis", label = "Accessibility Index", title = ""):
    """
    Plot function for accessibility graphs.
    """
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

    network = gpd.read_file(config["network"], engine = "pyogrio")
    network = network.to_crs(config["crs"])
    highway = gpd.read_file(config["basemap"]["roads"], engine = "pyogrio")
    highway = highway.to_crs(config["crs"])
    railways = gpd.read_file(config["basemap"]["railways"], engine = "pyogrio")
    railways = railways.to_crs(config["crs"])

    network.plot(ax=ax, color="white", linewidth=0.01)
    highway.plot(ax=ax, color="white", linewidth=0.2)
    railways.plot(ax=ax, color="white", linestyle="-", linewidth=0.3)
    railways.plot(ax=ax, color="black", linestyle="--", linewidth=0.3)

    # Remove the empty white-space around the axes
    ax.set_axis_off()
    plt.title(title)
    plt.tight_layout()

    # Set axis bb
    xmin, ymin, xmax, ymax = data.total_bounds
    pad = 0.05  # add a padding around the geometry
    ax.set_xlim(xmin-pad, xmax+pad)
    ax.set_ylim(ymin-pad, ymax+pad)

    # Save the figure as png file with resolution of 300 dpi
    outfp = "results/" + colname + ".png"
    plt.savefig(outfp, dpi=300)

    print("Successfully exported {} accessibility map.".format(colname))

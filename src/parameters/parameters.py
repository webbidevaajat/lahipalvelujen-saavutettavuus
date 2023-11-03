import matplotlib.pyplot as plt
import config

# plot function
def plot_map(res, indices: list, network, legend=True):
    """
    Plot function for accessibility graphs.

    Parameters
    ----------
    res: geoDataFrame
        origin grid containing all accessibility data
    indices: list(str)
        selected accessibility indices to be ploted
    network: geoDataFrame
        map base network
    legend: bool, default = True
        map legend
       
         
    """
    for index in indices:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        colname = config.accessibility_indices[index]["colname"]
        cmap = config.accessibility_indices[index]["cmap"]
        label = config.accessibility_indices[index]["label"]

        res.plot(
            ax=ax,
            column=colname, 
            linewidth=0.03,
            cmap=cmap,
            alpha=0.9,
            legend=legend,
            legend_kwds={"label": label, "orientation": "vertical"}
            )

        # Add roads on top of the grid
        # Use ax parameter to define the map on top of which the second items are plotted
        network.plot(ax=ax, color="white", linewidth=0.1)

        # Remove the empty white-space around the axes
        ax.set_axis_off()
        plt.tight_layout()

        # Save the figure as png file with resolution of 300 dpi
        outfp = "results/{}.png".format(colname)
        plt.savefig(outfp, dpi=300)
        plt.show()
        print("Successfully exported {} accessibility map.".format(index))
    
import json
import networkx as nx
from shapely.ops import unary_union
from itertools import compress
import numpy as np
import momepy
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from osgeo import ogr
from osgeo import osr
from utils.distance import haversine
from shapely.geometry import LineString, Point, MultiPoint
from shapely.ops import nearest_points, snap

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

class Network(object):
    def __init__(self, network):
        """
        Network to use in distance calculations.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        network : shapely.geometry.lines
            Geometries of network.
        """
        n = network.geometry
        n = unary_union(n)
        # geometries
        self.geoms = list(n.geoms)
        # graph
        self.graph = nx.Graph()
        
        i = 0
        coords = pd.Series(np.arange(len(self.geoms)))
        for line in self.geoms:
            for start_c, end_c in zip(list(line.coords),list(line.coords)[1:]):
                # start
                if start_c in set(coords.values):
                    start_id = coords[coords == start_c].index.values[0]
                else:
                    coords[i] = start_c
                    start_id = i
                    i += 1
                # end
                if end_c in set(coords.values):
                    end_id = coords[coords == end_c].index.values[0]
                else:
                    coords[i] = end_c
                    end_id = i
                    i += 1
            # add ids to graph
            self.graph.add_edge(start_id, end_id, dist = line.length) 
            if i % 100 == 0:
                print(i, len(self.geoms))
   
        self.points = gpd.GeoDataFrame({
            "id": coords.index,
            "geometry": [Point(c) for c in coords]
            }, 
            geometry="geometry", crs=config["crs"])    

    def get_distance(self, origin, destination):
        """
        Get distances from origin.
        
        Parameters
        ----------
        origin : datatypes.origin.Origin
            Origin to search distance into.
        """

        # Find the shortest path
        path = nx.shortest_path(self.graph, source=origin.access_node, target=destination.access_node, weight="dist")
        
        # Create a list of edges in the shortest path
        if len(path) > 1: 
            line = LineString(path)
            line_gdf = gpd.GeoDataFrame({"geometry": line}, geometry="geometry", crs=config["crs"], index=[0])
        orig_gdf = gpd.GeoDataFrame({"geometry": origin.centroid}, geometry="geometry", crs=config["crs"], index=[0])
        dest_gdf = gpd.GeoDataFrame({"geometry": destination.centroid}, geometry="geometry", crs=config["crs"], index=[0])
        self.plot_network(line, orig_gdf, dest_gdf)
        print(line.length)
        return(line.length)
    
    def get_dist_decay(self, origin, destination):
        b = -1
        return np.exp(b * self.get_distance(origin, destination) / 1000)
    
    def plot_network(self, line, orig, dest):
        fig, ax = plt.subplots(figsize=(18, 6))
        ax.set_title("Primal graph")
        ax.axis("off")
        
        orig.plot(ax=ax, marker='o', color='red', markersize=50)
        dest.plot(ax=ax, marker='o', color='red', markersize=50)
        nx.draw(self.graph, {n:[n[0], n[1]] for n in list(self.graph.nodes)}, ax=ax, node_size=1)
        line.plot(ax=ax, color="red")
        plt.show()

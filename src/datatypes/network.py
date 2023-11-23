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
from shapely.ops import nearest_points

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
        #p = n.boundary
        lines = list(n.geoms)
        points = list()
        for line in lines:
            points.append(line.coords[0])
            points.append(line.coords[-1])
        points = set(points)
        points = [Point(c) for c in points]
        #points = MultiPoint(points = points)
        #points = p.geoms
        # graph
        self.graph = nx.Graph()

        points = gpd.GeoDataFrame({"geometry": points}, geometry="geometry", crs=config["crs"]) 
        points["id"] = points.index + 1
        
        lines = gpd.GeoDataFrame({"geometry": lines}, geometry="geometry", crs=config["crs"]) 
        lines["id"] = lines.index + 1

        start_points = list()
        last_points = list()
        for index, row in lines.iterrows():
            start_points.append(Point(row['geometry'].coords[0]))
            last_points.append(Point(row['geometry'].coords[-1]))

        lines_start = gpd.GeoDataFrame({"geometry": start_points}, geometry="geometry", crs=config["crs"]) 
        lines_start["id"] = lines_start.index + 1

        lines_end = gpd.GeoDataFrame({"geometry": last_points}, geometry="geometry", crs=config["crs"]) 
        lines_end["id"] = lines_end.index + 1
        
        points.geometry = points.centroid.buffer(0.1)
        
        lines_start= lines_start.sjoin(points, predicate='within', lsuffix='line', rsuffix='start')
        lines_start = lines_start[["id_line", "id_start"]]

        lines_end = lines_end.sjoin(points, predicate='within', lsuffix='line', rsuffix='end')
        lines_end = lines_end[["id_line", "id_end"]]

        points.geometry = points.centroid

        lines = lines.merge(lines_start, left_on="id", right_on="id_line", how='left')
        lines = lines.merge(lines_end, left_on="id", right_on="id_line", how='left')

        for index, row in lines.iterrows():
            self.graph.add_edge(row["id_start"], row["id_end"], dist = row['geometry'].length)

        points["id"] = points["id"].astype("int")
        lines["id"] = lines["id"].astype("int")
        lines["id_end"] = lines["id_end"].astype("int")
        lines["id_start"] = lines["id_start"].astype("int")

        #points.to_file("results/points.gpkg")
        #lines.to_file("results/lines.gpkg")
        
        self.points = points
        self.lines = lines

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
        ps = list()
        for p in path:
            ps.append(self.points.loc[self.points["id"] == p]) 
        line = LineString([(p.x, p.y) for p in ps])
        line_gdf = gpd.GeoDataFrame({"geometry": line}, geometry="geometry", crs=config["crs"], index=[0])

        orig_gdf = gpd.GeoDataFrame({"geometry": origin.centroid}, geometry="geometry", crs=config["crs"], index=[0])
        dest_gdf = gpd.GeoDataFrame({"geometry": destination.centroid}, geometry="geometry", crs=config["crs"], index=[0])
        self.plot_network(line_gdf, orig_gdf, dest_gdf)
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
        line.plot(ax=ax, color="red")
        plt.show()

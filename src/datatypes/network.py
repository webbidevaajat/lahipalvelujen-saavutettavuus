import json
import networkx as nx
from shapely.ops import unary_union
import geopandas as gpd
from shapely.geometry import LineString, Point

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

class Network(object):
    def __init__(self, lines, points):
        """
        Network to use in distance calculations.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        network : shapely.geometry.lines
            Geometries of network.
        """
        # graph
        self.points = points
        self.graph = nx.Graph()
        for index, row in lines.iterrows():
            self.graph.add_edge(row["id_start"], row["id_end"], dist = row['geometry'].length)

    def get_distance(self, o, d):
        """
        Get distance from origin to destination.
        
        Parameters
        ----------
        origin : datatypes.origin.Origin
            Origin of path that has property access node.
        destination : datatypes.destination.Destination
            Destination of path that has property access node.
        """

        # Find the shortest path
        if o.access_node is None:
            return 9999999
        if d.access_node is None:
            return 9999999
        if o.access_node == d.access_node:
            return 0
        if not nx.has_path(self.graph, source=o.access_node, target=d.access_node):
            return 9999999
        else:
            return nx.shortest_path_length(self.graph, source=o.access_node, 
                                           target=d.access_node, weight="dist")
    
    def get_path(self, o, d):
        """
        Get line path and path distance from origin to destination.
        
        Parameters
        ----------
        origin : datatypes.origin.Origin
            Origin of path that has property access node.
        destination : datatypes.destination.Destination
            Destination of path that has property access node.
        """

        # Find the shortest path
        if o.access_node is None:
            return 9999999
        if d.access_node is None:
            return 9999999
        if o.access_node == d.access_node:
            return 0
        if not nx.has_path(self.graph, source=o.access_node, target=d.access_node):
            return 9999999

        path = nx.shortest_path_length(self.graph, source=o.access_node, 
                                       target=d.access_node, weight="dist")
        path_p = list()
        for p in path:
            path_p.append(self.points.loc[self.points["id"] == p, "geometry"].values[0]) 
        line = LineString(path_p)
        return line, line.length

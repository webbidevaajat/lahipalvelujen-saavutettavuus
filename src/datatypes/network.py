import json
import networkx as nx
from shapely.ops import unary_union
import geopandas as gpd
from shapely.geometry import LineString, Point

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
            return 9999999
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
            return 9999999
        if not nx.has_path(self.graph, source=o.access_node, target=d.access_node):
            return 9999999

        path = nx.shortest_path_length(self.graph, source=o.access_node, 
                                       target=d.access_node, weight="dist")
        path_p = list()
        for p in path:
            path_p.append(self.points.loc[self.points["id"] == p, "geometry"].values[0]) 
        line = LineString(path_p)
        return line, line.length

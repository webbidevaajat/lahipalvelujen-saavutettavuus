
import numpy as np
import networkx as nx
from osgeo import ogr
from osgeo import osr
from shapely.geometry import LineString, Point
import json
from src.utils.distance import haversine

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

class Destination(object):
    id_counter = 0
    def __init__(self, category, usage, provider, geometry, admin_matters, admin_region,
                 network, nodes, edges):
        """
        Origin point for which accessibility is calculted.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        geom : geopandas.geoseries.GeoSeries
            Geometry of origin zone or point.
        network : networkx.Graph
            Network used for routing
        nodes : NodeView
            Nodes connecting links
        edges : EdgeView
            Links between nodes
        """
        self.id = Destination.id_counter
        Destination.id_counter += 1
        self.category = category
        self.usage = usage
        self.admin_matters = admin_matters
        self.admin_region = admin_region
        self.provider = provider
        self.geometry = geometry
        self.centroid = geometry.centroid
        self.network = network
        self.nodes = nodes
        self.edges = edges
        self.crs = config["crs"]
    
    def get_distance(self, origin):
        """
        Get distances from origin.
        
        Parameters
        ----------
        origin : datatypes.origin.Origin
            Origin to search distance into.
        """
        # start and end
        p1 = self.centroid
        p2 = origin.centroid

        # get x and y coords
        orig_xy = (p1.y, p1.x)
        target_xy = (p2.y, p2.x)

        # find the nearest nodes in a graph to specified start and end points
        nn_start = None
        nn_end = None
        start_delta = float("inf")
        end_delta = float("inf")
        for n in self.nodes ():
            s_dist = haversine(orig_xy, n)
            e_dist = haversine(target_xy, n)
        if s_dist < start_delta :
                nn_start = n
                start_delta = s_dist
        if e_dist < end_delta :
                nn_end = n
                end_delta = e_dist
                
        path = nx.shortest_path (self.network, source= nn_start, 
                                 target= nn_end, weight=" dist ")
        # Build geometry type: multi-line
        multiline = ogr.Geometry(ogr.wkbMultiLineString)
        # Build geometry type: line
        line = ogr.Geometry(ogr.wkbLineString)

        for point in path:
            line.AddPoint(point[0], point[1])

        # Set the geometry's spatial reference
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(3879)

        line.AssignSpatialReference(srs)

        # Add line to multi-line
        multiline.AddGeometry(line)

        return(line.Length())

    def get_dist_decay(self, origin):
        b = -1
        return np.exp(b * self.get_distance(origin) / 1000)

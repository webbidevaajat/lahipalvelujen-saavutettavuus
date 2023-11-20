
import json
from shapely.geometry import Point
from shapely.ops import nearest_points

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

class Destination(object):
    id_counter = 0
    def __init__(self, category, usage, provider, geometry, admin_matters, admin_region):
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
        self.crs = config["crs"]

    def set_access_node(self, network):
        # Find the nearest nodes in a graph
        nearest_geoms  = nearest_points(self.centroid, network.points.geometry)
        nearest_data = network.points.loc[network.points.geometry == nearest_geoms[1]]
        nearest_value = nearest_data["id"].get_values()[0]
        self.access_node = nearest_value

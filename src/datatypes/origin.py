import json
import numpy
from shapely.ops import nearest_points

# Open yaml config file
with open('config.json') as f:
   config = json.load(f)

class Origin(object):
    id_counter = 0
    def __init__(self, geom, admin_region):
        """
        Origin point for which accessibility is calculted.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        geom : shapely.geometry
            Geometry of origin zone or point.
        """
        self.id = Origin.id_counter
        Origin.id_counter += 1
        self.geom = geom
        self.centroid = geom.centroid
        self.name = None
        self.admin_region = admin_region
        self.dest_radius = config["destination_radius"]

    def set_access_node(self, network):
        # Find the nearest nodes in a graph
        mask = network.points.within(self.centroid.buffer(config["access_radius"]))
        if any(mask):
            nearby_points = network.points.loc[mask]
            nearest_geoms  = nearest_points(self.centroid, nearby_points.geometry.unary_union)
            nearest_data = nearby_points.loc[nearby_points.geometry == nearest_geoms[1]]
            nearest_value = nearest_data["id"].values[0]
            self.access_node = nearest_value
        else:
            self.access_node = None

    def set_distances(self, network):
        self.distances = network.get_origin_dist(self, self.dest_radius)

    def set_destinations(self, destinations):
        """
        Keep only destination within buffer
        Check if destination has admin restriction and filter with that
        """
        self.destinations = list()
        for d in destinations:
            if d.access_node in self.distances.keys():
                if d.admin_matters:
                    if d.admin_region == self.admin_region:
                        self.destinations.append(d)
                else: 
                    self.destinations.append(d)

    def get_shortest_dist(self, category):
        distances = list()
        for d in self.destinations:
            if d.category == category:
                dist = self.distances[d.access_node]
                distances.append(dist)           
        if distances: 
            # return shortest time, mins
            return (min(distances) / 1000 / (5 / 60))
        else:
            return (self.dest_radius / 1000 / (5 / 60)) 

    def aindex_decay(self, categories):
        """
        Accessibility Index calculation option 1.
        AIndex is based on usage rate of service type and distance decay to location.

        """
        idx = list()
        # calculate over all destinations within origin radius
        if isinstance(categories, list):
            for d in self.destinations:
                if d.category in categories:
                    decay = numpy.exp(-0.7 * (self.distances[d.access_node] / 1000) + 0.35)
                    idx.append(decay * d.usage)
        else:
            raise TypeError("Categories argument is not a list.")
        # return sum for origin
        return sum(idx)
    
    def aindex_closest(self, categories):
        """
        Accessibility Index calculation option 2.
        AIndex is calculated as mean time for closest service in each category.
        
        """
        idx = list()
        # calculate over all destinations within origin radius
        if isinstance(categories, list):
            for category in categories:
                idx.append(self.get_shortest_dist(category))
        else:
            raise TypeError("Categories argument is not a list.")
        # Return mean of min travel times
        if idx:
            return (sum(idx) / len(idx))
        else:
            return (self.dest_radius / 1000 / (5 / 60)) 
    
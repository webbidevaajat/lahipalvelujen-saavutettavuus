import json
from shapely.geometry import Point
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
        self.radius = config["radius"]

    def set_destinations(self, destinations):
        """
        Keep only destination within buffer
        Check if destination has admin restriction and filter with that
        """
        self.destinations = list()
        buffer = self.centroid.buffer(self.radius)
        for d in destinations:
            if d.centroid.within(buffer):
                if d.admin_matters:
                    if d.admin_region == self.admin_region:
                        self.destinations.append(d)
                else: 
                    self.destinations.append(d)

    def set_access_node(self, network):
        # Find the nearest nodes in a graph
        nearest_geoms  = nearest_points(self.centroid, network.points.geometry)
        nearest_data = network.points.loc[network.points.geometry == nearest_geoms[1]]
        nearest_value = nearest_data["id"].get_values()[0]
        self.access_node = nearest_value

    def set_distances(self, network):
        self.distances = list()
        for d in self.destinations:
            self.distances.append(network.get_distance(self, d))

    def get_shortest_dist(self, category, network):
        distances = list()
        for i, d in enumerate(self.destinations):
            if d.category == category:
                dist = self.distances[i]
                distances.append(dist)                
        if distances: 
            # return shortest time, mins
            return (min(distances) / 1000 / (5 / 60))
        else:
            return (self.radius / 1000 / (5 / 60)) # buffer radius

    def accessibility_index1(self, categories, network):
        """
        Accessibility Index calculation option 1.
        AIndex is based on usage rate of service type and distance decay to location.

        """
        idx = list()
        # calculate over all destinations within origin radius
        if isinstance(categories, list):
            for i, d in enumerate(self.destinations):
                if d.category in categories:
                    dist = self.distances[i]
                    idx.append(dist * d.usage)
        else:
            raise TypeError("Categories argument is not a list.")
        # return sum for origin
        return sum(idx)
    
    def accessibility_index2(self, categories, network):
        """
        Accessibility Index calculation option 2.
        AIndex is calculated as mean time for closest service in each category.
        
        """
        idx = list()
        # calculate over all destinations within origin radius
        if isinstance(categories, list):
            for category in categories:
                idx.append(self.get_shortest_dist(category, network))
        else:
            raise TypeError("Categories argument is not a list.")
        # Return mean of min travel times
        if idx:
            return (sum(idx) / len(idx))
        else:
            return (self.radius / 1000 / (5 / 60)) # buffer radius
    
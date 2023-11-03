
from itertools import compress

class Origin(object):
    def __init__(self, id, geom):
        """
        Origin point for which accessibility is calculted.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        geom : shapely.geometry
            Geometry of origin zone or point.
        """
        self.id = id
        self.geom = geom
        self.centroid = geom.centroid
        self.name = None
        self.admin_region = "Vantaa"

    def set_destinations(self, destinations, radius, admin_boundary = False):
        # Keep only destination within buffer
        self.buffer = self.centroid.buffer(radius)
        mask = [d.centroid.within(self.buffer) for d in destinations]
        self.destinations = list(compress(destinations, mask))
        if admin_boundary:
            mask = [d.admin_region == self.admin_region for d in self.destinations]
            self.destinations = list(compress(self.destinations, mask))
            
    def get_closest(self, category):
         
        distances = list()
        for destination in self.destinations:
            distances.append(destination.get_distance(self))
        if distances: 
            # return shortest time, mins
            return (min(distances) / 1000 / (5 / 60))
        else:
            return (3000 / 1000 / (5 / 60)) # buffer radius

    def accessibility_index1(self):
        """
        Accessibility Index calculation option 1.
        AIndex is based on usage rate of service type and distance decay to location.

        """
        idx = list()
        # calculate over all destinations within origin radius
        for destination in self.destinations:
            idx.append(destination.get_dist_decay(self) * destination.usage)
        # return sum for origin
        return sum(idx)
    
    def accessibility_index2(self, categories):
        """
        Accessibility Index calculation option 2.
        AIndex is calculated as mean time for closest service in each category.
        
        """
        idx = list()
        # calculate over all destinations within origin radius
        for category in categories:
            idx.append(self.get_closest(category))
        
        # return mean of min travel times
        if idx:
            return (sum(idx) / len(idx))
        else:
            return (3000 / 1000 / (5 / 60)) # buffer radius
    
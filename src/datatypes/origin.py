
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



    def access_prob(self):
        points = list()
        for destination in self.destinations:
            points.append(destination.get_dist_decay(self) * destination.usage)
        return sum(points)
    
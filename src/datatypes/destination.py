
import numpy as np
import json

class Destination(object):
    id_counter = 0
    def __init__(self, category, usage, provider, geometry, admin, admin_region):
        """
        Origin point for which accessibility is calculted.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        geom : geopandas.geoseries.GeoSeries
            Geometry of origin zone or point.
        """
        self.id = Destination.id_counter
        Destination.id_counter += 1
        self.category = category
        self.usage = usage
        self.admin = admin
        self.admin_region = admin_region
        self.provider = provider
        self.geometry = geometry
        self.centroid = geometry.centroid
    
    def get_distance(self, origin):
        """
        Get distances from origin.
        
        Parameters
        ----------
        origin : datatypes.origin.Origin
            Origin to search distance into.
        """
        return self.centroid.distance(origin.centroid)

    def get_dist_decay(self, origin):
        b = -1
        return np.exp(b * self.get_distance(origin) / 1000)

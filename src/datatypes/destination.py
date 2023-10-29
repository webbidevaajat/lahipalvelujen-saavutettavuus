
import numpy as np

class Destination(object):
    def __init__(self, id, geom, category, provider):
        """
        Origin point for which accessibility is calculted.
        
        Parameters
        ----------
        id : str
            Origin id, usually corresponding grid cell.
        geom : geopandas.geoseries.GeoSeries
            Geometry of origin zone or point.
        """
        self.id = id
        self.geom = geom
        self.centroid = geom.centroid
        self.category = category
        self.provider = provider
        self.admin_region = "Vantaa"
    
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
    
    @property
    def usage(self):
        usage_rates = {
            "kindergarten": 0.06,
            "school": 0.16,
            "errands": 0.03,
            "healthcare": 0.06,
            "groceries": 0.48,
            "leisure": 0.03,
            "restaurant": 0.06,
            "sports_facility": 0.10,
        }
        return usage_rates[self.category]

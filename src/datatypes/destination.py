
class Destination(object):
    def __init__(self, id, geom, category):
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


class Origin(object):
    def __init__(self, id, geom):
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
        self.name = None
    
    def get_distances(self, destinations):
        """
        Get distances to all destinations.
        """
        return [self.get_distance(p) for p in destinations]

    def get_distance(self, destination):
        """
        Get distances to single destination.
        
        Parameters
        ----------
        destination : datatypes.destination.Destination
            Destination to search distance into.
        """
        return self.centroid.distance(destination.centroid)

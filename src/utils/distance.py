
from itertools import tee
import math

def haversine(n0, n1):
    """
    Calculates the haversine distance between two points on the
    Earth's surface, given their latitude and longitude coordinates.
    
    """
    x1, y1 = n0
    x2, y2 = n1
    x_dist = math.radians (x1 - x2)
    y_dist = math.radians (y1 - y2)
    y1_rad = math.radians (y1)
    y2_rad = math.radians (y2)
    a = math.sin ( y_dist /2)**2 + math.sin ( x_dist /2)**2 \
    * math.cos (y1_rad) * math.cos (y2_rad)
    c = 2 * math.asin ( math.sqrt (a))
    distance = c * 6371 # The final distance is calculated in kilometers
                        #(using the Earth's mean radius of 6371 kilometers).
    return distance

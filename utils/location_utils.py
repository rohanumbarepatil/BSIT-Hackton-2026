# utils/location_utils.py

import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    Returns distance in kilometers.
    """

    R = 6371  # Earth radius in km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance


def find_nearest_bin(user_location, bin_locations):
    """
    Find nearest bin from a list of bins.
    
    user_location = (lat, lon)
    bin_locations = [
        {"name": "Bin A", "lat": xx, "lon": xx}
    ]
    """

    user_lat, user_lon = user_location

    nearest_bin = None
    min_distance = float("inf")

    for bin in bin_locations:

        distance = haversine_distance(
            user_lat,
            user_lon,
            bin["lat"],
            bin["lon"]
        )

        if distance < min_distance:
            min_distance = distance
            nearest_bin = bin

    return nearest_bin
# services/bin_locator.py

from utils.location_utils import haversine_distance
from config import CAMPUS_BIN_COORDINATES, BIN_DISTANCE_THRESHOLD


def validate_user_location(user_lat, user_lon):
    """
    Check if user is close to any campus bin
    """

    for bin in CAMPUS_BIN_COORDINATES:

        distance = haversine_distance(
            user_lat,
            user_lon,
            bin["lat"],
            bin["lon"]
        )

        # Convert km → meters
        distance_meters = distance * 1000

        if distance_meters <= BIN_DISTANCE_THRESHOLD:
            return True, bin["name"]

    return False, None
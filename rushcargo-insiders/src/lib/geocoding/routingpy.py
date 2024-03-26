from routingpy import ORS

from .constants import (
    ORS_USER_AGENT,
    ORS_PROFILE_DRIVING,
    ORS_PREF_FASTEST,
    NOMINATIM_LATITUDE,
    NOMINATIM_LONGITUDE,
)
from .exceptions import RouteNotFound


# RoutingPy Geocoder Class
class RoutingPyGeocoder:
    # Geolocator
    _geolocator = None

    # Constructor
    def __init__(self, ORSApiKey: str, user: str):
        try:
            # Initialize Geolocator
            self._geolocator = ORS(
                api_key=ORSApiKey, user_agent=f"{ORS_USER_AGENT}-{user}", timeout=5
            )

        except Exception as err:
            raise err

    # Get Driving Route Distance between Two Coordinates from GeoPy Geolocator (in Kilometers)
    def getRouteDistance(self, coords1: dict, coords2: dict) -> int | None:
        try:
            # Get List of Coordinates
            coords = [
                [str(coords1[NOMINATIM_LONGITUDE]), str(coords1[NOMINATIM_LATITUDE])],
                [str(coords2[NOMINATIM_LONGITUDE]), str(coords2[NOMINATIM_LATITUDE])],
            ]

            # Get Client Directions
            route = self._geolocator.directions(
                locations=coords,
                profile=ORS_PROFILE_DRIVING,
                preference=ORS_PREF_FASTEST,
            )

            # Get Distance in Meters
            return route.distance

        except:
            raise RouteNotFound(coords1, coords2)

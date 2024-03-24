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
    def __init__(self, ORSApiKey: str, userAgent: str, user: str):
        try:
            # Initialize Geolocator
            self._geolocator = ORS(
                api_key=ORSApiKey, user_agent=f"{userAgent}-{user}", timeout=5
            )

        except Exception as err:
            raise err

    # Get Driving Route Distance between Two Coordinates from GeoPy Geolocator (in Kilometers)
    def getRouteDistance(self, coords1: dict, coords2: dict) -> int | None:
        try:
            # Get List of Coordinates
            coords = [
                [coords1[NOMINATIM_LONGITUDE], coords1[NOMINATIM_LATITUDE]],
                [coords2[NOMINATIM_LONGITUDE], coords2[NOMINATIM_LATITUDE]],
            ]

            # Get Client Directions
            route = self._geolocator.directions(
                locations=coords,
                profile=ORS_PROFILE_DRIVING,
                preferences=ORS_PREF_FASTEST,
            )

            # Get Distance in Meters
            return route.distance

        except Exception as err:
            raise RouteNotFound(coords1, coords2)


def initRoutingPyGeocoder(ORSApiKey: str, user: str) -> RoutingPyGeocoder:
    return RoutingPyGeocoder(ORSApiKey, ORS_USER_AGENT, user)

from routingpy import ORS

from .constants import (
    ORS_USER_AGENT,
    ORS_PROFILE_DRIVING,
    ORS_PREF_FASTEST,
    ORS_PREFERENCE_SHORTEST,
    NOMINATIM_LATITUDE,
    NOMINATIM_LONGITUDE,
)
from .exceptions import RouteNotFound


class ORSGeocoder:
    """
    Class that Handles RoutingPy (Open Routing Service API) Requests
    """

    # Geolocator
    __geolocator = None

    def __init__(self, ORSApiKey: str, user: str):
        """
        ORS RoutingPy Geocoder Class Constructor

        :param str ORSApiKey: Open Routing Service API Key
        :param str user: Remote Database Role Name
        """

        # Set User Agent Name
        userAgent = f"{ORS_USER_AGENT}-{user}"

        try:
            # Initialize Geolocator
            self.__geolocator = ORS(
                api_key=ORSApiKey, user_agent=userAgent, timeout=5
            )

        except Exception as err:
            raise err

    def __getRouteDistance(self, coords1: dict, coords2: dict, profile: str) -> int:
        """
        Method to Get Route Distance between Two Coordinates through the ORS API (in meters)

        :param dict coords1: Coordinates Route Dictionary of the Starting Point
        :param str coords2: Coordinates Route Dictionary of the End Point
        :param str profile: Route Profile
        :return: Route Distance between the Two Points in meters
        :rtype: int
        :raise RouteNotFound: Raised when there's no Physical Route between the Two Coordinates
        """

        try:
            # Get List of Coordinates
            coords = [
                [str(coords1[NOMINATIM_LONGITUDE]), str(coords1[NOMINATIM_LATITUDE])],
                [str(coords2[NOMINATIM_LONGITUDE]), str(coords2[NOMINATIM_LATITUDE])],
            ]

            # Get Route Directions
            route = self.__geolocator.directions(
                locations=coords,
                profile=profile,
                preference=ORS_PREFERENCE_SHORTEST,
            )

            # Get Distance in Meters
            return route.distance

        except:
            raise RouteNotFound(coords1, coords2)

    def getDrivingRouteDistance(self, coords1: dict, coords2: dict) -> int:
        """
        Method to Get Driving Route Distance between Two Coordinates through the ORS API (in meters)

        :param dict coords1: Coordinates Dictionary of the Starting Point
        :param str coords2: Coordinates Dictionary of the End Point
        :return: Route Distance between the Two Points in meters
        :rtype: int
        """

        return self.__getRouteDistance(coords1, coords2, ORS_PROFILE_DRIVING)

from .constants import NOMINATIM_LATITUDE, NOMINATIM_LONGITUDE


class LocationNotFound(Exception):
    """
    Exception Raised when Geopy couldn't Find a Given Location for a Specific Address Type
    """

    def __init__(self, locationName, locationType):
        """
        LocationNotFound Exception Constructor

        :param str locationName: Location Name that's being Searched for
        :param str locationType: Nominatim API Address Type that's being Compared the Location with
        """

        super().__init__(
            f"GeoPy API couldn't Find '{locationName}' with Address Type of '{locationType}'. Try Again with a Different Name\n"
        )


class PlaceNotFound(Exception):
    """
    Exception Raised when a Place wasn't Found by GeoPy Geocoder
    """

    def __init__(self, cityId: str):
        """
        PlacedNotFound Exception Constructor

        :param str cityId: City ID where the Place was Searched for
        """

        super().__init__(f"Place Not Found at City ID '{cityId}'\n")


class RouteNotFound(Exception):
    """
    Exception Raised when a Geocoder API couldn't Process the Route between Two Coordinates
    """

    def __init__(self, coords1: dict, coords2: dict):
        """
        RouteNotFound Exception Constructor

        :param dict coords1: Coordinates Dictionary of the Route Starting Point
        :param str coords2: Coordinates Dictionary of the Route End Point
        """

        super().__init__(
            f"Route not Found between [lon:'{coords1[NOMINATIM_LONGITUDE]}', lat:'{coords1[NOMINATIM_LATITUDE]}' and [lon:'{coords2[NOMINATIM_LONGITUDE]}', lat:'{coords2[NOMINATIM_LATITUDE]}']\n"
        )

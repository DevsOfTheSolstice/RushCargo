from .constants import NOMINATIM_LATITUDE, NOMINATIM_LONGITUDE


class LocationNotFound(Exception):
    """
    Exception Raised when Geopy couldn't Find a Given Location for a Specific Address Type
    """

    def __init__(
        self, locationName: str, locationType: str, locationAltType: str = None
    ):
        """
        LocationNotFound Exception Constructor

        :param str locationName: Location Name that's being Searched for
        :param str locationType: Nominatim API Address Type that's being Compared the Location with
        :param str locationAltType: Alternative Nominatim API Address Type that's being Compared the Location with
        """

        # Check if there's an Alternative Address Type
        if locationAltType == None:
            super().__init__(
                f"GeoPy API couldn't Find '{locationName}' with Address Type of '{locationType}'. Try Again with a Different Name\n"
            )

        else:
            super().__init__(
                f"GeoPy API couldn't Find '{locationName}' with Address Type of '{locationType}' or Alternative Address Type of '{locationAltType}'. Try Again with a Different Name\n"
            )


class PlaceNotFound(Exception):
    """
    Exception Raised when a Place wasn't Found by GeoPy Geocoder
    """

    def __init__(self, regionId: int, cityName: str):
        """
        PlacedNotFound Exception Constructor

        :param int regionId: Region ID at its Remtoe Table where the City is Located
        :param str cityName: City Name where the Place was Searched for
        """

        super().__init__(
            f"Place Not Found at City '{cityName}' Located at Region ID '{regionId}'\n"
        )


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


class RouteLimitSurpassed(Exception):
    """
    Exception Raised when a the Route Distance between the Two Nodes is too Long and Surpassed a Given Limit
    """

    def __init__(self, coords1: dict, coords2: dict, meters: int, maxMeters: int):
        """
        RouteLimitSurpassed Exception Constructor

        :param dict coords1: Coordinates Dictionary of the Route Starting Point
        :param str coords2: Coordinates Dictionary of the Route End Point
        :param int meters: Route Distance Length (in meters)
        :param int maxMeters: Maximum Route Distance Length Allowed (in meters)
        """

        super().__init__(
            f"Route is Too Long between [lon:'{coords1[NOMINATIM_LONGITUDE]}', lat:'{coords1[NOMINATIM_LATITUDE]}' and [lon:'{coords2[NOMINATIM_LONGITUDE]}', lat:'{coords2[NOMINATIM_LATITUDE]}']\nSurpassed the Route Distance Limit by: {(maxMeters-meters)/1000}km"
        )

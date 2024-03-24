from .constants import NOMINATIM_LATITUDE, NOMINATIM_LONGITUDE


class LocationError(Exception):
    """
    Exception Raised when Geopy couldn't Find a Given Location for a Specific Address Type
    """

    def __init__(self, locationName, locationType):
        super().__init__(
            f"Geopy didn't Find '{locationName}' with Address Type of '{locationType}'. Try Again with a Different Name\n"
        )


class PlaceNotFound(Exception):
    """
    Exception Raised when a Place wasn't Found by GeoPy Geocoder
    """

    def __init__(self, cityAreaName: str, placeName: str):
        super().__init__(f"'{placeName}' Not Found at '{cityAreaName}'\n")


class RouteNotFound(Exception):
    """
    Exception Raised when an Geocoder API couldn't Process the Route between Two Coordinates
    """

    def __init__(self, coords1: dict, coords2: dict):
        super().__init__(
            f"Route not Found between [lon:{coords1[NOMINATIM_LONGITUDE]}, lat:{coords1[NOMINATIM_LATITUDE]} and [lon:{coords2[NOMINATIM_LONGITUDE]}, lat:{coords2[NOMINATIM_LATITUDE]}]\n"
        )

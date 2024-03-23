from geopy.geocoders import Nominatim

from .constants import *
from ..model.constants import CITY_AREA_ID
from ..model.exceptions import *

from ..controller.constants import *


# GeoPy Geocoder Class
class GeoPyGeocoder:
    # Geolocator
    _geolocator = None

    # Constructor
    def __init__(self, userAgent: str, user: str):
        # Initialize Geolocator
        self._geolocator = Nominatim(user_agent=f"{userAgent}-{user}", timeout=5)

    # Get Name
    def __getName(self, locationRaw: dict):
        return locationRaw[NOMINATIM_NAME]

    # Get Country Name
    def getCountry(self, search: str) -> str | None:
        # Get Country Location
        geopyLocation = self._geolocator.geocode(search)

        # Check if it's a Country
        try:
            # Get Country Name
            if geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                return self.__getName(geopyLocation.raw)
            else:
                raise -1
        except:
            raise LocationError(search, NOMINATIM_COUNTRY)

    # Get Province Name
    def getProvince(self, location: dict, province: str) -> str | None:
        # Get Province Location
        geopyLocation = self._geolocator.geocode(
            ", ".join([province, location[DICT_COUNTRY_NAME]])
        )

        # Check if it's a Province
        try:
            if (
                geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE
                or geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE_ALT
            ):
                return self.__getName(geopyLocation.raw)
            else:
                raise -1
        except:
            raise LocationError(province, NOMINATIM_PROVINCE)

    # Get Region Name
    def getRegion(self, location: dict, region: str) -> str | None:
        # Get Region Location
        geopyLocation = self._geolocator.geocode(
            ", ".join(
                [
                    region,
                    location[DICT_PROVINCE_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        # Check if it's a Region
        try:
            if (
                geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION
                or geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION_ALT
            ):
                return self.__getName(geopyLocation.raw)
            else:
                raise -1
        except:
            raise LocationError(region, NOMINATIM_REGION)

    # Get City Name
    def getCity(self, location: dict, city: str) -> str | None:
        # Get City Location
        geopyLocation = self._geolocator.geocode(
            ", ".join(
                [
                    city,
                    location[DICT_REGION_NAME],
                    location[DICT_PROVINCE_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        # Check if it's a City
        try:
            if geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY:
                return self.__getName(geopyLocation.raw)
            else:
                raise -1
        except:
            raise LocationError(city, NOMINATIM_CITY)

    # Get City Area Name
    def getCityArea(self, location: dict, cityArea: str) -> str | None:
        # Get City Area Location
        geopyLocation = self._geolocator.geocode(
            ", ".join(
                [
                    cityArea,
                    location[DICT_CITY_NAME],
                    location[DICT_REGION_NAME],
                    location[DICT_PROVINCE_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        # Check if it's a City Area
        try:
            if geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY_AREA:
                return self.__getName(geopyLocation.raw)
            else:
                raise -1
        except:
            raise LocationError(cityArea, NOMINATIM_CITY_AREA)

    # Get Place Coordinates
    def getPlaceCoordinates(self, location: dict, place: str) -> dict | None:
        # Get Place Location
        geopyLocation = self._geolocator.geocode(
            ", ".join(
                [
                    place,
                    location[DICT_CITY_AREA_NAME],
                    location[DICT_CITY_NAME],
                    location[DICT_REGION_NAME],
                    location[DICT_PROVINCE_NAME],
                    location[DICT_COUNTRY_NAME],
                ]
            )
        )

        try:
            # Intialize Coordinates Dictionary
            coords = {}

            # Check Coordinates
            if geopyLocation == None:
                raise -1

            # Set City Area ID from City Area Table
            coords[CITY_AREA_ID] = location[DICT_CITY_AREA_ID]

            # Set Coordinates
            coords[NOMINATIM_LATITUDE] = geopyLocation.raw[NOMINATIM_LATITUDE]
            coords[NOMINATIM_LONGITUDE] = geopyLocation.raw[NOMINATIM_LONGITUDE]

            return coords
        except:
            raise PlaceNotFound(place, "place")


# Initialize GeoPy Geocoder
def initGeoPyGeocoder(userAgent: str, user: str) -> GeoPyGeocoder:
    return GeoPyGeocoder(userAgent, user)

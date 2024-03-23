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
    def _getCountry(self, search: str) -> str | None:
        # Get Country Location
        location = self._geolocator.geocode(search)

        # Check if it's a Country
        try:
            # Get Country Name
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(search, NOMINATIM_COUNTRY)

    @classmethod
    def getCountry(cls, search:str):
        return cls._getCountry(cls, search)

    # Get Province Name
    def _getProvince(self, location: dict, province: str) -> str | None:
        # Get Province Location
        location = self._geolocator.geocode(
            ", ".join([province, location[DICT_COUNTRY_NAME]])
        )

        # Check if it's a Province
        try:
            if (
                location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE
                or location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE_ALT
            ):
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(province, NOMINATIM_PROVINCE)

    @classmethod
    def getProvince(cls, location:dict, province:str):
        return cls._getProvince(cls, location, province)

    # Get Region Name
    def _getRegion(self, location: dict, region: str) -> str | None:
        # Get Region Location
        location = self._geolocator.geocode(
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
                location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION
                or location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION_ALT
            ):
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(region, NOMINATIM_REGION)

    @classmethod
    def getRegion(cls, location:dict, region:str):
        return cls._getRegion(cls, location, region)

    # Get City Name
    def _getCity(self, location: dict, city: str) -> str | None:
        # Get City Location
        location = self._geolocator.geocode(
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
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(city, NOMINATIM_CITY)

    @classmethod
    def getCity(cls, location:dict, city:str):
        return cls._getCity(cls, location, city)

    # Get City Area Name
    def _getCityArea(self, location: dict, cityArea: str) -> str | None:
        # Get City Area Location
        location = self._geolocator.geocode(
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
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY_AREA:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(cityArea, NOMINATIM_CITY_AREA)

    @classmethod
    def getCityArea(cls, location:dict, cityArea:str):
        return cls._getCityArea(cls,location,cityArea)

    # Get Place Coordinates
    def _getPlaceCoordinates(
        self, location: dict, place: str
    ) -> dict | None:
        # Get Place Location
        location = self._geolocator.geocode(
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

            # Set City Area ID from City Area Table
            coords[CITY_AREA_ID] = location[DICT_CITY_AREA_ID]

            # Set Coordinates
            coords[NOMINATIM_LATITUDE] = location.raw[NOMINATIM_LATITUDE]
            coords[NOMINATIM_LONGITUDE] = location.raw[NOMINATIM_LONGITUDE]

            return coords
        except:
            raise PlaceNotFound(location[DICT_CITY_AREA_NAME], place)

    @classmethod
    def getPlaceCoordinates(cls, location:dict, place:str):
        return cls._getPlaceCoordinates(cls, location, place)


# Initialize GeoPy Geocoder
def initGeoPyGeocoder(userAgent: str, user: str) -> GeoPyGeocoder:
    return GeoPyGeocoder(userAgent, user)

from geopy.geocoders import Nominatim

from .constants import *
from .exceptions import LocationError, PlaceNotFound

from ..model.constants import CITY_AREA_ID

from ..controller.constants import (
    DICT_CITY_AREA_NAME,
    DICT_CITY_AREA_ID,
    DICT_CITY_NAME,
    DICT_REGION_NAME,
    DICT_PROVINCE_NAME,
    DICT_COUNTRY_NAME,
)


# GeoPy Geocoder Class
class GeoPyGeocoder:
    # Geolocator
    _geolocator = None

    # Constructor
    def __init__(self, userAgent: str, user: str):
        try:
            # Initialize Geolocator
            self._geolocator = Nominatim(user_agent=f"{userAgent}-{user}", timeout=5)
        
        except Exception as err:
            raise err

    # Get Name
    def __getName(self, locationRaw: dict):
        return locationRaw[NOMINATIM_NAME]

    # Get Country Name
    def getCountry(self, search: str) -> str | None:
        try:
            # Get Country Location
            geopyLocation = self._geolocator.geocode(search)

            # Check if it's a Country
            if geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                return self.__getName(geopyLocation.raw)
            
            raise LocationError(search, NOMINATIM_COUNTRY)
        
        except Exception as err:
            raise err

    # Get Province Name
    def getProvince(self, location: dict, province: str) -> str | None:
        try:
            # Get Province Location
            geopyLocation = self._geolocator.geocode(
                ", ".join([province, location[DICT_COUNTRY_NAME]])
            )

            # Check if it's a Province
            if (
                geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE
                or geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE_ALT
            ):
                return self.__getName(geopyLocation.raw)
            
            raise LocationError(province, NOMINATIM_PROVINCE)
            
        except Exception as err:
            raise err

    # Get Region Name
    def getRegion(self, location: dict, region: str) -> str | None:
        try:
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
            if (
                geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION
                or geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION_ALT
            ):
                return self.__getName(geopyLocation.raw)
            
            raise LocationError(region, NOMINATIM_REGION)
        
        except Exception as err:
            raise err

    # Get City Name
    def getCity(self, location: dict, city: str) -> str | None:
        try:
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
            if geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY:
                return self.__getName(geopyLocation.raw)

            raise LocationError(city, NOMINATIM_CITY)
        
        except Exception as err:
            raise err

    # Get City Area Name
    def getCityArea(self, location: dict, cityArea: str) -> str | None:
        try:
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
            if geopyLocation.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY_AREA:
                return self.__getName(geopyLocation.raw)

            raise LocationError(cityArea, NOMINATIM_CITY_AREA)

        except Exception as err:
            raise err

    # Get Place Coordinates
    def getPlaceCoordinates(self, location: dict, place: str) -> dict | None:
        try:
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

            # Intialize Coordinates Dictionary
            coords = {}

            # Check Coordinates
            if geopyLocation == None:
                raise PlaceNotFound(place, "place")

            # Set City Area ID from City Area Table
            coords[CITY_AREA_ID] = location[DICT_CITY_AREA_ID]

            # Set Coordinates
            coords[NOMINATIM_LATITUDE] = geopyLocation.raw[NOMINATIM_LATITUDE]
            coords[NOMINATIM_LONGITUDE] = geopyLocation.raw[NOMINATIM_LONGITUDE]

            return coords

        except Exception as err:
            return err


# Initialize GeoPy Geocoder
def initGeoPyGeocoder(user: str) -> GeoPyGeocoder:
    return GeoPyGeocoder(NOMINATIM_USER_AGENT, user)

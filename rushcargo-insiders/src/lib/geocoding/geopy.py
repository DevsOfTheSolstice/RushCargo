from geopy.geocoders import Nominatim

from .constants import *
from ..model.exceptions import *


# Geopy Geocoder Class
class GeopyGeocoder:
    # Geolocator
    _geolocator = None

    # Constructor
    def __init__(self, userAgent: str):
        self._geolocator = Nominatim(user_agent=userAgent)

    # Get Name
    def __getName(self, locationRaw: dict):
        return locationRaw[NOMINATIM_NAME]

    # Get Country Name
    def getCountry(self, country: str) -> str | None:
        # Get Country Location
        location = self._geolocator.geocode(country)

        # Check if it's a Country:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(country, NOMINATIM_COUNTRY)

    # Get Region Name
    def getRegion(self, country: str, region: str) -> str | None:
        # Get Region Location
        location = self._geolocator.geocode(", ".join([region, country]))

        # Check if it's a Region:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(region, NOMINATIM_REGION)

    # Get Subregion Name
    def getSubregion(self, country: str, region: str, subregion: str) -> str | None:
        # Get Subregion Location
        location = self._geolocator.geocode(", ".join([subregion, region, country]))

        # Check if it's a Subregion:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_SUBREGION:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(subregion, NOMINATIM_SUBREGION)

    # Get City Name
    def getCity(
        self, country: str, region: str, subregion: str, city: str
    ) -> str | None:
        # Get City Location
        location = self._geolocator.geocode(
            ", ".join([city, subregion, region, country])
        )

        # Check if it's a City:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(city, NOMINATIM_CITY)

    # Get City Area Name
    def getCityArea(
        self, country: str, region: str, subregion: str, city: str, cityArea: str
    ) -> str | None:
        # Get City Area Location
        location = self._geolocator.geocode(
            ", ".join([cityArea, city, subregion, region, country])
        )

        # Check if it's a City Area:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY_AREA:
                return self.__getName(location.raw)
            else:
                raise -1
        except:
            raise LocationError(cityArea, NOMINATIM_CITY_AREA)


# Initialize Geopy Geocoder
def initGeopyGeocoder(userAgent: str) -> GeopyGeocoder:
    return GeopyGeocoder(userAgent)

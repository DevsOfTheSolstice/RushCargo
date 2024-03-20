from geopy.geocoders import Nominatim

from .constants import *
from ..model.exceptions import *

from ..local_database.database import *
from ..local_database.constants import *


# GeoPy Geocoder Class
class GeoPyGeocoder:
    # Geolocator
    _geolocator = None

    # GeoPy Local Database
    _localdb = None
    _tables = None

    # Constructor
    def __init__(self, userAgent: str, user: str):
        # Initialize Geolocator
        self._geolocator = Nominatim(user_agent=f"{userAgent}-{user}", timeout=5)

        # Initialize GeoPy Local Database
        self._localdb = GeoPyDatabase()
        self._tables = GeoPyTable(self._localdb)

    # Get Name
    def __getName(self, locationRaw: dict):
        return locationRaw[NOMINATIM_NAME]

    # Get Country Name
    def getCountry(self, search: str) -> str | None:
        # Check if Country Search is Stored at Local Database
        name = self._tables.getCountry(search)

        if name != None:
            return name

        # Get Country Location
        location = self._geolocator.geocode(search)

        # Check if it's a Country:
        try:
            if location.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                # Get Country Name
                name = self.__getName(location.raw)

                # Store Country Search at Local Database
                self._tables.addCountry(search, name)

                return name
            else:
                raise -1
        except:
            raise LocationError(search, NOMINATIM_COUNTRY)

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


# Initialize GeoPy Geocoder
def initGeoPyGeocoder(userAgent: str, user: str) -> GeoPyGeocoder:
    return GeoPyGeocoder(userAgent, user)

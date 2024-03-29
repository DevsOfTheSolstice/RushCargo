from geopy.geocoders import Nominatim

from .constants import *
from .exceptions import LocationNotFound, PlaceNotFound

from ..controller.constants import (
    DICT_CITY_ID,
    DICT_CITY_NAME,
    DICT_REGION_ID,
    DICT_REGION_NAME,
    DICT_PROVINCE_NAME,
    DICT_COUNTRY_NAME,
)

from ..model.constants import CITY_ID


class NominatimGeocoder:
    """
    Class that Handles GeoPy (Nominatim API) Requests
    """

    # Geolocator
    __geolocator = None

    def __init__(self, user: str):
        """
        Nominatim GeoPy Geocoder Class Constructor

        :param str user: Remote Database Role Name
        """

        try:
            # Initialize Geolocator
            self.__geolocator = Nominatim(
                user_agent=f"{NOMINATIM_USER_AGENT}-{user}", timeout=5
            )

        except Exception as err:
            raise err

    def __getName(self, location: dict) -> str:
        """
        Method to Get Location Name from the Coincidence Dictionary Returned by Nominatim API

        :param dict location: Coincidence Dictionary Returned by Nominatim API
        :return: Location Name
        :rtype: str
        """

        return location.raw[NOMINATIM_NAME]

    def getCountry(self, countryName: str) -> str:
        """
        Method to Check if a Country Name is Valid and its Normalized Form through the Nominatim API

        :param str countryName: Country Name to be Validated and Normalized
        :return: Country Normalized Name
        :rtype: str
        :raise LocationNotFound: Raised when there's no Country Coincidence for the Given Name
        """

        try:
            # Get Country Location
            geopyLocation = self.__geolocator.geocode(countryName, exactly_one=False)

            # Check Location
            if geopyLocation == None:
                raise LocationNotFound(countryName, NOMINATIM_COUNTRY)

            # Iterate over Coincidences
            for coincidence in geopyLocation:
                # Check if it's a Country
                if coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_COUNTRY:
                    return self.__getName(coincidence)

            # Invalid Location
            raise LocationNotFound(countryName, NOMINATIM_COUNTRY)

        except LocationNotFound as err:
            raise err

    def getProvince(self, location: dict, provinceName: str) -> str:
        """
        Method to Check if a Province Name is Valid and its Normalized Form through the Nominatim API

        :param dict location: Location Dictionary that Contains the Province Parent Locations Information
        :param str provinceName: Province Name to be Validated and Normalized
        :return: Province Normalized Name
        :rtype: str
        :raise LocationError: Raised when there's no Province Coincidence for the Given Name at the Given Parent Location
        """

        try:
            # Get Province Location
            geopyLocation = self.__geolocator.geocode(
                ", ".join([provinceName, location[DICT_COUNTRY_NAME]]),
                exactly_one=False,
            )

            # Check Location
            if geopyLocation == None:
                raise LocationNotFound(provinceName, NOMINATIM_PROVINCE)

            # Iterate over Coincidences
            for coincidence in geopyLocation:
                # Check if it's a Province
                if (
                    coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE
                    or coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_PROVINCE_ALT
                ):
                    return self.__getName(coincidence)

            # Invalid Location
            raise LocationNotFound(provinceName, NOMINATIM_PROVINCE)

        except LocationNotFound as err:
            raise err

    def getRegion(self, location: dict, regionName: str) -> str:
        """
        Method to Check if a Region Name is Valid and its Normalized Form through the Nominatim API

        :param dict location: Location Dictionary that Contains the Region Parent Locations Information
        :param str regionName: Region Name to be Validated and Normalized
        :return: Region Normalized Name
        :rtype: str
        :raise LocationError: Raised when there's no Region Coincidence for the Given Name at the Given Parent Location
        """

        try:
            # Get Region Location
            geopyLocation = self.__geolocator.geocode(
                ", ".join(
                    [
                        regionName,
                        location[DICT_PROVINCE_NAME],
                        location[DICT_COUNTRY_NAME],
                    ]
                ),
                exactly_one=False,
            )

            # Check Location
            if geopyLocation == None:
                raise LocationNotFound(regionName, NOMINATIM_REGION)

            # Iterate over Coincidences
            for coincidence in geopyLocation:
                print(coincidence.raw)
                # Check if it's a Region
                if (
                    coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION
                    or coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_REGION_ALT
                    or coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_DIVISION_ALT
                ):
                    return self.__getName(coincidence)

            # Invalid Location
            raise LocationNotFound(regionName, NOMINATIM_REGION)

        except LocationNotFound as err:
            raise err

    def getCity(self, location: dict, cityName: str) -> str:
        """
        Method to Check if a City Name is Valid and its Normalized Form through the Nominatim API

        :param dict location: Location Dictionary that Contains the City Parent Locations Information
        :param str cityName: City Name to be Validated and Normalized
        :return: City Normalized Name
        :rtype: str
        :raise LocationError: Raised when there's no City Coincidence for the Given Name at the Given Parent Location
        """

        try:
            # Get City Location
            geopyLocation = self.__geolocator.geocode(
                ", ".join(
                    [
                        cityName,
                        location[DICT_REGION_NAME],
                        location[DICT_PROVINCE_NAME],
                        location[DICT_COUNTRY_NAME],
                    ]
                ),
                exactly_one=False,
            )

            # Check Location
            if geopyLocation == None:
                raise LocationNotFound(cityName, NOMINATIM_CITY)

            # Iterate over Coincidences
            for coincidence in geopyLocation:
                # Check if it's a City
                if (
                    coincidence.raw[NOMINATIM_ADDRESS_TYPE] == NOMINATIM_CITY
                    or coincidence.raw[NOMINATIM_CITY] == NOMINATIM_DIVISION_ALT
                ):
                    return self.__getName(coincidence)

            # Invalid Location
            raise LocationNotFound(cityName, NOMINATIM_CITY)

        except LocationNotFound as err:
            raise err

    def getPlaceCoordinates(self, location: dict, placeName: str) -> dict:
        """
        Method to Check if a Place Name is Valid and Get its Latitude and Longitude Coordinates through the Nominatim API

        :param dict location: Location Dictionary that Contains the Place Parent Locations Information
        :param str placeName: Place Name to be Validated
        :return: Dictionary that Holds the City ID where the Placed is Located, and the Place Latitude and Longitude Coordinates
        :rtype: dict
        :raise PlaceNotFound: Raised when there's no Place Coincidence for the Given Name at the Given Parent Location
        """

        try:
            # Get Place Location
            geopyLocation = self.__geolocator.geocode(
                ", ".join(
                    [
                        placeName,
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
                raise PlaceNotFound(location[DICT_REGION_ID], location[DICT_CITY_NAME])

            # Set City ID from City Table
            coords[CITY_ID] = location[DICT_CITY_ID]

            # Set Latitude and Longitude Coordinates Received by the Nominatim API
            coords[NOMINATIM_LATITUDE] = geopyLocation.raw[NOMINATIM_LATITUDE]
            coords[NOMINATIM_LONGITUDE] = geopyLocation.raw[NOMINATIM_LONGITUDE]

            return coords

        except PlaceNotFound as err:
            raise err

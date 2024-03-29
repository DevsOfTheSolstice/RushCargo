from rich.prompt import Prompt, IntPrompt, Confirm

from .constants import *
from .exceptions import (
    RowNotFound,
    EmptyTable,
    InvalidLocation,
    WarehouseNotFound,
    MainWarehouseError,
)

from ..geocoding.exceptions import LocationNotFound, PlaceNotFound
from ..geocoding.geopy import (
    NominatimGeocoder,
    NOMINATIM_LATITUDE,
    NOMINATIM_LONGITUDE,
)
from ..geocoding.routingpy import ORSGeocoder

from ..io.constants import (
    ADD,
    RM,
    ALL,
    GET,
    MOD,
)
from ..io.exceptions import GoToMenu
from ..io.validator import *

from ..local_database.database import NominatimDatabase, NominatimTables

from ..model.database_territory import *
from ..model.database_building import *
from ..model.database_connections import *

from ..terminal.constants import *


class LocationEventHandler:
    """
    Class that Handles the Location-related Subcommands
    """

    # Table Classes
    __countryTable = None
    __provinceTable = None
    __regionTable = None
    __cityTable = None
    __warehouseTable = None
    __warehouseConnTable = None
    __branchTable = None

    # Nominatim GeoPy Local Database Tables
    __localDatabase = None
    __localTables = None

    # Geocoders
    __nominatimGeocoder = None
    __ORSGeocoder = None

    # Get Location Messages
    __GET_COUNTRY_MSG = "Enter Country Name"
    __GET_PROVINCE_MSG = "Enter Province Name"
    __GET_REGION_MSG = "Enter Region Name"
    __GET_CITY_MSG = "Enter City Name"

    # Constructor
    def __init__(self, remoteCursor, user: str, ORSApiKey: str):
        """
        Location Event Handler Class Constructor

        :param Cursor[TupleRow] remoteCursor: Remote Database Connection Cursor
        :param str user: Remote Database Role Name
        :param str ORSApiKey: Open Routing Service API Key
        """

        # Initialize Table Classes
        self.__countryTable = CountryTable(remoteCursor)
        self.__provinceTable = ProvinceTable(remoteCursor)
        self.__regionTable = RegionTable(remoteCursor)
        self.__cityTable = CityTable(remoteCursor)
        self.__warehouseTable = WarehouseTable(remoteCursor)
        self.__warehouseConnTable = WarehouseConnectionTable(remoteCursor)
        self.__branchTable = BranchTable(remoteCursor)

        # Initialize Nominatim GeoPy Local Database and Get Connection Cursor
        self.__localDatabase = NominatimDatabase()
        localCursor = self.__localDatabase.getCursor()

        # Initialize Local Nominatim GeoPy Database Tables Class
        self.__localTables = NominatimTables(localCursor)

        # Initialize Nominatim GeoPy and RoutingPy Geocoders
        self.__nominatimGeocoder = NominatimGeocoder(user)
        self.__ORSGeocoder = ORSGeocoder(ORSApiKey, user)

    def __getRouteDistance(self, warehouseId: int, locationCoords: dict) -> int:
        """
        Method to Get the Route Distance between a Warehouse and a Given Location

        :param int warehouseId: Warehouse ID at its Remote Table
        :param dict location: Dictionary that Contains the Coordinates for a Given Place
        :return: Route Distance between the Warehouse and the Given Location
        :rtype: int
        """

        # Get Warehouse Object
        warehouse = self.__warehouseTable.find(warehouseId)

        # Initialize Warehouse Coordinates Dictionary
        warehouseCoords = {}

        # Get Warehouse Coordinates
        warehouseCoords[NOMINATIM_LATITUDE] = warehouse.gpsLatitude
        warehouseCoords[NOMINATIM_LONGITUDE] = warehouse.gpsLongitude

        # Calculate Route Distance
        routeDistance = self.__ORSGeocoder.getDrivingRouteDistance(
            warehouseCoords, locationCoords
        )

        return routeDistance

    def __getWarehouseDict(self, warehouseId: int) -> dict:
        """
        Method to Get a Valid Warehouse Dictionary to be Used by a Warehouse-related Table Class

        :param int warehouseId: Warehouse ID at its Remote Table
        :return: Warehouse Dictionary that Contains its Building ID and its Coordinates
        :rtype: dict
        """

        # Get Warehouse Object
        warehouse = self.__warehouseTable.find(warehouseId)

        # Initialize Warehouse Dictionary
        warehouseDict = {}

        # Assign Dictionary Fields
        warehouseDict[DICT_WAREHOUSE_ID] = warehouseId
        warehouseDict[DICT_WAREHOUSE_COORDS] = {
            NOMINATIM_LONGITUDE: warehouse.gpsLongitude,
            NOMINATIM_LATITUDE: warehouse.gpsLatitude,
        }

        return warehouseDict

    def getCountryName(self) -> dict | None:
        """
        Method to Search for a Country Name in the Local Database

        :return: A Dictionary that Contains the Country Name and its ID from its Local SQLite Table if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Initialize Location Data Dictionary
        location = {}

        while True:
            try:
                countrySearch = Prompt.ask(self.__GET_COUNTRY_MSG)

                # Check Country Name
                isAddressValid(COUNTRY_TABLENAME, COUNTRY_NAME, countrySearch)

                # Check if the Search is Stored in the Local Database
                countryNameId = self.__localTables.getCountrySearchNameId(countrySearch)
                location[DICT_COUNTRY_NAME_ID] = countryNameId

                # Check Country Name ID
                if countryNameId != None:
                    # Get Country Name from Local Database
                    countryName = self.__localTables.getCountryName(countryNameId)
                    location[DICT_COUNTRY_NAME] = countryName

                else:
                    # Get Country Name from Nominatim GeoPy API based on the Name Provided
                    countryName = self.__nominatimGeocoder.getCountry(countrySearch)
                    location[DICT_COUNTRY_NAME] = countryName

                    # Store Country Search in Local Database
                    self.__localTables.addCountry(countrySearch, countryName)

                    # Get Country Name ID from Local Database
                    location[DICT_COUNTRY_NAME_ID] = (
                        self.__localTables.getCountryNameId(countryName)
                    )

                return location

            # Raise GoToMenu Error
            except GoToMenu as err:
                raise err

            # Go Back to the While-loop
            except (LocationNotFound, FieldValueError) as err:
                console.print(err, style="warning")

                # Go Back to the While-loop
                if Confirm.ask("Do you want to Type Another Country Name?"):
                    # Clear Terminal
                    clear()
                    continue

                return None

    def getCountryDict(self) -> dict:
        """
        Method to Get Country ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :return: A Dictionary that Contains the Country ID from its Remote Table, and the Columns that were Inserted at ``self.getCountryName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the Country Name) to Search for it in its Table
        location = self.getCountryName()
        countryName = location[DICT_COUNTRY_NAME]

        try:
            # Check if the Country Name is Stored at the Remote Database
            if not self.__countryTable.get(COUNTRY_NAME, countryName, False):
                raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

        except RowNotFound:
            # Clear Terminal
            clear()

            # Insert Country
            self.__countryTable.add(countryName)

        # Get Country Object from the Remote Database
        c = self.__countryTable.find(COUNTRY_NAME, countryName)

        # Set Country ID to Data Dictionary
        location[DICT_COUNTRY_ID] = c.countryId

        return location

    def getProvinceName(self) -> dict | None:
        """
        Method to Search for a Province Name in the Local Database

        :return: A Dictionary that Contains the Province Name and its ID from its Local SQLite Table, and the Columns that were Inserted at ``self.getCountryDict()`` Call if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the Country Name and its ID in the Local SQLite and Remote Database)
        location = self.getCountryDict()

        while True:
            try:
                provinceSearch = Prompt.ask(self.__GET_PROVINCE_MSG)

                # Check Province Name
                isAddressValid(PROVINCE_TABLENAME, PROVINCE_NAME, provinceSearch)

                # Check if the Search is Stored in the Local Database
                provinceNameId = self.__localTables.getProvinceSearchNameId(
                    location[DICT_COUNTRY_NAME_ID], provinceSearch
                )
                location[DICT_PROVINCE_NAME_ID] = provinceNameId

                # Check Province Name ID
                if provinceNameId != None:
                    # Get Province Name from Local Database
                    provinceName = self.__localTables.getProvinceName(provinceNameId)
                    location[DICT_PROVINCE_NAME] = provinceName

                else:
                    # Get Province Name from Nominatim GeoPy API based on the Name Provided
                    provinceName = self.__nominatimGeocoder.getProvince(
                        location, provinceSearch
                    )
                    location[DICT_PROVINCE_NAME] = provinceName

                    # Store Province Search at Local Database
                    self.__localTables.addProvince(
                        location[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
                    )

                    # Get Province Name ID from Local Database
                    location[DICT_PROVINCE_NAME_ID] = (
                        self.__localTables.getProvinceNameId(
                            location[DICT_COUNTRY_NAME_ID], provinceName
                        )
                    )

                return location

            # Raise GoToMenu Error
            except GoToMenu as err:
                raise err

            except (LocationNotFound, FieldValueError) as err:
                console.print(err, style="warning")

                # Go Back to the While-loop
                if Confirm.ask("Do you want to Type Another Province Name?"):
                    # Clear Terminal
                    clear()
                    continue

                return None

    def getProvinceDict(self) -> dict:
        """
        Method to Get Province ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :return: A Dictionary that Contains the Province ID from its Remote Table, and the Columns that were Inserted at ``self.getProvinceName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the Province Name) to Search for it in its Table
        location = self.getProvinceName()
        countryId = location[DICT_COUNTRY_ID]
        provinceName = location[DICT_PROVINCE_NAME]

        provinceFields = [PROVINCE_FK_COUNTRY, PROVINCE_NAME]
        provinceValues = [countryId, provinceName]

        try:

            # Check if the Province Name at the Given Country ID is Stored at the Remote Database
            if not self.__provinceTable.getMult(provinceFields, provinceValues, False):
                raise InvalidLocation(provinceName, COUNTRY_TABLENAME, countryId)

        except InvalidLocation:
            # Clear Terminal
            clear()

            # Insert Province
            self.__provinceTable.add(countryId, provinceName)

        # Get Province Object from the Remote Database
        p = self.__provinceTable.findMult(countryId, provinceName)

        # Set Province ID to Data Dictionary
        location[DICT_PROVINCE_ID] = p.provinceId

        return location

    def getRegionName(self) -> dict | None:
        """
        Method to Search for a Region Name in the Local Database

        :return: A Dictionary that Contains the Region Name and its ID from its Local SQLite Table, and the Columns that were Inserted at ``self.getProvinceDict()`` Call if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the Province Name and its ID in the Local SQLite and Remote Database)
        location = self.getProvinceDict()

        while True:
            try:
                regionSearch = Prompt.ask(self.__GET_REGION_MSG)

                # Check Region Name
                isAddressValid(REGION_TABLENAME, REGION_NAME, regionSearch)

                # Check if the Search is Stored in the Local Database
                regionNameId = self.__localTables.getRegionSearchNameId(
                    location[DICT_PROVINCE_NAME_ID], regionSearch
                )
                location[DICT_REGION_NAME_ID] = regionNameId

                # Check Region Name ID
                if regionNameId != None:
                    # Get Region Name from Local Database
                    regionName = self.__localTables.getRegionName(regionNameId)
                    location[DICT_REGION_NAME] = regionName

                else:
                    # Get Region Name from Nominatim GeoPy API based on the Name Provided
                    regionName = self.__nominatimGeocoder.getRegion(
                        location, regionSearch
                    )

                    location[DICT_REGION_NAME] = regionName

                    # Store Region Search at Local Database
                    self.__localTables.addRegion(
                        location[DICT_PROVINCE_NAME_ID], regionSearch, regionName
                    )

                    # Get Region Name ID from Local Database
                    location[DICT_REGION_NAME_ID] = self.__localTables.getRegionNameId(
                        location[DICT_PROVINCE_NAME_ID], regionName
                    )

                return location

            # Raise GoToMenu Error
            except GoToMenu as err:
                raise err

            except (LocationNotFound, FieldValueError) as err:
                console.print(err, style="warning")

                # Go Back to the While-loop
                if Confirm.ask("Do you want to Type Another Region Name?"):
                    # Clear Terminal
                    clear()
                    continue

                return None

    def getRegionDict(self) -> dict:
        """
        Method to Get Region ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :return: A Dictionary that Contains the Region ID from its Remote Table, and the Columns that were Inserted at ``self.getRegionName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the Region Name) to Search for it in its Table
        location = self.getRegionName()
        provinceId = location[DICT_PROVINCE_ID]
        regionName = location[DICT_REGION_NAME]

        regionFields = [REGION_FK_PROVINCE, REGION_NAME]
        regionValues = [provinceId, regionName]

        try:
            # Check if the Region Name at the Given Province ID is Stored at the Remote Database
            if not self.__regionTable.getMult(regionFields, regionValues, False):
                raise InvalidLocation(regionName, PROVINCE_TABLENAME, provinceId)

        except InvalidLocation:
            # Clear Terminal
            clear()

            # Insert Region
            self.__regionTable.add(provinceId, regionName)

        # Get Region Object from the Remote Database
        r = self.__regionTable.findMult(provinceId, regionName)

        # Set Region ID to Data Dictionary
        location[DICT_REGION_ID] = r.regionId

        return location

    def getCityName(self) -> dict | None:
        """
        Method to Search for a City Name in the Local Database

        :return: A Dictionary that Contains the City Name and its ID from its Local SQLite Table, and the Columns that were Inserted at ``self.getRegionDict()`` Call if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the Region Name and its ID in the Local SQLite and Remote Database)
        location = self.getRegionDict()

        while True:
            try:
                citySearch = Prompt.ask(self.__GET_CITY_MSG)

                # Check City Name
                isAddressValid(CITY_TABLENAME, CITY_NAME, citySearch)

                # Check if the Search is Stored in the Local Database
                cityNameId = self.__localTables.getCitySearchNameId(
                    location[DICT_REGION_NAME_ID], citySearch
                )
                location[DICT_CITY_NAME_ID] = cityNameId

                # Check City Name ID
                if cityNameId != None:
                    # Get City Name from Local Database
                    cityName = self.__localTables.getCityName(cityNameId)
                    location[DICT_CITY_NAME] = cityName

                else:
                    # Get City Name from Nominatim GeoPy API based on the Name Provided
                    cityName = self.__nominatimGeocoder.getCity(location, citySearch)

                    location[DICT_CITY_NAME] = cityName

                    # Store City Search at Local Database
                    self.__localTables.addCity(
                        location[DICT_REGION_NAME_ID], citySearch, cityName
                    )

                    # Get City Name ID from Local Database
                    location[DICT_CITY_NAME_ID] = self.__localTables.getCityNameId(
                        location[DICT_REGION_NAME_ID], cityName
                    )

                return location

            # Raise GoToMenu Error
            except GoToMenu as err:
                raise err

            except (LocationNotFound, FieldValueError) as err:
                console.print(err, style="warning")

                # Go Back to the While-loop
                if Confirm.ask("Do you want to Type Another City Name?"):
                    # Clear Terminal
                    clear()
                    continue

                return None

    def getCityDict(self) -> dict:
        """
        Method to Get City ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :return: A Dictionary that Contains the City ID from its Remote Table, and the Columns that were Inserted at ``self.getCityName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the City Name) to Search for it in its Table
        location = self.getCityName()
        regionId = location[DICT_REGION_ID]
        cityName = location[DICT_CITY_NAME]

        cityFields = [CITY_FK_REGION, CITY_NAME]
        cityValues = [regionId, cityName]

        try:

            # Check if the City Name at the Given Region ID is Stored at the Remote Database
            if not self.__cityTable.getMult(cityFields, cityValues, False):
                raise InvalidLocation(cityName, REGION_TABLENAME, regionId)

        except InvalidLocation:
            # Clear Terminal
            clear()

            # Insert City
            self.__cityTable.add(regionId, cityName)

        # Get City Object from the Remote Database
        c = self.__cityTable.findMult(regionId, cityName)

        # Set City ID to Data Dictionary
        location[DICT_CITY_ID] = c.cityId

        return location

    def getPlaceCoordinates(self) -> dict | None:
        """
        Method to Get Place Coordinates in a Given City ID

        :return: A Dictionary that Contains the City ID from its Remote Table, and the Latitude and Longitude of the Given Place Obtained through the ``self.__nominatimGeocoder`` Object if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        # Get Location Dictionary (that Contains the City ID)
        location = self.getCityDict()

        while True:
            try:
                # Get Place Name to Search
                placeSearch = Prompt.ask("Enter Place Name Near to the Building")

                isPlaceNameValid(placeSearch)

                # Get Place Coordinates from Nominatim GeoPy API based on the Data Provided
                coords = self.__nominatimGeocoder.getPlaceCoordinates(
                    location, placeSearch
                )

                location[NOMINATIM_LATITUDE] = coords[NOMINATIM_LATITUDE]
                location[NOMINATIM_LONGITUDE] = coords[NOMINATIM_LONGITUDE]

                return location

            # Raise GoToMenu Error
            except GoToMenu as err:
                raise err

            except (LocationNotFound, PlaceNotFound) as err:
                console.print(err, style="warning")

                # Go Back to the While-loop
                if Confirm.ask("Do you want to Type Another Place Name?"):
                    # Clear Terminal
                    clear()
                    continue

                return None

    def __getCountry(self) -> int:
        """
        Method to Get Country ID from its Remote Table by Printing the Tables, and Selecting the Row Country ID

        :return: Country ID at its Remote Table
        :rtype: int
        """

        # Clear Terminal
        clear()

        # Print All Countries
        if self.__countryTable.all(COUNTRY_NAME, False) == 0:
            raise EmptyTable(COUNTRY_TABLENAME)

        while True:
            try:
                # Select Country ID
                countryId = IntPrompt.ask("\nSelect Country ID")

                # Get Country Object
                country = self.__countryTable.find(COUNTRY_ID, countryId)

                # Check if Country ID Exists
                if country == None:
                    raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_ID, countryId)

                return countryId

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    def getCountryId(self) -> int:
        """
        Method to Select a Country ID from its Remote Table

        :return: Country ID at its Remote Table
        :rtype: int
        """

        return self.__getCountry()

    def __getProvince(self, countryId: int) -> int:
        """
        Method to Get Province ID from its Remote Table by Printing the Tables, and Selecting the Row Province ID, Given a Country ID

        :param int countryId: Country ID at its Remote Table where the Province is Located
        :return: Province ID at its Remote Table
        :rtype: int
        """

        # Clear Terminal
        clear()

        # Print Provinces at the Given Country ID
        if not self.__provinceTable.get(PROVINCE_FK_COUNTRY, countryId):
            raise RowNotFound(PROVINCE_TABLENAME, PROVINCE_FK_COUNTRY, countryId)

        while True:
            try:
                # Select Province ID
                provinceId = IntPrompt.ask("\nSelect Province ID")

                # Get Province Object
                province = self.__provinceTable.find(provinceId)

                # Check if Province ID Exists
                if province == None:
                    raise RowNotFound(PROVINCE_TABLENAME, PROVINCE_ID, provinceId)

                elif province.countryId != countryId:
                    raise InvalidLocation(province.name, COUNTRY_TABLENAME, countryId)

                return provinceId

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    def getProvinceId(self) -> int:
        """
        Method to Select a Province ID from its Remote Table

        :return: Province ID at its Remote Table
        :rtype: int
        """

        # Get Country ID where the Province is Located
        countryId = self.getCountryId()

        return self.__getProvince(countryId)

    def __getRegion(self, provinceId: int) -> int:
        """
        Method to Get Region ID from its Remote Table by Printing the Tables, and Selecting the Row Region ID, Given a Province ID

        :param int provinceId: Province ID at its Remote Table where the Region is Located
        :return: Region ID at its Remote Table
        :rtype: int
        """

        # Clear Terminal
        clear()

        # Print Regions at the Given Province ID
        if not self.__regionTable.get(REGION_FK_PROVINCE, provinceId):
            raise RowNotFound(REGION_TABLENAME, REGION_FK_PROVINCE, provinceId)

        while True:
            try:
                # Select Region ID
                regionId = IntPrompt.ask("\nSelect Region ID")

                # Get Region Object
                region = self.__regionTable.find(regionId)

                # Check if Region ID Exists
                if region == None:
                    raise RowNotFound(REGION_TABLENAME, REGION_ID, regionId)

                elif region.provinceId != provinceId:
                    raise InvalidLocation(region.name, PROVINCE_TABLENAME, provinceId)

                return regionId

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    def getRegionId(self) -> int:
        """
        Method to Select a Region ID from its Remote Table

        :return: Region ID at its Remote Table
        :rtype: int
        """

        # Get Province ID where the Region is Located
        provinceId = self.getProvinceId()

        return self.__getRegion(provinceId)

    def getProvinceBuildingCityId(self, provinceId: int) -> int:
        """
        Method to Select a Building City ID from its Remote Table by Getting All of its Parent Location Given a Province ID

        :param int province: Province ID at its Remote Table where the Building is Located
        :return: Building City ID at its Remote Table
        :rtype: int
        """

        regionId = self.__getRegion(provinceId)

        return self.getRegionBuildingCityId(regionId)

    def __getCity(self, regionId: int) -> int:
        """
        Method to Get City ID from its Remote Table by Printing the Tables, and Selecting the Row City ID, Given a Region ID

        :param int regionId: Region ID at its Remote Table where the City is Located
        :return: City ID at its Remote Table
        :rtype: int
        """

        # Clear Terminal
        clear()

        # Print Cities at the Given Region ID
        if not self.__cityTable.get(CITY_FK_REGION, regionId):
            raise RowNotFound(CITY_TABLENAME, CITY_FK_REGION, regionId)

        while True:
            try:
                # Select City ID
                cityId = IntPrompt.ask("\nSelect City ID")

                # Get City Object
                city = self.__cityTable.find(cityId)

                # Check if City ID Exists
                if city == None:
                    raise RowNotFound(CITY_TABLENAME, CITY_ID, cityId)

                elif city.regionId != regionId:
                    raise InvalidLocation(city.name, REGION_TABLENAME, regionId)

                return cityId

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    def getCityId(self) -> int:
        """
        Method to Select a City ID from its Remote Table

        :return: City ID at its Remote Table
        :rtype: int
        """

        # Get Region ID where the City is Located
        regionId = self.getRegionId()

        return self.__getCity(regionId)

    def getRegionBuildingCityId(self, regionId: int) -> int:
        """
        Method to Select a Building City ID from its Remote Table by Getting All of its Parent Location Given a Region ID

        :param int regionId: Region ID at its Remote Table where the Building is Located
        :return: Building City ID at its Remote Table
        :rtype: int
        """

        return self.__getCity(regionId)

    def getWarehouseId(self, cityId: int) -> int:
        """
        Method to Get Warehouse ID from its Remote Table by Printing the Tables, and Selecting the Row Warehouse ID, Given a City ID

        :param int cityId: City ID at its Remote Table where the Warehouse is Located
        :return: Warehouse ID at its Remote Table
        :rtype: int
        """

        # Clear Terminal
        clear()

        # Print Warehouses at the Given City ID
        if not self.__warehouseTable.get(BUILDING_FK_CITY, cityId):
            raise WarehouseNotFound(cityId)

        while True:
            try:
                # Select Warehouse ID
                buildingId = IntPrompt.ask("\nSelect Warehouse ID")

                # Get Warehouse Object
                warehouse = self.__warehouseTable.find(buildingId)

                # Check if Warehouse ID Exists
                if warehouse == None:
                    raise RowNotFound(WAREHOUSE_TABLENAME, WAREHOUSE_ID, buildingId)

                elif warehouse.cityId != cityId:
                    raise InvalidLocation(
                        warehouse.buildingName, CITY_TABLENAME, cityId
                    )

                return buildingId

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    def getBranchId(self, cityId: int) -> int:
        """
        Method to Get Branch ID from its Remote Table by Printing the Tables, and Selecting the Row Branch ID, Given a City ID

        :param int cityId: City ID at its Remote Table where the Branch is Located
        :return: Branch ID at its Remote Table
        :rtype: int
        """

        # Clear Terminal
        clear()

        # Print Branchs at the Given City ID
        if not self.__branchTable.get(BUILDING_FK_CITY, cityId):
            raise RowNotFound(BUILDING_TABLENAME, BUILDING_FK_CITY, cityId)

        while True:
            try:
                # Select Branch ID
                buildingId = IntPrompt.ask("\nSelect Branch ID")

                # Get Branch Object
                branch = self.__branchTable.find(buildingId)

                # Check if Branch ID Exists
                if branch == None:
                    raise RowNotFound(WAREHOUSE_TABLENAME, WAREHOUSE_ID, buildingId)

                elif branch.cityId != cityId:
                    raise InvalidLocation(branch.buildingName, CITY_TABLENAME, cityId)

                return buildingId

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    def _allHandler(self, tableName: str) -> None:
        """
        Handler of ``all`` Location-related Subcommand

        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        """

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(ALL_DESC_MSG)

        if tableName == COUNTRY_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Print Table
            self.__countryTable.all(sortBy, desc)

        elif tableName == PROVINCE_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    PROVINCE_ID,
                    PROVINCE_FK_COUNTRY,
                    PROVINCE_NAME,
                    PROVINCE_FK_AIR_FORWARDER,
                    PROVINCE_FK_OCEAN_FORWARDER,
                    PROVINCE_FK_WAREHOUSE,
                ],
            )

            # Print Table
            self.__provinceTable.all(sortBy, desc)

        elif tableName == REGION_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    REGION_ID,
                    REGION_FK_PROVINCE,
                    REGION_NAME,
                    REGION_FK_WAREHOUSE,
                ],
            )

            # Print Table
            self.__regionTable.all(sortBy, desc)

        elif tableName == CITY_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME, CITY_FK_WAREHOUSE],
            )

            # Print Table
            self.__cityTable.all(sortBy, desc)

        elif tableName == WAREHOUSE_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[WAREHOUSE_ID, BUILDING_NAME, BUILDING_FK_CITY],
            )

            # Print Table
            self.__warehouseTable.all(sortBy, desc)

        elif tableName == BRANCH_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    BRANCH_ID,
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BRANCH_ROUTE_DISTANCE,
                    BUILDING_NAME,
                    BUILDING_FK_CITY,
                ],
            )

            # Print Table
            self.__branchTable.all(sortBy, desc)

        # Press ENTER to Continue
        Prompt.ask(PRESS_ENTER)

    def _getHandler(self, tableName: str) -> None:
        """
        Handler of ``get`` Location-related Subcommand

        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        while True:
            try:
                if tableName == COUNTRY_TABLENAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == COUNTRY_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    self.__countryTable.get(field, value)

                elif tableName == PROVINCE_TABLENAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            PROVINCE_ID,
                            PROVINCE_FK_COUNTRY,
                            PROVINCE_NAME,
                            PROVINCE_FK_AIR_FORWARDER,
                            PROVINCE_FK_OCEAN_FORWARDER,
                            PROVINCE_FK_WAREHOUSE,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == PROVINCE_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    self.__provinceTable.get(field, value)

                elif tableName == REGION_TABLENAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            REGION_ID,
                            REGION_FK_PROVINCE,
                            REGION_NAME,
                            REGION_FK_WAREHOUSE,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == REGION_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    self.__regionTable.get(field, value)

                elif tableName == CITY_TABLENAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[CITY_ID, CITY_FK_REGION, CITY_NAME, CITY_FK_WAREHOUSE],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == CITY_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    self.__cityTable.get(field, value)

                elif tableName == WAREHOUSE_TABLENAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            WAREHOUSE_ID,
                            BUILDING_NAME,
                            BUILDING_PHONE,
                            BUILDING_FK_CITY,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == BUILDING_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    self.__warehouseTable.get(field, value)

                elif tableName == BRANCH_TABLENAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            BRANCH_ID,
                            BRANCH_FK_WAREHOUSE_CONNECTION,
                            BUILDING_NAME,
                            BUILDING_PHONE,
                            BUILDING_FK_CITY,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == BUILDING_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    self.__branchTable.get(field, value)

                if Confirm.ask("Do you want to Continue Searching for?"):
                    # Clear Terminal
                    clear()
                    continue

                break

            # Raise GoToMenu Error
            except GoToMenu as err:
                raise err

            # Go Back to the While-loop
            except (LocationNotFound, PlaceError) as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

    def _modHandler(self, tableName: str) -> None:
        """
        Handler of ``mod`` Location-related Subcommand

        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        """

        if tableName == COUNTRY_TABLENAME:
            # Select Country ID to Modify
            countryId = self.getCountryId()

            # Print Fetched Results
            if not self.__countryTable.get(COUNTRY_ID, countryId):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(MOD_FIELD_MSG, choices=[COUNTRY_PHONE_PREFIX])

            # Prompt to Ask the New Value
            if field == COUNTRY_PHONE_PREFIX:
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

            # Modify Country
            self.__countryTable.modify(countryId, field, value)

        elif tableName == PROVINCE_TABLENAME:
            # Select Province ID to Modify
            provinceId = self.getProvinceId()

            # Print Fetched Results
            if not self.__provinceTable.get(PROVINCE_ID, provinceId):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[
                    PROVINCE_FK_AIR_FORWARDER,
                    PROVINCE_FK_OCEAN_FORWARDER,
                    PROVINCE_FK_WAREHOUSE,
                ],
            )

            # Prompt to Ask the New Value
            if (
                field == PROVINCE_FK_AIR_FORWARDER
                or field == PROVINCE_FK_OCEAN_FORWARDER
            ):
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

                # TO DEVELOP: CHECK AND CONFIRM FORWARDERS

            elif field == PROVINCE_FK_WAREHOUSE:
                # Select Warehouse ID
                cityId = self.getProvinceBuildingCityId(provinceId)
                warehouseId = self.getWarehouseId(cityId)

                # Get Warehouse Dictionary from Warehouse ID
                warehouseDict = self.__getWarehouseDict(warehouseId)

                # Get Province Object
                province = self.__provinceTable.find(provinceId)

                # Check if there's a Main Warehouse
                if province.warehouseId != None:
                    currWarehouseId = province.warehouseId

                    # Drop Old Warehouse Connections with all the Main Province Warehouses at the Same Country and all the Main Region Warehouses at the Given Province
                    self.__warehouseConnTable.removeProvinceMainWarehouse(
                        provinceId, currWarehouseId
                    )

                # Get Province Country ID
                countryId = province.countryId

                # Add Warehouse Connections for the Current Warehouse with All the Main Province Warehouses at the Given Country and all the Main Region Warehouses at the Given Province
                self.__warehouseConnTable.insertProvinceMainWarehouse(
                    self.__ORSGeocoder, countryId, provinceId, warehouseDict
                )

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSE_ID]

            # Modify Province
            self.__provinceTable.modify(provinceId, field, value)

        elif tableName == REGION_TABLENAME:
            # Select Region ID to Modify
            regionId = self.getRegionId()

            # Print Fetched Results
            if not self.__regionTable.get(REGION_ID, regionId):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[REGION_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == REGION_FK_WAREHOUSE:
                # Select Warehouse ID
                cityId = self.getRegionBuildingCityId(regionId)
                warehouseId = self.getWarehouseId(cityId)

                # Get Warehouse Dictionary Fields from Warehouse ID
                warehouseDict = self.__getWarehouseDict(warehouseId)

                # Get Region Object
                region = self.__regionTable.find(regionId)

                # Check if there's a Main Warehouse
                if region.warehouseId != None:
                    currWarehouseId = region.warehouseId

                    # Drop Old Warehouse Connections with the Main Province Warehouse, all the Main Region Warehouses at the Same Province, and all the Main City Warehouses at the Given Region
                    self.__warehouseConnTable.removeRegionMainWarehouse(
                        regionId, currWarehouseId
                    )

                # Get Region Province ID
                provinceId = region.provinceId

                # Get Province Main Warehouse ID
                province = self.__provinceTable.find(provinceId)
                provinceWarehouseId = province.warehouseId

                # Get Province Warehouse Dictionary Fields from Province Warehouse ID
                provinceWarehouseDict = self.__getWarehouseDict(provinceWarehouseId)

                # Add Warehouse Connections for the Current Warehouse with the Main Province Warehouse, all the Main Region Warehouses at the Given Province and all the Main City Warehouses at the Given Region
                self.__warehouseConnTable.insertRegionMainWarehouse(
                    self.__ORSGeocoder,
                    provinceId,
                    regionId,
                    provinceWarehouseDict,
                    warehouseDict,
                )

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSE_ID]

            # Modify Region
            self.__regionTable.modify(regionId, field, value)

        elif tableName == CITY_TABLENAME:
            # Select City ID to Modify
            cityId = self.getCityId()

            # Print Fetched Results
            if not self.__cityTable.get(CITY_ID, cityId):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[CITY_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == CITY_FK_WAREHOUSE:
                # Select Warehouse ID
                warehouseId = self.getWarehouseId(cityId)

                # Get Warehouse Dictionary Fields from Warehouse ID
                warehouseDict = self.__getWarehouseDict(warehouseId)

                # Get City Object
                city = self.__cityTable.find(cityId)

                # Check if there's a Main Warehouse
                if city.warehouseId != None:
                    currWarehouseId = city.warehouseId

                    # Drop Old Warehouse Connections with the Main Region Warehouse, all the Main City Warehouses at the Same Region, and all the City Warehouses at the Given City
                    self.__warehouseConnTable.removeCityMainWarehouse(
                        cityId, currWarehouseId
                    )

                # Get City Region ID
                regionId = city.regionId

                # Get Region Main Warehouse ID
                region = self.__regionTable.find(regionId)
                regionWarehouseId = region.warehouseId

                # Get Region Warehouse Dictionary Fields from Region Warehouse ID
                regionWarehouseDict = self.__getWarehouseDict(regionWarehouseId)

                # Add Warehouse Connections for the Current Warehouse with the Main Region Warehouse, all the Main City Warehouses at the Given Region and all the City Warehouses at the Given City
                self.__warehouseConnTable.insertCityMainWarehouse(
                    self.__ORSGeocoder,
                    regionId,
                    cityId,
                    regionWarehouseDict,
                    warehouseDict,
                )

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSE_ID]

            # Modify City
            self.__cityTable.modify(regionId, field, value)

        elif tableName == WAREHOUSE_TABLENAME:
            # Select Warehouse ID
            cityId = self.getCityId()
            warehouseId = self.getWarehouseId(cityId)

            # Print Fetched Results
            if not self.__warehouseTable.get(WAREHOUSE_ID, warehouseId):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[BUILDING_NAME, BUILDING_PHONE, BUILDING_EMAIL],
            )

            # Prompt to Ask the New Value
            value = askBuildingValue(tableName, field)

            # Modify Warehouse
            self.__warehouseTable.modify(warehouseId, field, value)

        elif tableName == BRANCH_TABLENAME:
            # Select Branch ID
            branchId = self.getBranchId()

            # Print Fetched Results
            if not self.__branchTable.get(BRANCH_ID, branchId):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BUILDING_NAME,
                    BUILDING_PHONE,
                    BUILDING_EMAIL,
                ],
            )

            # Prompt to Ask the New Value
            if field != BRANCH_FK_WAREHOUSE_CONNECTION:
                value = askBuildingValue(tableName, field)

                # Modify Branch
                self.__branchTable.modify(branchId, field, value)

            else:
                # Get Branch Object
                branch = self.__branchTable.find(branchId)

                # Get City ID where the Branch is Located, and the Warehouse at the Given City
                cityId = branch.cityId
                warehouseId = self.getWarehouseId(cityId)

                # Get Branch Coordinates
                coords = {
                    NOMINATIM_LATITUDE: branch.gpsLatitude,
                    NOMINATIM_LONGITUDE: branch.gpsLongitude,
                }

                # Get Route Distance
                routeDistance = self.__getRouteDistance(warehouseId, coords)

                # Modify Branch
                self.__branchTable.modify(
                    branchId, BRANCH_FK_WAREHOUSE_CONNECTION, warehouseId
                )
                self.__branchTable.modify(
                    branchId, BRANCH_ROUTE_DISTANCE, routeDistance
                )

        # Press ENTER to Continue
        Prompt.ask(PRESS_ENTER)

    def _addHandler(self, tableName: str) -> None:
        """
        Handler of ``add`` Location-related Subcommand

        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        """

        while True:
            if tableName == COUNTRY_TABLENAME:
                # Get the Country Name to Insert
                location = self.getCountryName()
                if location == None:
                    return

                countryName = location[DICT_COUNTRY_NAME]

                # Ask for the Other Country Fields and Insert the Country to Its Table
                self.__countryTable.add(countryName)

                return

            elif tableName == PROVINCE_TABLENAME:
                # Get the Province Name to Insert and the Country ID where It's Located
                location = self.getProvinceName()
                if location == None:
                    return

                countryId = location[DICT_COUNTRY_ID]
                provinceName = location[DICT_PROVINCE_NAME]

                # Ask for the Other Province Fields and Insert the Province to Its Table
                self.__provinceTable.add(countryId, provinceName)

            elif tableName == REGION_TABLENAME:
                # Get the Region Name to Insert and the Province ID where It's Located
                location = self.getRegionName()
                if location == None:
                    return

                provinceId = location[DICT_PROVINCE_ID]
                regionName = location[DICT_REGION_NAME]

                # Ask for the Other Region Fields and Insert the Region to Its Table
                self.__regionTable.add(provinceId, regionName)

            elif tableName == CITY_TABLENAME:
                # Get the City Name to Insert and the Region ID where It's Located
                location = self.getCityName()
                if location == None:
                    return

                regionId = location[DICT_REGION_ID]
                cityName = location[DICT_CITY_NAME]

                # Ask for the Other City Fields and Insert the City to Its Table
                self.__cityTable.add(regionId, cityName)

            elif tableName == WAREHOUSE_TABLENAME or tableName == BRANCH_TABLENAME:
                # Get Building Coordinates
                location = self.getPlaceCoordinates()
                if location == None:
                    return

                # Get Building Name
                buildingName = Prompt.ask("Enter Building Name")

                # Check Building Name
                isAddressValid(tableName, BUILDING_NAME, buildingName)

                if tableName == WAREHOUSE_TABLENAME:
                    # Ask for the Other Warehouse Fields and Insert the Warehouse to Its Table
                    warehouseId = self.__warehouseTable.add(location, buildingName)

                    # Get Warehouse Dictionary
                    warehouseDict = self.__getWarehouseDict(warehouseId)
                    parentWarehouseDict = None

                    # Check if there's a Main Warehouse at the Province ID where It's Located
                    province = self.__provinceTable.find(location[DICT_PROVINCE_ID])

                    if province.warehouseId == None:
                        self.__warehouseConnTable.insertProvinceMainWarehouse(
                            self.__ORSGeocoder,
                            location[DICT_COUNTRY_ID],
                            location[DICT_PROVINCE_ID],
                            warehouseDict,
                        )
                        parentWarehouseDict = warehouseDict

                        # Set as Main Province Warehouse
                        self.__provinceTable.modify(
                            location[DICT_PROVINCE_ID],
                            PROVINCE_FK_WAREHOUSE,
                            warehouseId,
                        )

                    else:
                        parentWarehouseDict = self.__getWarehouseDict(
                            province.warehouseId
                        )

                    # Check if there's a Main Warehouse at the Region ID where It's Located
                    region = self.__regionTable.find(location[DICT_REGION_ID])

                    if region.warehouseId == None:
                        self.__warehouseConnTable.insertRegionMainWarehouse(
                            self.__ORSGeocoder,
                            location[DICT_PROVINCE_ID],
                            location[DICT_REGION_ID],
                            parentWarehouseDict,
                            warehouseDict,
                        )
                        parentWarehouseDict = warehouseDict

                        # Set as Main Region Warehouse
                        self.__regionTable.modify(
                            location[DICT_REGION_ID], REGION_FK_WAREHOUSE, warehouseId
                        )

                    else:
                        parentWarehouseDict = self.__getWarehouseDict(
                            region.warehouseId
                        )

                    # Check if there's a Main Warehouse at the City ID where It's Located
                    city = self.__cityTable.find(location[DICT_CITY_ID])

                    if city.warehouseId == None:
                        self.__warehouseConnTable.insertCityMainWarehouse(
                            self.__ORSGeocoder,
                            location[DICT_REGION_ID],
                            location[DICT_CITY_ID],
                            parentWarehouseDict,
                            warehouseDict,
                        )
                        parentWarehouseDict = warehouseDict

                        # Set as Main City Warehouse
                        self.__cityTable.modify(
                            location[DICT_CITY_ID], CITY_FK_WAREHOUSE, warehouseId
                        )

                    else:
                        parentWarehouseDict = self.__getWarehouseDict(city.warehouseId)

                        # Insert City Warehouse Connection
                        self.__warehouseConnTable.insertCityWarehouse(
                            self.__ORSGeocoder, parentWarehouseDict, warehouseDict
                        )

                elif tableName == BRANCH_TABLENAME:
                    # Get Warehouse at the Given City
                    warehouseId = self.getWarehouseId(location[DICT_CITY_ID])

                    # Get Route Distance
                    routeDistance = self.__getRouteDistance(warehouseId, location)

                    # Ask for the Other Branch Fields and Insert the Branch to Its Table
                    self.__branchTable.add(
                        location,
                        buildingName,
                        warehouseId,
                        routeDistance,
                    )

            # Ask to Add More
            if not Confirm.ask(ADD_MORE_MSG):
                break

            # Clear Terminal
            clear()

    def _rmHandler(self, tableName: str) -> None:
        """
        Handler of ``rm`` Location-related Subcommand

        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises MainWarehouseError: Raised if the Warehouse that's being Removed is Referenced as the Main One at Any Location Table
        """

        if tableName == COUNTRY_TABLENAME:
            # Select Country ID to Remove
            countryId = self.getCountryId()

            # Print Fetched Results
            if not self.__countryTable.get(COUNTRY_ID, countryId):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self.__countryTable.remove(countryId)

        elif tableName == PROVINCE_TABLENAME:
            # Select Province ID to Remove
            provinceId = self.getProvinceId()

            # Print Fetched Results
            if not self.__provinceTable.get(PROVINCE_ID, provinceId):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self.__provinceTable.remove(provinceId)

        elif tableName == REGION_TABLENAME:
            # Select Region ID to Remove
            regionId = self.getRegionId()

            # Print Fetched Results
            if not self.__regionTable.get(REGION_ID, regionId):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self.__regionTable.remove(regionId)

        elif tableName == CITY_TABLENAME:
            # Select City ID to Remove
            cityId = self.getCityId

            # Print Fetched Results
            if not self.__cityTable.get(CITY_ID, cityId):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self.__cityTable.remove(cityId)

        elif tableName == WAREHOUSE_TABLENAME:
            # Select Warehouse ID to Remove
            cityId = self.getCityId()
            warehouseId = self.getWarehouseId(cityId)

            # Print Fetched Results
            if not self.__warehouseTable.get(WAREHOUSE_ID, warehouseId):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            # Check if it's the Main Warehouse at Any Location
            location = self.__warehouseConnTable.isMainWarehouse(warehouseId)

            if location != None:
                locationTableName, locationId = location
                raise MainWarehouseError(locationTableName, locationId)

            else:
                # Remove City Warehouse Connections
                self.__warehouseConnTable.removeCityWarehouse(warehouseId)

                # Remove Warehouse
                self.__warehouseTable.remove(warehouseId)

        elif tableName == BRANCH_TABLENAME:
            # Select Branch ID to Remove
            cityId = self.getCityId()
            branchId = self.getWarehouseId(cityId)

            # Print Fetched Results
            if not self.__branchTable.get(BRANCH_ID, branchId):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self.__branchTable.remove(branchId)

        # Press ENTER to Continue
        Prompt.ask(PRESS_ENTER)

    def handler(self, action: str, tableName: str) -> None:
        """
        Main Handler of ``add``, ``all``, ``get``, ``mod`` and ``rm`` Location-related Subcommands

        :param str action: Location-related Command (``add``, ``all``, ``get``, ``mod`` or ``rm``)
        :param str tableName: Location-related Table Name at Remote Database
        :return: Nothing
        :rtype: NoneType
        """

        if action == ADD:
            self._addHandler(tableName)

        elif action == GET:
            self._getHandler(tableName)

        elif action == ALL:
            self._allHandler(tableName)

        elif action == MOD:
            self._modHandler(tableName)

        elif action == RM:
            self._rmHandler(tableName)

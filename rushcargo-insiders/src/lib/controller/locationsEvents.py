from rich.prompt import Prompt, IntPrompt, Confirm

from .constants import *
from .exceptions import (
    RowNotFound,
    EmptyTable,
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

from ..graph.constants import LAYOUT_CMDS
from ..graph.warehouses import rushWGraph, RushWGraph

from ..io.constants import (
    DB_ADD,
    DB_RM,
    DB_ALL,
    DB_GET,
    DB_MOD,
)
from ..io.exceptions import GoToMenu
from ..io.validator import *

from ..local_database.database import NominatimDatabase, NominatimTables

from ..model.database_tables import cancelTasks
from ..model.database_building import *
from ..model.database_connections import *
from ..model.database_territory import *

from ..terminal.clear import clear
from ..terminal.constants import *


def nothingToChange() -> None:
    """
    Function to Print a Message when a Row is Already Modified at a Given Table

    :return: Nothing
    :rtype: NoneType
    """

    console.print("Nothing to Change...", style="warning")

    # Press ENTER to Continue
    Prompt.ask(PRESS_ENTER)


class LocationsEventHandler:
    """
    Class that Handles the Locations Scheme-related Subcommands
    """

    # Table Classes
    __countriesTable = None
    __regionsTable = None
    __citiesTable = None
    __warehousesTable = None
    __warehouseConnsTable = None
    __branchesTable = None

    # Nominatim GeoPy Local Database Tables
    __localDatabase = None
    __localTables = None

    # Geocoders
    __nominatimGeocoder = None
    __ORSGeocoder = None

    # Get Location Messages
    __GET_COUNTRY_MSG = "Enter Country Name"
    __GET_REGION_MSG = "Enter Region Name"
    __GET_CITY_MSG = "Enter City Name"

    # Constructor
    def __init__(self, user: str, ORSApiKey: str):
        """
        Location Event Handler Class Constructor

        :param str user: Remote Database Role Name
        :param str ORSApiKey: Open Routing Service API Key
        """

        # Initialize Table Classes
        self.__countriesTable = CountriesTable()
        self.__regionsTable = RegionsTable()
        self.__citiesTable = CitiesTable()
        self.__warehouseConnsTable = WarehouseConnectionsTable()
        """
        self.__warehousesTable = WarehousesTable()
        self.__branchesTable = BranchesTable()
        """

        # Initialize Nominatim GeoPy Local Database and Get Connection and Cursor
        self.__localDatabase = NominatimDatabase()
        localConnection = self.__localDatabase.getConnection()
        localCursor = self.__localDatabase.getCursor()

        # Initialize Local Nominatim GeoPy Database Tables Class
        self.__localTables = NominatimTables(localConnection, localCursor)

        # Initialize Nominatim GeoPy and RoutingPy Geocoders
        self.__nominatimGeocoder = NominatimGeocoder(user)
        self.__ORSGeocoder = ORSGeocoder(ORSApiKey, user)

    async def __getRouteDistance(
        self, aconn, warehouseId: int, locationCoords: dict
    ) -> int:
        """
        Asynchronous Method to Get the Route Distance between a Warehouse and a Given Location

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int warehouseId: Warehouse ID at its Remote Table
        :param dict location: Dictionary that Contains the Coordinates for a Given Place
        :return: Route Distance between the Warehouse and the Given Location
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Warehouse Object
        findTask = asyncio.create_task(self.__warehousesTable.find(aconn, warehouseId))
        await asyncio.gather(findTask)
        warehouse = findTask.result()

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

    async def __getWarehouseDict(self, aconn, warehouseId: int) -> dict:
        """
        Method to Get a Valid Warehouse Dictionary to be Used by a Warehouse-related Table Class

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int warehouseId: Warehouse ID at its Remote Table
        :return: Warehouse Dictionary that Contains its Building ID and its Coordinates
        :rtype: dict
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Warehouse Object
        findTask = asyncio.create_task(self.__warehousesTable.find(aconn, warehouseId))
        await asyncio.gather(findTask)
        warehouse = findTask.result()

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
                isAddressValid(COUNTRIES_TABLE_NAME, COUNTRIES_NAME, countrySearch)

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

    async def getCountryDict(self, aconn) -> dict:
        """
        Asynchronous Method to Get Country ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: A Dictionary that Contains the Country ID from its Remote Table, and the Columns that were Inserted at ``self.getCountryName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Location Dictionary (that Contains the Country Name) to Search for it in its Table
        location = self.getCountryName()
        countryName = location[DICT_COUNTRY_NAME]

        # Get Country Object from the Remote Database
        findTask = asyncio.create_task(
            self.__countriesTable.find(aconn, COUNTRIES_NAME, countryName)
        )
        await asyncio.gather(findTask)
        c = findTask.result()

        # Check if the Country Name is Stored at the Remote Database
        if c == None:
            # Clear Terminal
            clear()

            # Insert Country
            await asyncio.gather(self.__countriesTable.add(aconn, countryName))

            # Get Country Object from the Remote Database
            findTask = asyncio.create_task(
                self.__countriesTable.find(aconn, COUNTRIES_NAME, countryName)
            )
            await asyncio.gather(findTask)
            c = findTask.result()

        # Set Country ID to Data Dictionary
        location[DICT_COUNTRY_ID] = c.countryId

        return location

    async def getRegionName(self, aconn) -> dict | None:
        """
        Asynchronous Method to Search for a Region Name in the Local Database

        :return: A Dictionary that Contains the Region Name and its ID from its Local SQLite Table, and the Columns that were Inserted at ``self.getCountryDict()`` Call if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Location Dictionary (that Contains the Country Name and its ID in the Local SQLite and Remote Database)
        getTask = asyncio.create_task(self.getCountryDict(aconn))
        await asyncio.gather(getTask)
        location = getTask.result()

        while True:
            try:
                regionSearch = Prompt.ask(self.__GET_REGION_MSG)

                # Check Region Name
                isAddressValid(REGIONS_TABLE_NAME, REGIONS_NAME, regionSearch)

                # Check if the Search is Stored in the Local Database
                regionNameId = self.__localTables.getRegionSearchNameId(
                    location[DICT_COUNTRY_NAME_ID], regionSearch
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
                        location[DICT_COUNTRY_NAME_ID], regionSearch, regionName
                    )

                    # Get Region Name ID from Local Database
                    location[DICT_REGION_NAME_ID] = self.__localTables.getRegionNameId(
                        location[DICT_COUNTRY_NAME_ID], regionName
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

    async def getRegionDict(self, aconn) -> dict:
        """
        Asynchronous Method to Get Region ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: A Dictionary that Contains the Region ID from its Remote Table, and the Columns that were Inserted at ``self.getRegionName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Location Dictionary (that Contains the Region Name) to Search for it in its Table
        getTask = asyncio.create_task(self.getRegionName(aconn))
        await asyncio.gather(getTask)
        location = getTask.result()
        countryId = location[DICT_COUNTRY_ID]
        regionName = location[DICT_REGION_NAME]

        # Get Region Object from the Remote Database
        findMultTask = asyncio.create_task(
            self.__regionsTable.findMult(aconn, countryId, regionName)
        )
        await asyncio.gather(findMultTask)
        r = findMultTask.result()

        # Check if the Region Name at the Given Country ID is Stored at the Remote Database
        if r == None:
            # Clear Terminal
            clear()

            # Insert Region
            await asyncio.gather(self.__regionsTable.add(aconn, countryId, regionName))

            # Get Region Object from the Remote Database
            findMultTask = asyncio.create_task(
                self.__regionsTable.findMult(aconn, countryId, regionName)
            )
            await asyncio.gather(findMultTask)
            r = findMultTask.result()

        # Set Region ID to Data Dictionary
        location[DICT_REGION_ID] = r.regionId

        return location

    async def getCityName(self, aconn) -> dict | None:
        """
        Asynchronous Method to Search for a City Name in the Local Database

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: A Dictionary that Contains the City Name and its ID from its Local SQLite Table, and the Columns that were Inserted at ``self.getRegionDict()`` Call if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Location Dictionary (that Contains the Region Name and its ID in the Local SQLite and Remote Database)
        getTask = asyncio.create_task(self.getRegionDict(aconn))
        await asyncio.gather(getTask)
        location = getTask.result()

        while True:
            try:
                citySearch = Prompt.ask(self.__GET_CITY_MSG)

                # Check City Name
                isAddressValid(CITIES_TABLE_NAME, CITIES_NAME, citySearch)

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

    async def getCityDict(self, aconn) -> dict:
        """
        Asynchronous Method to Get City ID and Name from its Remote Table. If Found, Returns a Dictionary with its Info. Otherwise, raise a GoToMenu Exception

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: A Dictionary that Contains the City ID from its Remote Table, and the Columns that were Inserted at ``self.getCityName()`` Call
        :rtype: dict
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Location Dictionary (that Contains the City Name) to Search for it in its Table
        getTask = asyncio.create_task(self.getCityName(aconn))
        await asyncio.gather(getTask)
        location = getTask.result()
        regionId = location[DICT_REGION_ID]
        cityName = location[DICT_CITY_NAME]

        # Get City Object from the Remote Database
        findMultTask = asyncio.create_task(
            self.__citiesTable.findMult(aconn, regionId, cityName)
        )
        await asyncio.gather(findMultTask)
        c = findMultTask.result()

        # Check if the City Name at the Given Region ID is Stored at the Remote Database
        if c == None:
            # Clear Terminal
            clear()

            # Insert City
            await asyncio.gather(self.__citiesTable.add(aconn, regionId, cityName))

            # Get City Object from the Remote Database
            findMultTask = asyncio.create_task(
                self.__citiesTable.findMult(aconn, regionId, cityName)
            )
            await asyncio.gather(findMultTask)
            c = findMultTask.result()

        # Set City ID to Data Dictionary
        location[DICT_CITY_ID] = c.cityId

        return location

    async def getPlaceCoordinates(self, aconn) -> dict | None:
        """
        Asynchronous Method to Get Place Coordinates in a Given City ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: A Dictionary that Contains the City ID from its Remote Table, and the Latitude and Longitude of the Given Place Obtained through the ``self.__nominatimGeocoder`` Object if there's no Error. Otherwise, if the User wants, It'll return ``None`` and Go Back to the Main Menu
        :rtype: dict if there's no Error. Otherwise, None
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Location Dictionary (that Contains the City ID)
        getTask = asyncio.create_task(self.getCityDict(aconn))
        await asyncio.gather(getTask)
        location = getTask.result()

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

    async def __getCountry(self, aconn) -> int:
        """
        Asynchronous Method to Get Country ID from its Remote Table by Printing the Tables, and Selecting the Row Country ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: Country ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Print All Countries
        allTask = asyncio.create_task(
            self.__countriesTable.all(aconn, COUNTRIES_NAME, False)
        )
        await asyncio.gather(allTask)
        countriesList = allTask.result()

        if countriesList == None:
            raise EmptyTable(COUNTRIES_TABLE_NAME)

        while True:
            try:
                # Select Country ID
                countryId = IntPrompt.ask("\nSelect Country ID")

                # Check if Country ID Exists
                for c in countriesList:
                    if c.countryId == countryId:
                        return countryId

                raise RowNotFound(COUNTRIES_TABLE_NAME, COUNTRIES_ID, countryId)

            except Exception as err:
                console.print(err, style="warning")
                continue

    async def getCountryId(self, aconn) -> int:
        """
        Asynchronous Method to Select a Country ID from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: Country ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        getTask = asyncio.create_task(self.__getCountry(aconn))
        await asyncio.gather(getTask)

        return getTask.result()

    async def __getRegion(self, aconn, countryId: int) -> int:
        """
        Asynchronous Method to Get Region ID from its Remote Table by Printing the Tables, and Selecting the Row Region ID, Given a Country ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID at its Remote Table where the Region is Located
        :return: Region ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Print Regions at the Given Country ID
        getTask = asyncio.create_task(
            self.__regionsTable.get(aconn, REGIONS_FK_COUNTRY, countryId, True)
        )
        await asyncio.gather(getTask)
        regionsList = getTask.result()

        if regionsList == None:
            raise RowNotFound(REGIONS_TABLE_NAME, REGIONS_FK_COUNTRY, countryId)

        while True:
            try:
                # Select Region ID
                regionId = IntPrompt.ask("\nSelect Region ID")

                # Check if Region ID Exists
                for r in regionsList:
                    if r.regionId == regionId:
                        return regionId

                raise RowNotFound(REGIONS_TABLE_NAME, REGIONS_ID, regionId)

            except Exception as err:
                console.print(err, style="warning")
                continue

    async def getRegionId(self, aconn) -> int:
        """
        Asynchronous Method to Select a Region ID from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: Region ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Country ID where the Region is Located
        getCountryTask = asyncio.create_task(self.getCountryId(aconn))
        await asyncio.gather(getCountryTask)
        countryId = getCountryTask.result()

        getCityTask = asyncio.create_task(self.__getRegion(aconn, countryId))
        await asyncio.gather(getCityTask)

        return getCityTask.result()

    async def __getCity(self, aconn, regionId: int) -> int:
        """
        Asynchronous Method to Get City ID from its Remote Table by Printing the Tables, and Selecting the Row City ID, Given a Region ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID at its Remote Table where the City is Located
        :return: City ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Print Cities at the Given Region ID
        getTask = asyncio.create_task(
            self.__citiesTable.get(aconn, CITIES_FK_REGION, regionId)
        )
        await asyncio.gather(getTask)
        citiesList = getTask.result()

        if citiesList == None:
            raise RowNotFound(CITIES_TABLE_NAME, CITIES_FK_REGION, regionId)

        while True:
            try:
                # Select City ID
                cityId = IntPrompt.ask("\nSelect City ID")

                # Check if City ID Exists
                for c in citiesList:
                    if c.cityId == cityId:
                        return cityId

                raise RowNotFound(CITIES_TABLE_NAME, CITIES_ID, cityId)

            except Exception as err:
                console.print(err, style="warning")
                continue

    async def getCityId(self, aconn) -> int:
        """
        Asynchronous Method to Select a City ID from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :return: City ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Region ID where the City is Located
        getRegionTask = asyncio.create_task(self.getRegionId(aconn))
        await asyncio.gather(getRegionTask)
        regionId = getRegionTask.result()

        getCityTask = asyncio.create_task(self.__getCity(aconn, regionId))
        await asyncio.gather(getCityTask)

        return getCityTask.result()

    async def getRegionBuildingCityId(self, aconn, regionId: int) -> int:
        """
        Asynchronous Method to Select a Building City ID from its Remote Table by Getting All of its Parent Location Given a Region ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID at its Remote Table where the Building is Located
        :return: Building City ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        getTask = asyncio.create_task(self.__getCity(aconn, regionId))
        await asyncio.gather(getTask)

        return getTask.result()

    async def getWarehouseId(self, aconn, cityId: int) -> int:
        """
        Asynchronous Method to Get Warehouse ID from its Remote Table by Printing the Tables, and Selecting the Row Warehouse ID, Given a City ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID at its Remote Table where the Warehouse is Located
        :return: Warehouse ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Print Warehouses at the Given City ID
        getTask = asyncio.create_task(
            self.__warehousesTable.get(aconn, BUILDINGS_FK_CITY, cityId)
        )
        await asyncio.gather(getTask)
        warehousesList = getTask.result()

        if warehousesList == None:
            raise WarehouseNotFound(cityId)

        while True:
            try:
                # Select Warehouse ID
                buildingId = IntPrompt.ask("\nSelect Warehouse ID")

                # Check if Building ID Exists
                for w in warehousesList:
                    if w.buildingId == buildingId:
                        return buildingId

                raise RowNotFound(WAREHOUSES_TABLE_NAME, WAREHOUSES_ID, buildingId)

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    async def getBranchId(self, aconn, cityId: int) -> int:
        """
        Asynchronous Method to Get Branch ID from its Remote Table by Printing the Tables, and Selecting the Row Branch ID, Given a City ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID at its Remote Table where the Branch is Located
        :return: Branch ID at its Remote Table
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Print Branches at the Given City ID
        getTask = asyncio.create_task(
            self.__branchesTable.get(aconn, BUILDINGS_FK_CITY, cityId)
        )
        await asyncio.gather(getTask)
        branchesList = getTask.result()

        if branchesList == None:
            raise RowNotFound(BUILDINGS_TABLE_NAME, BUILDINGS_FK_CITY, cityId)

        while True:
            try:
                # Select Branch ID
                buildingId = IntPrompt.ask("\nSelect Branch ID")

                # Check if Building ID Exists
                for b in branchesList:
                    if b.buildingId == buildingId:
                        return buildingId

                raise RowNotFound(BRANCHES_TABLE_NAME, BRANCHES_ID, buildingId)

            except Exception as err:
                console.print(err, style="warning")

                # Press ENTER to Continue
                Prompt.ask(PRESS_ENTER)

                # Clear Terminal
                clear()

                continue

    async def _allHandler(self, aconn, tableName: str) -> None:
        """
        Asynchronous Handler of ``all`` Location-related Subcommand

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(ALL_DESC_MSG)

        if tableName == COUNTRIES_TABLE_NAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[COUNTRIES_ID, COUNTRIES_NAME, COUNTRIES_PHONE_PREFIX],
            )

            # Print Table
            await asyncio.gather(self.__countriesTable.all(aconn, sortBy, desc))

        elif tableName == REGIONS_TABLE_NAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    REGIONS_ID,
                    REGIONS_FK_COUNTRY,
                    REGIONS_NAME,
                    REGIONS_FK_WAREHOUSE,
                ],
            )

            # Print Table
            await asyncio.gather(self.__regionsTable.all(aconn, sortBy, desc))

        elif tableName == CITIES_TABLE_NAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[CITIES_ID, CITIES_FK_REGION, CITIES_NAME, CITIES_FK_WAREHOUSE],
            )

            # Print Table
            await asyncio.gather(self.__citiesTable.all(aconn, sortBy, desc))

        elif tableName == WAREHOUSES_TABLE_NAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[WAREHOUSES_ID, BUILDINGS_NAME, BUILDINGS_FK_CITY],
            )

            # Print Table
            await asyncio.gather(self.__warehousesTable.all(sortBy, desc))

        elif tableName == BRANCHES_TABLE_NAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    BRANCHES_ID,
                    BRANCHES_FK_WAREHOUSE_CONNECTION,
                    BRANCHES_ROUTE_DISTANCE,
                    BUILDINGS_NAME,
                    BUILDINGS_FK_CITY,
                ],
            )

            # Print Table
            await asyncio.gather(self.__branchesTable.all(sortBy, desc))

        # Press ENTER to Continue
        Prompt.ask(PRESS_ENTER)

    async def _getHandler(self, aconn, tableName: str) -> None:
        """
        Asynchronous Handler of ``get`` Location-related Subcommand

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        while True:
            try:
                if tableName == COUNTRIES_TABLE_NAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[COUNTRIES_ID, COUNTRIES_NAME, COUNTRIES_PHONE_PREFIX],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == COUNTRIES_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    await asyncio.gather(self.__countriesTable.get(aconn, field, value))

                elif tableName == REGIONS_TABLE_NAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            REGIONS_ID,
                            REGIONS_FK_COUNTRY,
                            REGIONS_NAME,
                            REGIONS_FK_AIR_FORWARDER,
                            REGIONS_FK_OCEAN_FORWARDER,
                            REGIONS_FK_WAREHOUSE,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == REGIONS_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    await asyncio.gather(self.__regionsTable.get(aconn, field, value))

                elif tableName == CITIES_TABLE_NAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            CITIES_ID,
                            CITIES_FK_REGION,
                            CITIES_NAME,
                            CITIES_FK_WAREHOUSE,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == CITIES_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    await asyncio.gather(self.__citiesTable.get(aconn, field, value))

                elif tableName == WAREHOUSES_TABLE_NAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            WAREHOUSES_ID,
                            BUILDINGS_NAME,
                            BUILDINGS_PHONE,
                            BUILDINGS_FK_CITY,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == BUILDINGS_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    await asyncio.gather(
                        self.__warehousesTable.get(aconn, field, value)
                    )

                elif tableName == BRANCHES_TABLE_NAME:
                    # Asks for Field to Compare
                    field = Prompt.ask(
                        GET_FIELD_MSG,
                        choices=[
                            BRANCHES_ID,
                            BRANCHES_FK_WAREHOUSE_CONNECTION,
                            BUILDINGS_NAME,
                            BUILDINGS_PHONE,
                            BUILDINGS_FK_CITY,
                        ],
                    )

                    # Prompt to Ask the Value to be Compared
                    if field == BUILDINGS_NAME:
                        value = Prompt.ask(GET_VALUE_MSG)

                        isAddressValid(tableName, field, value)

                    else:
                        value = str(IntPrompt.ask(GET_VALUE_MSG))

                    # Print Table Coincidences
                    await asyncio.gather(self.__branchesTable.get(aconn, field, value))

                if Confirm.ask("Do you want to Continue Searching?"):
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

    async def _modHandler(self, aconn, tableName: str) -> None:
        """
        Asynchronous Handler of ``mod`` Location-related Subcommand

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        if tableName == COUNTRIES_TABLE_NAME:
            # Select Country ID to Modify
            getTask = asyncio.create_task(self.getCountryId(aconn))
            await asyncio.gather(getTask)
            countryId = getTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__countriesTable.get(aconn, COUNTRIES_ID, countryId)
                )
                == None
            ):
                noCoincidence()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(MOD_FIELD_MSG, choices=[COUNTRIES_PHONE_PREFIX])

            # Prompt to Ask the New Value
            if field == COUNTRIES_PHONE_PREFIX:
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

            # Modify Country
            await asyncio.gather(
                self.__countriesTable.modify(aconn, countryId, field, value)
            )

        elif tableName == REGIONS_TABLE_NAME:
            # Select Region ID to Modify
            getTask = asyncio.create_task(self.getRegionId(aconn))
            await asyncio.gather(getTask)
            regionId = getTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__regionsTable.get(aconn, REGIONS_ID, regionId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[
                    REGIONS_FK_AIR_FORWARDER,
                    REGIONS_FK_OCEAN_FORWARDER,
                    REGIONS_FK_WAREHOUSE,
                ],
            )

            # Prompt to Ask the New Value
            if field == REGIONS_FK_AIR_FORWARDER or field == REGIONS_FK_OCEAN_FORWARDER:
                value = str(IntPrompt.ask(MOD_VALUE_MSG))

                # TO DEVELOP: CHECK AND CONFIRM FORWARDERS

            elif field == REGIONS_FK_WAREHOUSE:
                # Select Warehouse ID
                getTask = asyncio.create_task(
                    self.getRegionBuildingCityId(aconn, regionId)
                )
                await asyncio.gather(getTask)
                cityId = getTask.result()

                warehouseIdTask = asyncio.create_task(
                    self.getWarehouseId(aconn, cityId)
                )

                # Get Region Object
                regionTask = asyncio.create_task(
                    self.__regionsTable.find(aconn, regionId)
                )

                tasks = [warehouseIdTask, regionTask]
                try:
                    await asyncio.gather(*tasks)

                except Exception as err:
                    cancelTasks(tasks)
                    raise err

                warehouseId = warehouseIdTask.result()
                region = regionTask.result()

                # Check if there's a Main Warehouse
                currWarehouseId = region.warehouseId

                if warehouseId == currWarehouseId:
                    nothingToChange()
                    return

                warehouseDictTask = None

                async with asyncio.TaskGroup() as tg:
                    # Remove the Old Region Main Warehouse from the Region Table
                    tg.create_task(
                        self.__regionsTable.modify(
                            aconn, regionId, REGIONS_FK_WAREHOUSE, None
                        )
                    )

                    # Drop Old Warehouse Connections with all the Main Region Warehouses at the Same Country and all thMain Region Warehouses at the Given Region
                    tg.create_task(
                        self.__warehouseConnsTable.removeRegionMainWarehouse(
                            aconn.acursor(), regionId, currWarehouseId
                        )
                    )

                    # Get Warehouse Dictionary from Warehouse ID
                    getTask = asyncio.create_task(
                        self.__getWarehouseDict(aconn, warehouseId)
                    )
                    await asyncio.gather(getTask)
                    warehouseDictTask = getTask.result()

                # Get Region Country ID
                countryId = region.countryId

                warehouseDict = warehouseDictTask.result()

                # Add Warehouse Connections for the Current Warehouse with All the Main Region Warehouses at theGiven Country and all the Main Region Warehouses at the Given Region
                await asyncio.gather(
                    self.__warehouseConnsTable.insertRegionMainWarehouse(
                        aconn.acursor(),
                        self.__ORSGeocoder,
                        countryId,
                        regionId,
                        warehouseDict,
                    )
                )

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSE_ID]

            # Modify Region
            await asyncio.gather(
                self.__regionsTable.modify(aconn, regionId, field, value)
            )

        elif tableName == CITIES_TABLE_NAME:
            # Select City ID to Modify
            getTask = asyncio.create_task(self.getCityId(aconn))
            await asyncio.gather(getTask)
            cityId = getTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(self.__citiesTable.get(aconn, CITIES_ID, cityId))
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[CITIES_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == CITIES_FK_WAREHOUSE:
                # Select Warehouse ID
                warehouseIdTask = asyncio.create_task(
                    self.getWarehouseId(aconn, cityId)
                )

                # Get City Object
                cityTask = asyncio.create_task(self.__citiesTable.find(cityId))

                tasks = [warehouseIdTask, cityTask]
                try:
                    await asyncio.gather(*tasks)

                except Exception as err:
                    cancelTasks(tasks)
                    raise err

                warehouseId = warehouseIdTask.result()
                city = cityTask.result()

                # Get City Region ID
                regionId = city.regionId

                # Check if there's a Main Warehouse
                currWarehouseId = city.warehouseId

                if warehouseId == currWarehouseId:
                    nothingToChange()
                    return

                regionTask = warehouseDictTask = None

                async with asyncio.TaskGroup() as tg:
                    # Remove the Old City Main Warehouse from the City Table
                    tg.create_task(
                        self.__citiesTable.modify(
                            aconn, cityId, CITIES_FK_WAREHOUSE, None
                        )
                    )

                    # Drop Old Warehouse Connections with the Main Region Warehouse, all the Main City Warehouses at theSame Region, and all the City Warehouses at the Given City
                    tg.create_task(
                        self.__warehouseConnsTable.removeCityMainWarehouse(
                            aconn.acursor(), regionId, cityId, currWarehouseId
                        )
                    )

                    # Get Region Main Warehouse ID
                    regionTask = asyncio.create_task(
                        self.__regionsTable.find(aconn, regionId)
                    )

                    # Get Warehouse Dictionary Fields from Warehouse ID
                    warehouseDictTask = asyncio.create_task(
                        self.__getWarehouseDict(aconn, warehouseId)
                    )

                    tasks = [regionTask, warehouseDictTask]
                    try:
                        await asyncio.gather(*tasks)

                    except Exception as err:
                        cancelTasks(tasks)
                        raise err

                region = regionTask.result()
                regionWarehouseId = region.warehouseId

                # Get Region Warehouse Dictionary Fields from Region Warehouse ID
                regionWarehouseDictTask = asyncio.create_task(
                    self.__getWarehouseDict(regionWarehouseId)
                )
                await asyncio.gather(regionWarehouseDictTask)

                warehouseDict = warehouseDictTask.result()
                regionWarehouseDict = regionWarehouseDictTask.result()

                # Add Warehouse Connections for the Current Warehouse with the Main Region Warehouse, all the MainCity Warehouses at the Given Region and all the City Warehouses at the Given City
                await asyncio.gather(
                    self.__warehouseConnsTable.insertCityMainWarehouse(
                        aconn.acursor(),
                        self.__ORSGeocoder,
                        regionId,
                        cityId,
                        regionWarehouseDict,
                        warehouseDict,
                    )
                )

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSE_ID]

            # Modify City
            await asyncio.gather(self.__citiesTable.modify(aconn, cityId, field, value))

        elif tableName == WAREHOUSES_TABLE_NAME:
            # Select Warehouse ID
            getCityTask = asyncio.create_task(self.getCityId(aconn))
            await asyncio.gather(getCityTask)
            cityId = getCityTask.result()
            getWarehouseTask = asyncio.create_task(self.getWarehouseId(aconn, cityId))
            await asyncio.gather(getWarehouseTask)
            warehouseId = getWarehouseTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__warehousesTable.get(aconn, WAREHOUSES_ID, warehouseId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[BUILDINGS_NAME, BUILDINGS_PHONE, BUILDINGS_EMAIL],
            )

            # Prompt to Ask the New Value
            value = askBuildingValue(tableName, field)

            # Modify Warehouse
            await asyncio.gather(
                self.__warehousesTable.modify(aconn, warehouseId, field, value)
            )

        elif tableName == BRANCHES_TABLE_NAME:
            # Select Branch ID
            getCityTask = asyncio.create_task(self.getCityId(aconn))
            await asyncio.gather(getCityTask)
            cityId = getCityTask.result()
            getBranchTask = asyncio.create_task(self.getBranchId(aconn, cityId))
            await asyncio.gather(getBranchTask)
            branchId = getBranchTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__branchesTable.get(aconn, BRANCHES_ID, branchId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[
                    BRANCHES_FK_WAREHOUSE_CONNECTION,
                    BUILDINGS_NAME,
                    BUILDINGS_PHONE,
                    BUILDINGS_EMAIL,
                ],
            )

            # Prompt to Ask the New Value
            if field != BRANCHES_FK_WAREHOUSE_CONNECTION:
                value = askBuildingValue(tableName, field)

                # Modify Branch
                await asyncio.gather(
                    self.__branchesTable.modify(aconn, branchId, field, value)
                )

            else:
                # Get Branch Object
                findBranchTask = asyncio.create_task(
                    self.__branchesTable.find(aconn, branchId)
                )
                await asyncio.gather(findBranchTask)
                branch = findBranchTask.result()

                # Get City ID where the Branch is Located, and the Warehouse at the Given City
                cityId = branch.cityId
                getWarehouseTask = asyncio.create_task(
                    self.getWarehouseId(aconn, cityId)
                )
                await asyncio.gather(getWarehouseTask)
                warehouseId = getWarehouseTask.result()

                # Get Branch Coordinates
                coords = {
                    NOMINATIM_LATITUDE: branch.gpsLatitude,
                    NOMINATIM_LONGITUDE: branch.gpsLongitude,
                }

                # Modify Branch
                modWarehouseTask = asyncio.create_task(
                    self.__branchesTable.modify(
                        aconn, branchId, BRANCHES_FK_WAREHOUSE_CONNECTION, warehouseId
                    )
                )

                # Get Route Distance
                getRouteTask = asyncio.create_task(
                    self.__getRouteDistance(aconn, warehouseId, coords)
                )
                await asyncio.gather(getRouteTask)
                routeDistance = getRouteTask.result()

                modRouteTask = asyncio.create_task(
                    self.__branchesTable.modify(
                        aconn, branchId, BRANCHES_ROUTE_DISTANCE, routeDistance
                    )
                )

                tasks = [modWarehouseTask, modRouteTask]
                try:
                    await asyncio.gather(*tasks)

                except Exception as err:
                    cancelTasks(tasks)
                    raise err

        # Press ENTER to Continue
        Prompt.ask(PRESS_ENTER)

    async def _addHandler(self, aconn, tableName: str) -> None:
        """
        Asynchronous Handler of ``add`` Location-related Subcommand

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        while True:
            if tableName == COUNTRIES_TABLE_NAME:
                # Get the Country Name to Insert
                location = self.getCountryName()
                if location == None:
                    return

                countryName = location[DICT_COUNTRY_NAME]

                # Ask for the Other Country Fields and Insert the Country to Its Table
                await asyncio.gather(self.__countriesTable.add(aconn, countryName))

                return

            elif tableName == REGIONS_TABLE_NAME:
                # Get the Region Name to Insert and the Country ID where It's Located
                getTask = asyncio.create_task(self.getRegionName(aconn))
                await asyncio.gather(getTask)
                location = getTask.result()
                if location == None:
                    return

                provinceId = location[DICT_COUNTRY_ID]
                regionName = location[DICT_REGION_NAME]

                # Ask for the Other Region Fields and Insert the Region to Its Table
                await asyncio.gather(
                    self.__regionsTable.add(aconn, provinceId, regionName)
                )

            elif tableName == CITIES_TABLE_NAME:
                # Get the City Name to Insert and the Region ID where It's Located
                getTask = asyncio.create_task(self.getCityName(aconn))
                await asyncio.gather(getTask)
                location = getTask.result()
                if location == None:
                    return

                regionId = location[DICT_REGION_ID]
                cityName = location[DICT_CITY_NAME]

                # Ask for the Other City Fields and Insert the City to Its Table
                await asyncio.gather(self.__citiesTable.add(aconn, regionId, cityName))

            elif tableName == WAREHOUSES_TABLE_NAME or tableName == BRANCHES_TABLE_NAME:
                # Get Building Coordinates
                getTask = asyncio.create_task(self.getPlaceCoordinates(aconn))
                await asyncio.gather(getTask)
                location = getTask.result()
                if location == None:
                    return

                # Get Building Name
                buildingName = Prompt.ask("Enter Building Name")

                # Check Building Name
                isAddressValid(tableName, BUILDINGS_NAME, buildingName)

                if tableName == WAREHOUSES_TABLE_NAME:
                    # Ask for the Other Warehouse Fields and Insert the Warehouse to Its Table
                    insertTask = asyncio.create_task(
                        self.__warehousesTable.add(aconn, location, buildingName)
                    )

                    # Get Warehouse Dictionary
                    warehouseDictTask = asyncio.create_task(
                        self.__getWarehouseDict(aconn, warehouseId)
                    )

                    # Check if there's a Main Warehouse at the Region ID where It's Located
                    regionTask = asyncio.create_task(
                        self.__regionsTable.find(aconn, location[DICT_REGION_ID])
                    )

                    tasks = [insertTask, warehouseDictTask, regionTask]
                    try:
                        await asyncio.gather(*tasks)

                    except Exception as err:
                        cancelTasks(tasks)
                        raise err

                    warehouseId = insertTask.result()
                    warehouseDict = warehouseDictTask.result()
                    region = regionTask.result()

                    parentWarehouseDict = None

                    async with asyncio.TaskGroup() as tg:
                        if region.warehouseId == None:
                            tg.create_task(
                                self.__warehouseConnsTable.insertRegionMainWarehouse(
                                    aconn.acursor(),
                                    self.__ORSGeocoder,
                                    location[DICT_COUNTRY_ID],
                                    location[DICT_REGION_ID],
                                    warehouseDict,
                                )
                            )
                            parentWarehouseDict = warehouseDict

                            # Set as Main Region Warehouse
                            tg.create_task(
                                self.__regionsTable.modify(
                                    aconn,
                                    location[DICT_REGION_ID],
                                    REGIONS_FK_WAREHOUSE,
                                    warehouseId,
                                )
                            )

                        else:
                            getTask = asyncio.create_task(
                                self.__getWarehouseDict(aconn, region.warehouseId)
                            )
                            await asyncio.gather(getTask)
                            parentWarehouseDict = getTask.result()

                        # Check if there's a Main Warehouse at the City ID where It's Located
                        findTask = asyncio.create_task(
                            self.__citiesTable.find(aconn, location[DICT_CITY_ID])
                        )
                        await asyncio.gather(findTask)
                        city = findTask.result()

                        if city.warehouseId == None:
                            tg.create_task(
                                self.__warehouseConnsTable.insertCityMainWarehouse(
                                    aconn.acursor(),
                                    self.__ORSGeocoder,
                                    location[DICT_REGION_ID],
                                    location[DICT_CITY_ID],
                                    parentWarehouseDict,
                                    warehouseDict,
                                )
                            )
                            parentWarehouseDict = warehouseDict

                            # Set as Main City Warehouse
                            tg.create_task(
                                self.__citiesTable.modify(
                                    aconn,
                                    location[DICT_CITY_ID],
                                    CITIES_FK_WAREHOUSE,
                                    warehouseId,
                                )
                            )

                        else:
                            getTask = asyncio.create_task(
                                self.__getWarehouseDict(aconn, city.warehouseId)
                            )
                            await asyncio.gather(getTask)
                            parentWarehouseDict = getTask.result()

                            # Insert City Warehouse Connection
                            await asyncio.gather(
                                self.__warehouseConnsTable.insertCityWarehouse(
                                    aconn.acursor(),
                                    self.__ORSGeocoder,
                                    parentWarehouseDict,
                                    warehouseDict,
                                )
                            )

                elif tableName == BRANCHES_TABLE_NAME:
                    # Get Warehouse at the Given City
                    getWarehouseTask = asyncio.create_task(
                        self.getWarehouseId(aconn, location[DICT_CITY_ID])
                    )
                    await asyncio.gather(getWarehouseTask)
                    warehouseId = getWarehouseTask.result()

                    # Get Route Distance
                    getRouteTask = asyncio.create_task(
                        self.__getRouteDistance(aconn, warehouseId, location)
                    )
                    await asyncio.gather(getRouteTask)
                    routeDistance = getRouteTask.result()

                    # Ask for the Other Branch Fields and Insert the Branch to Its Table
                    await asyncio.gather(
                        self.__branchesTable.add(
                            aconn,
                            location,
                            buildingName,
                            warehouseId,
                            routeDistance,
                        )
                    )

            # Ask to Add More
            if not Confirm.ask(ADD_MORE_MSG):
                break

            # Commit
            commitTask = asyncio.create_task(aconn)

            # Clear Terminal
            clear()

            await asyncio.gather(commitTask)

    async def _rmHandler(self, aconn, tableName: str) -> None:
        """
        Asynchronous Handler of ``rm`` Location-related Subcommand

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str tableName: Location Table Name at the Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises MainWarehouseError: Raised if the Warehouse that's being Removed is Referenced as the Main One at Any Location Table
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        if tableName == COUNTRIES_TABLE_NAME:
            # Select Country ID to Remove
            getTask = asyncio.create_task(self.getCountryId(aconn))
            await asyncio.gather(getTask)
            countryId = getTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__countriesTable.get(aconn, COUNTRIES_ID, countryId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            await asyncio.gather(self.__countriesTable.remove(aconn, countryId))

        elif tableName == REGIONS_TABLE_NAME:
            # Select Region ID to Remove
            getTask = asyncio.create_task(self.getRegionId())
            await asyncio.gather(getTask)
            regionId = getTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__regionsTable.get(aconn, REGIONS_ID, regionId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            await asyncio.gather(self.__regionsTable.remove(aconn, regionId))

        elif tableName == CITIES_TABLE_NAME:
            # Select City ID to Remove
            getTask = asyncio.create_task(self.getCityId)
            await asyncio.gather(getTask)
            cityId = getTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(self.__citiesTable.get(aconn, CITIES_ID, cityId))
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            await asyncio.gather(self.__citiesTable.remove(aconn, cityId))

        elif tableName == WAREHOUSES_TABLE_NAME:
            # Select Warehouse ID to Remove
            getCityTask = asyncio.create_task(self.getCityId(aconn))
            await asyncio.gather(getCityTask)
            cityId = getCityTask.result()
            getWarehouseTask = asyncio.create_task(self.getWarehouseId(aconn, cityId))
            await asyncio.gather(getWarehouseTask)
            warehouseId = getWarehouseTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__warehousesTable.get(aconn, WAREHOUSES_ID, warehouseId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            # Check if it's the Main Warehouse at Any Location
            isMainTask = asyncio.create_task(
                self.__warehouseConnsTable.isMainWarehouse(aconn.acursor(), warehouseId)
            )
            await asyncio.gather(isMainTask)
            location = isMainTask.result()

            if location != None:
                locationTableName, locationId = location
                raise MainWarehouseError(locationTableName, locationId)

            else:
                # Remove City Warehouse Connections
                await asyncio.gather(
                    self.__warehouseConnsTable.removeCityWarehouse(
                        aconn.acursor(), warehouseId
                    )
                )

                # Remove Warehouse
                await asyncio.gather(self.__warehousesTable.remove(aconn, warehouseId))

        elif tableName == BRANCHES_TABLE_NAME:
            # Select Branch ID to Remove
            getCityTask = asyncio.create_task(self.getCityId(aconn))
            await asyncio.gather(getCityTask)
            cityId = getCityTask.result()
            getBranchTask = asyncio.create_task(self.getBranchId(aconn, cityId))
            await asyncio.gather(getBranchTask)
            branchId = getBranchTask.result()

            # Print Fetched Results
            if (
                await asyncio.gather(
                    self.__branchesTable.get(aconn, BRANCHES_ID, branchId)
                )
                == None
            ):
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            await asyncio.gather(self.__branchesTable.remove(aconn, branchId))

        # Press ENTER to Continue
        Prompt.ask(PRESS_ENTER)

    async def dbHandler(self, aconn, action: str, tableName: str) -> None:
        """
        Asynchronous Database Handler of ``add``, ``all``, ``get``, ``mod`` and ``rm`` Location-related Subcommands

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str action: Location-related Command (``add``, ``all``, ``get``, ``mod`` or ``rm``)
        :param str tableName: Location-related Table Name at Remote Database
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Command Execution
        """

        if action == DB_ADD:
            await asyncio.gather(self._addHandler(aconn, tableName))

        elif action == DB_GET:
            await asyncio.gather(self._getHandler(aconn, tableName))

        elif action == DB_ALL:
            await asyncio.gather(self._allHandler(aconn, tableName))

        elif action == DB_MOD:
            await asyncio.gather(self._modHandler(aconn, tableName))

        elif action == DB_RM:
            await asyncio.gather(self._rmHandler(aconn, tableName))

    async def graphHandler(self, aconn, graphType: str, level: str) -> None:
        """
        Asynchronous Graph Handler of ``countries``, ``regions`` and ``cities`` Graph Level Subcommands

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str graphType: Graph Type Command
        :param str level: Graph Level Command (``countries``, ``regions`` and ``cities``)
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Command Execution
        """

        global rushWGraph

        # Select Graph Layout
        layout = Prompt.ask("Select a Layout", choices=LAYOUT_CMDS)

        # Check the Graph Type Command
        if graphType == WAREHOUSES_TABLE_NAME:
            # Check if the Given Graph is Initialized
            if rushWGraph == None:
                initTask = asyncio.create_task(RushWGraph.create(aconn, True))
                await asyncio.gather(initTask)
                rushWGraph = initTask.result()

            # Update the Graph
            else:
                await asyncio.gather(rushWGraph.update(aconn))

            warehouseIds = None
            locationId = None

            if level == COUNTRIES_TABLE_NAME:
                # Select Country ID
                getTask = asyncio.create_task(self.getCountryId(aconn))
                await asyncio.gather(getTask)
                locationId = countryId = getTask.result()

                # Get the Region Main Warehouse IDs at the Given Country
                warehouseTask = asyncio.create_task(
                    self.__warehouseConnsTable.getRegionMainWarehouseIds(
                        aconn.acursor(), countryId
                    )
                )
                await asyncio.gather(warehouseTask)
                warehouseIds = warehouseTask.result()

            elif level == REGIONS_TABLE_NAME:
                # Select Region ID
                getTask = asyncio.create_task(self.getRegionId(aconn))
                await asyncio.gather(getTask)
                locationId = regionId = getTask.result()

                # Get the City Main Warehouse IDs at the Given Region
                warehouseTask = asyncio.create_task(
                    self.__warehouseConnsTable.getCityMainWarehouseIds(
                        aconn.acursor(), regionId
                    )
                )
                # Get the Region Main Warehouse ID
                findTask = asyncio.create_task(
                    self.__regionsTable.find(aconn, regionId)
                )

                tasks = [warehouseTask, findTask]
                try:
                    await asyncio.gather(*tasks)

                except Exception as err:
                    cancelTasks(tasks)
                    raise err

                warehouseIds = warehouseTask.result()
                region = findTask.result()

                # Add the Region Main Warehouse ID
                warehouseIds.append(region.warehouseId)

            elif level == CITIES_TABLE_NAME:
                # Select City ID
                getTask = asyncio.create_task(self.getCityId(aconn))
                await asyncio.gather(getTask)
                locationId = cityId = getTask.result()

                # Get the Warehouse IDs at the Given City
                warehouseTask = asyncio.create_task(
                    self.__warehouseConnsTable.getCityWarehouseIds(
                        aconn.cursor(), cityId
                    )
                )
                await asyncio.gather(warehouseTask)
                warehouseIds = warehouseTask.result()

            # Draw the Graph with the Given Warehouse IDs and Layout. Store it Locally
            rushWGraph.draw(layout, level, locationId, warehouseIds)

from rich.prompt import Prompt, IntPrompt, Confirm

from .constants import *
from .exceptions import (
    RowNotFound,
    InvalidLocation,
    BuildingFound,
    WarehouseNotFound,
    InvalidWarehouse,
)

from ..geocoding.geopy import (
    GeoPyGeocoder,
    NOMINATIM_LATITUDE,
    NOMINATIM_LONGITUDE,
)
from ..geocoding.routingpy import RoutingPyGeocoder

from ..io.constants import (
    ADD,
    RM,
    ALL,
    GET,
    MOD,
)
from ..io.validator import *

from ..local_database.database import GeoPyDatabase, GeoPyTables

from ..model.database_tables import uniqueInsertedMult, uniqueInserted
from ..model.database_territory import *
from ..model.database_building import *
from ..model.database_warehouse_conn import *


# Location Table-related Event Handler
class LocationEventHandler:
    # Table Classes
    _countryTable = None
    _provinceTable = None
    _regionTable = None
    _cityTable = None
    _cityAreaTable = None
    _warehouseTable = None
    _warehouseConnTable = None
    _branchTable = None

    # GeoPy Local Database
    _localdb = None
    _tables = None

    # Geocoders
    _geoPyGeocoder = None
    _routingPyGeocoder = None

    # Get Location Messages
    _GET_COUNTRY_MSG = "Enter Country Name"
    _GET_PROVINCE_MSG = "Enter Province Name"
    _GET_REGION_MSG = "Enter Region Name"
    _GET_CITY_MSG = "Enter City Name"
    _GET_CITY_AREA_MSG = "Enter City Area Name"

    # Constructor
    def __init__(self, db: Database, user: str, ORSApiKey: str):
        # Initialize Table Classes
        self._countryTable = CountryTable(db)
        self._provinceTable = ProvinceTable(db)
        self._regionTable = RegionTable(db)
        self._cityTable = CityTable(db)
        self._cityAreaTable = CityAreaTable(db)
        self._warehouseTable = WarehouseTable(db)
        self._warehouseConnTable = WarehouseConnectionTable(db)
        self._branchTable = BranchTable(db)

        # Initialize GeoPy Local Database
        self._localdb = GeoPyDatabase()

        # Get GeoPy Local Database Cursor
        cursor = self._localdb.getCursor()

        # Initialize Local Database Tables Class
        self._tables = GeoPyTables(cursor)

        # Initialize GeoPy and RoutingPy Geocoders
        self._geoPyGeocoder = GeoPyGeocoder(user)
        self._routingPyGeocoder = RoutingPyGeocoder(ORSApiKey, user)

        # Check if Building Exists

    def __buildingExists(self, areaId: str, buildingName: str) -> bool:
        buildingFields = [BUILDING_FK_CITY_AREA, BUILDING_NAME]
        buildingValues = [areaId, buildingName]

        # Check if Building Name has already been Inserted for the City Area
        if self._warehouseTable._getMultParentTable(buildingFields, buildingValues):
            uniqueInsertedMult(buildingValues, buildingFields, buildingValues)
            return

    # Returns Building Type Corresponding for the Given Table
    def __buildingType(self, tableName: str) -> None | str:
        if tableName == WAREHOUSE_TABLENAME:
            return "Warehouse"

        elif tableName == BRANCH_TABLENAME:
            return "Branch"

        return None

    # Returns Complete Building Name
    def __buildingName(self, buildingType: str, buildingName: str) -> str:
        return f"{buildingType} {buildingName}"

    # Ask for Building Common Fields
    def __askBuildingFields(
        self,
        tableName: str,
        buildingType: str,
        areaId: int,
    ) -> None | tuple[str, int, str, str]:
        # Get Building Name
        buildingName = Prompt.ask(f"Enter {buildingType} Name")

        # Check Building Name
        isAddressValid(tableName, BUILDING_NAME, buildingName)

        # Get Building Complete Name
        buildingName = self.__buildingName(buildingType, buildingName)

        # Check if Building Name for the Given City Area Already Exists
        if self.__buildingExists(areaId, buildingName):
            console.print(
                f"There's a Building Named as '{buildingName}' in '{areaId}'",
                style="warning",
            )
            raise BuildingFound(buildingName, areaId)

        # Get New Building Fields
        buildingPhone = Prompt.ask(f"Enter {buildingType} Phone Number")
        buildingEmail = Prompt.ask(f"Enter {buildingType} Email")
        addressDescription = Prompt.ask(f"Enter {buildingType} Address Description")

        # Check Building Warehouse Name, Phone, Email and Description
        isPhoneValid(tableName, BUILDING_PHONE, buildingPhone)
        isEmailValid(buildingEmail)
        isAddressValid(tableName, BUILDING_ADDRESS_DESCRIPTION, addressDescription)

        return buildingName, buildingPhone, buildingEmail, addressDescription

    # Ask for Building Common Values
    def __askBuildingValue(self, buildingType: str, field: str):
        if field == BUILDING_PHONE:
            value = str(IntPrompt.ask(MOD_VALUE_MSG))

        elif field == BUILDING_EMAIL:
            value = Prompt.ask(MOD_VALUE_MSG)

            # Check Building Email and Get its Normalized Form
            value = isEmailValid(value)

        elif field == BUILDING_NAME:
            value = Prompt.ask(MOD_VALUE_MSG)

            # Check Building Name
            isAddressValid(BUILDING_TABLENAME, field, value)

            # Get Building Complete Name
            value = self.__buildingName(buildingType, value)

        # Not a Building Table Column
        else:
            return None

        return value

    # Returns Warehouse Connection ID and Route Distance from a Given Branch
    def __getBranchWarehouseConnection(
        self, areaId: int, location: dict
    ) -> None | tuple[int, int]:
        # Clear Terminal
        clear()

        # Initialize Warehouse Coordinates Dictionary
        warehouseCoords = {}

        # Print Warehouses at the Given City Area
        if not self._warehouseTable.get(BUILDING_FK_CITY_AREA, areaId):
            raise WarehouseNotFound(areaId)

        while True:
            try:
                # Select Branch Warehouse Connection from the Given City Area
                warehouseId = IntPrompt.ask("Select the Warehouse Connection")

                # Get Warehouse Object
                warehouse = self._warehouseTable.find(warehouseId)

                # Check if Warehouse ID Exists and is in the Given City Area
                if warehouse == None or warehouse.areaId != areaId:
                    raise InvalidWarehouse(areaId)

                # Get Warehouse Coordinates
                warehouseCoords[NOMINATIM_LATITUDE] = warehouse.gpsLatitude
                warehouseCoords[NOMINATIM_LONGITUDE] = warehouse.gpsLongitude

                break

            except Exception as err:
                console.print(err, style="warning")
                continue

        # Calculate Route Distance
        routeDistance = self._routingPyGeocoder.getRouteDistance(
            warehouseCoords, location
        )

        return warehouseId, routeDistance

    # Returns Warehouse ID from a Given City Area
    def __getCityAreaWarehouse(self, areaId: int) -> Warehouse | None:
        # Print Warehouses at the Given City Area
        if not self._warehouseTable.get(BUILDING_FK_CITY_AREA, areaId):
            raise WarehouseNotFound(areaId)

        while True:
            try:
                # Select Main Warehouse for the Given Region
                warehouseId = IntPrompt.ask("Select the Warehouse")

                # Get Warehouse Object
                warehouse = self._warehouseTable.find(warehouseId)

                # Check if Warehouse ID Exists and is in the Given City Area
                if warehouse == None or warehouse.areaId != areaId:
                    raise InvalidWarehouse(areaId)

                return warehouse

            except Exception as err:
                console.print(err, style="warning")
                continue

    # Get Valid Warehouse Dictionary to be Used by a Warehouse Table Class
    def __getWarehouseDict(self, w:Warehouse)->dict:
        # Initialize Dictionary
        warehouseDict = {}

        # Assign Dictionary Fields
        warehouseDict[DICT_WAREHOUSES_ID] = w.buildingId
        warehouseDict[DICT_WAREHOUSES_COORDS] = {NOMINATIM_LONGITUDE: w.gpsLongitude, NOMINATIM_LATITUDE:w.gpsLatitude}

        return warehouseDict

    # Get Country ID and Name
    def getCountryId(self) -> dict | None:
        while True:
            countrySearch = Prompt.ask(self._GET_COUNTRY_MSG)

            # Check Country Name
            isAddressValid(COUNTRY_TABLENAME, COUNTRY_NAME, countrySearch)

            # Initialize Data Dictionary
            location = {}

            # Check if Country Search is Stored in Local Database
            countryNameId = self._tables.getCountrySearchNameId(countrySearch)
            location[DICT_COUNTRY_NAME_ID] = countryNameId
            countryName = None

            # Check Country Name ID
            if countryNameId != None:
                # Get Country Name from Local Database
                countryName = self._tables.getCountryName(countryNameId)
                location[DICT_COUNTRY_NAME] = countryName
            else:
                # Get Country Name from GeoPy API based on the Name Provided
                try:
                    countryName = self._geoPyGeocoder.getCountry(countrySearch)
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                location[DICT_COUNTRY_NAME] = countryName

                # Store Country Search in Local Database
                self._tables.addCountry(countrySearch, countryName)

                # Get Country Name ID from Local Database
                location[DICT_COUNTRY_NAME_ID] = self._tables.getCountryNameId(
                    countryName
                )

            break

        # Get Country
        c = self._countryTable.find(COUNTRY_NAME, countryName)

        if c == None:
            raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

        # Set Country ID to Data Dictionary
        location[DICT_COUNTRY_ID] = c.countryId

        return location

    # Get Province ID based on its Name and the Country ID where it's Located
    def getProvinceId(self) -> dict | None:
        # Get Country ID
        location = self.getCountryId()

        while True:
            provinceSearch = Prompt.ask(self._GET_PROVINCE_MSG)

            # Check Province Name
            isAddressValid(PROVINCE_TABLENAME, PROVINCE_NAME, provinceSearch)

            # Check if Province Search is Stored in Local Database
            provinceNameId = self._tables.getProvinceSearchNameId(
                location[DICT_COUNTRY_NAME_ID], provinceSearch
            )
            location[DICT_PROVINCE_NAME_ID] = provinceNameId
            provinceName = None

            # Check Province Name ID
            if provinceNameId != None:
                # Get Province Name from Local Database
                provinceName = self._tables.getProvinceName(provinceNameId)
                location[DICT_PROVINCE_NAME] = provinceName
            else:
                # Get Province Name from GeoPy API based on the Name Provided
                try:
                    provinceName = self._geoPyGeocoder.getProvince(
                        location, provinceSearch
                    )
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                location[DICT_PROVINCE_NAME] = provinceName

                # Store Province Search at Local Database
                self._tables.addProvince(
                    location[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
                )

                # Get Province Name ID from Local Database
                location[DICT_PROVINCE_NAME_ID] = self._tables.getProvinceNameId(
                    location[DICT_COUNTRY_NAME_ID], provinceName
                )

            break

        # Get Province
        p = self._provinceTable.findMult(location[DICT_COUNTRY_ID], provinceName)

        if p == None:
            raise RowNotFound(PROVINCE_TABLENAME, PROVINCE_NAME, provinceName)

        # Drop Country ID and Country Name ID from Data Dictionary
        location.pop(DICT_COUNTRY_ID)
        location.pop(DICT_COUNTRY_NAME_ID)

        # Set Province ID to Data Dictionary
        location[DICT_PROVINCE_ID] = p.provinceId

        return location

    # Get Region ID based on its Name and the Province ID where it's Located
    def getRegionId(self) -> dict | None:
        # Get Province ID
        location = self.getProvinceId()

        while True:
            regionSearch = Prompt.ask(self._GET_REGION_MSG)

            # Check Region Name
            isAddressValid(REGION_TABLENAME, REGION_NAME, regionSearch)

            # Check if Region Search is Stored in Local Database
            regionNameId = self._tables.getRegionSearchNameId(
                location[DICT_PROVINCE_NAME_ID], regionSearch
            )
            location[DICT_REGION_NAME_ID] = regionNameId
            regionName = None

            # Check Region Name ID
            if regionNameId != None:
                # Get Region Name from Local Database
                regionName = self._tables.getRegionName(regionNameId)
                location[DICT_REGION_NAME] = regionName
            else:
                # Get Region Name from GeoPy API based on the Name Provided
                try:
                    regionName = self._geoPyGeocoder.getRegion(location, regionSearch)
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                location[DICT_REGION_NAME] = regionName

                # Store Region Search in Local Database
                self._tables.addRegion(
                    location[DICT_PROVINCE_NAME_ID], regionSearch, regionName
                )

                # Get Region Name ID from Local Database
                location[DICT_REGION_NAME_ID] = self._tables.getRegionNameId(
                    location[DICT_PROVINCE_NAME_ID], regionName
                )

            break

        # Get Region
        r = self._regionTable.findMult(location[DICT_PROVINCE_ID], regionName)

        if r == None:
            raise RowNotFound(REGION_TABLENAME, REGION_NAME, regionName)

        # Drop Province ID and Province Name ID from Data Dictionary
        location.pop(DICT_PROVINCE_ID)
        location.pop(DICT_PROVINCE_NAME_ID)

        # Set Region ID to Data Dictionary
        location[DICT_REGION_ID] = r.regionId

        return location

    # Get Region ID from a Given Province ID
    def __buildingRegionId(self, provinceId: int) -> None | int:
        # Clear Terminal
        clear()

        # Print Regions at the Given Province
        if not self._regionTable.get(REGION_FK_PROVINCE, provinceId):
            raise RowNotFound(REGION_TABLENAME, REGION_FK_PROVINCE, provinceId)

        while True:
            try:
                # Select Region ID from the Given Province
                regionId = IntPrompt.ask("\nSelect Building Region ID")

                # Get Region Object
                region = self._regionTable.find(regionId)

                # Check if Region ID Exists and is in the Given Province
                if region == None:
                    raise RowNotFound(REGION_TABLENAME, REGION_ID, regionId)
                elif region.provinceId != provinceId:
                    raise InvalidLocation(region.name, PROVINCE_TABLENAME, provinceId)

                return regionId

            except Exception as err:
                console.print(err, style="warning")
                continue

    # Get City ID based on its Name and the Region ID where it's Located
    def getCityId(self) -> dict | None:
        # Get Region ID
        location = self.getRegionId()

        while True:
            citySearch = Prompt.ask(self._GET_CITY_MSG)

            # Check City Name
            isAddressValid(CITY_TABLENAME, CITY_NAME, citySearch)

            # Check if City Search is Stored in Local Database
            cityNameId = self._tables.getCitySearchNameId(
                location[DICT_REGION_NAME_ID], citySearch
            )
            location[DICT_CITY_NAME_ID] = cityNameId
            cityName = None

            # Check City Name ID
            if cityNameId != None:
                # Get City Name from Local Database
                cityName = self._tables.getCityName(cityNameId)
                location[DICT_CITY_NAME] = cityName
            else:
                # Get City Name from GeoPy API based on the Name Provided
                try:
                    cityName = self._geoPyGeocoder.getCity(
                        location,
                        citySearch,
                    )
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                location[DICT_CITY_NAME] = cityName

                # Store City Search at Local Database
                self._tables.addCity(
                    location[DICT_REGION_NAME_ID], citySearch, cityName
                )

                # Get City Name ID from Local Database
                location[DICT_CITY_NAME_ID] = self._tables.getCityNameId(
                    location[DICT_REGION_NAME_ID], cityName
                )

            break

        # Get City
        c = self._cityTable.findMult(location[DICT_REGION_ID], cityName)

        if c == None:
            raise RowNotFound(CITY_TABLENAME, CITY_NAME, cityName)

        # Drop Region ID and Region Name ID from Data Dictionary
        location.pop(DICT_REGION_ID)
        location.pop(DICT_REGION_NAME_ID)

        # Set City ID to Data Dictionary
        location[DICT_CITY_ID] = c.cityId

        return location

    # Get City ID from a Given Region ID
    def __buildingCityId(self, regionId: int) -> None | int:
        # Clear Terminal
        clear()

        # Print Cities at the Given Region
        if not self._cityTable.get(CITY_FK_REGION, regionId):
            raise RowNotFound(CITY_TABLENAME, CITY_FK_REGION, regionId)

        while True:
            try:
                # Select City ID from the Given Region
                cityId = IntPrompt.ask("\nSelect Building City ID")

                # Get City Object
                city = self._cityTable.find(cityId)

                # Check if City ID Exists and is in the Given Region
                if city == None:
                    raise RowNotFound(CITY_TABLENAME, CITY_ID, cityId)
                elif city.regionId != regionId:
                    raise InvalidLocation(city.name, REGION_TABLENAME, regionId)

                return cityId

            except Exception as err:
                console.print(err, style="warning")
                continue

    # Get City Area ID based on its Name and the City ID where it's Located
    def getCityAreaId(self) -> dict | None:
        # Get City ID
        location = self.getCityId()

        while True:
            areaSearch = Prompt.ask(self._GET_CITY_AREA_MSG)

            # Check City Area Name
            isAddressValid(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaSearch)

            # Check if City Area Search is Stored in Local Database
            areaNameId = self._tables.getCityAreaSearchNameId(
                location[DICT_CITY_NAME_ID], areaSearch
            )
            location[DICT_CITY_AREA_NAME_ID] = areaNameId
            areaName = None

            # Check City Name ID
            if areaNameId != None:
                # Get City Name from Local Database
                areaName = self._tables.getCityAreaName(areaNameId)
                location[DICT_CITY_AREA_NAME] = areaName
            else:
                # Get City Area Name from GeoPy API based on the Name Provided
                try:
                    areaName = self._geoPyGeocoder.getCityArea(
                        location,
                        areaSearch,
                    )
                except Exception as err:
                    console.print(err, style="warning")
                    continue

                location[DICT_CITY_AREA_NAME] = areaName

                # Store City Area Search at Local Database
                self._tables.addCityArea(
                    location[DICT_CITY_NAME_ID], areaSearch, areaName
                )

                # Get City Area Name ID from Local Database
                location[DICT_CITY_AREA_NAME_ID] = self._tables.getCityAreaNameId(
                    location[DICT_CITY_NAME_ID], areaName
                )

            break

        # Get City Area
        a = self._cityAreaTable.findMult(location[DICT_CITY_ID], areaName)

        if a == None:
            raise RowNotFound(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaName)

        # Drop City ID and City Name ID from Data Dictionary
        location.pop(DICT_CITY_ID)
        location.pop(DICT_CITY_NAME_ID)

        # Set City Area ID to Data Dictionary
        location[DICT_CITY_AREA_ID] = a.areaId

        return location

    # Get City ID Area from a Given City ID
    def __buildingCityAreaId(self, cityId: int) -> None | int:
        # Clear Terminal
        clear()

        # Print City Areas at the Given City
        if not self._cityAreaTable.get(CITY_AREA_FK_CITY, cityId):
            raise RowNotFound(CITY_AREA_TABLENAME, CITY_AREA_FK_CITY, cityId)

        while True:
            try:
                # Select City Area ID from the Given City
                areaId = IntPrompt.ask("\nSelect Building City Area ID")

                # Get City Area Object
                area = self._cityAreaTable.find(areaId)

                # Check if City Area ID Exists and is in the Given City
                if area == None:
                    raise RowNotFound(CITY_AREA_TABLENAME, CITY_AREA_ID, areaId)
                elif area.cityId != cityId:
                    raise InvalidLocation(area.areaName, CITY_TABLENAME, cityId)

                return areaId

            except Exception as err:
                console.print(err, style="warning")
                continue

    # Get Place Coordinates
    def getPlaceCoordinates(self, msg: str) -> dict | None:
        # Get City Area ID
        location = self.getCityAreaId()

        while True:
            try:
                # Get Place Name to Search
                placeSearch = Prompt.ask(msg)

                # Check Place Search
                isPlaceNameValid(placeSearch)

                # Get Place Coordinates from GeoPy API based on the Data Provided
                location = self._geoPyGeocoder.getPlaceCoordinates(
                    location, placeSearch
                )

                return location

            # Handle LocationError Exception
            except Exception as err:
                console.print(err, style="warning")
                continue

    # Get All Table Handler
    def _allHandler(self, tableName: str) -> None:
        sortBy = None

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(ALL_DESC_MSG)

        if tableName == COUNTRY_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._countryTable.all(sortBy, desc)

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

            # Clear Terminal
            clear()

            # Print Table
            self._provinceTable.all(sortBy, desc)

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

            # Clear Terminal
            clear()

            # Print Table
            self._regionTable.all(sortBy, desc)

        elif tableName == CITY_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME, CITY_FK_WAREHOUSE],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._cityTable.all(sortBy, desc)

        elif tableName == CITY_AREA_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    CITY_AREA_ID,
                    CITY_AREA_FK_CITY,
                    CITY_AREA_NAME,
                    CITY_AREA_FK_WAREHOUSE,
                ],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._cityAreaTable.all(sortBy, desc)

        elif tableName == WAREHOUSE_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[WAREHOUSE_ID, BUILDING_NAME, BUILDING_FK_CITY_AREA],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._warehouseTable.all(sortBy, desc)

        elif tableName == BRANCH_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    BRANCH_ID,
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BRANCH_ROUTE_DISTANCE,
                    BUILDING_NAME,
                    BUILDING_FK_CITY_AREA,
                ],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._branchTable.all(sortBy, desc)

    # Get Table Handler
    def _getHandler(self, tableName: str) -> None:
        field = value = None

        if tableName == COUNTRY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Prompt to Ask the Value to be Compared
            if field == COUNTRY_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._countryTable.get(field, value)

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

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._provinceTable.get(field, value)

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

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._regionTable.get(field, value)

        elif tableName == CITY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME, CITY_FK_WAREHOUSE],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._cityTable.get(field, value)

        elif tableName == CITY_AREA_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    CITY_AREA_ID,
                    CITY_AREA_FK_CITY,
                    CITY_AREA_NAME,
                    CITY_AREA_FK_WAREHOUSE,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_AREA_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._cityAreaTable.get(field, value)

        elif tableName == WAREHOUSE_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    WAREHOUSE_ID,
                    BUILDING_NAME,
                    BUILDING_PHONE,
                    BUILDING_FK_CITY_AREA,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == BUILDING_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._warehouseTable.get(field, value)

        elif tableName == BRANCH_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    BRANCH_ID,
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BUILDING_NAME,
                    BUILDING_PHONE,
                    BUILDING_FK_CITY_AREA,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == BUILDING_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._branchTable.get(field, value)

    # Modify Row from Table Handler
    def _modHandler(self, tableName: str) -> None:
        field = value = None

        # Building Type
        buildingType = None

        # Initialize Warehouse Dictionary
        warehouseDict = {}

        # Get Building Type
        if tableName == WAREHOUSE_TABLENAME or tableName == BRANCH_ID:
            buildingType = self.__buildingType(tableName)

        if tableName == COUNTRY_TABLENAME:
            # Ask for Country ID to Modify
            countryId = IntPrompt.ask("\nEnter Country ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()
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
            self._countryTable.modify(countryId, field, value)

        elif tableName == PROVINCE_TABLENAME:
            # Ask for Province ID to Modify
            provinceId = IntPrompt.ask("\nEnter Province ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._provinceTable.get(PROVINCE_ID, provinceId):
                noCoincidenceFetched()
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
                # Select Main City Area ID
                regionId = self.__buildingRegionId(provinceId)
                cityId = self.__buildingCityId(regionId)
                areaId = self.__buildingCityAreaId(cityId)

                # Clear Terminal
                clear()

                # Get Main Warehouse for the Given City Area
                warehouse = self.__getCityAreaWarehouse(areaId)

                # Get Warehouse Dictionary Fields from Warehouse Object
                warehouseDict = self.__getWarehouseDict(warehouse)

                # Get Current Province Main Warehouse ID
                currWarehouse = self._provinceTable.find(provinceId)

                # Check if there's a Main Warehouse
                if currWarehouse != None:
                    currWarehouseId = currWarehouse.warehouseId

                    # Drop Old Warehouse Connections with all the Main Province Warehouses at the Same Country and all the Main Region Warehouses at the Given Province
                    self._warehouseConnTable.removeProvinceMainWarehouse(provinceId, currWarehouseId)

                # Get Province Object
                province = self._provinceTable.find(provinceId)

                # Get Province Country ID
                countryId = province.countryId

                # Add Warehouse Connections for the Current Warehouse All the Main Province Warehouses at the Given Country and all the Main Region Warehouses at the Given Province
                self._warehouseConnTable.insertProvinceMainWarehouse(countryId, provinceId, warehouseDict)

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSES_ID]

            # Modify Province
            self._provinceTable.modify(provinceId, field, value)

        elif tableName == REGION_TABLENAME:
            # Ask for Region ID to Modify
            regionId = IntPrompt.ask("\nEnter Region ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()
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
                # Select Main City Area ID
                cityId = self.__buildingCityId(regionId)
                areaId = self.__buildingCityAreaId(cityId)

                # Clear Terminal
                clear()

                # Get Main Warehouse for the Given City Area
                warehouse = self.__getCityAreaWarehouse(areaId)

                # Get Warehouse Dictionary Fields from Warehouse Object
                warehouseDict = self.__getWarehouseDict(warehouse)

                # Get Current Region Main Warehouse ID
                currWarehouse = self._regionTable.find(regionId)

                # Check if there's a Main Warehouse
                if currWarehouse != None:
                    currWarehouseId = currWarehouse.warehouseId

                    # TO DEVELOP: Drop Old Warehouse Connections with the Main Province Warehouse, all the Main Region Warehouses at the Same Province, and all the Main City Warehouses at the Given Region
                    self._warehouseConnTable.removeRegionMainWarehouse(regionId, currWarehouseId)

                # TO DEVELOP: Add Warehouse Connections for the Current Warehouse with the Main Province Warehouse, all the Main Region Warehouses at the Given Province and all the Main City Warehouses at the Given Region

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSES_ID]

            # Modify Region
            self._regionTable.modify(regionId, field, value)

        elif tableName == CITY_TABLENAME:
            # Ask for City ID to Modify
            cityId = IntPrompt.ask("\nEnter City ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityTable.get(CITY_ID, cityId):
                noCoincidenceFetched()
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
                # Select Main City Area ID
                areaId = self.__buildingCityAreaId(cityId)

                # Clear Terminal
                clear()

                # Get Main Warehouse for the Given City Area
                warehouseId = self.__getCityAreaWarehouse(areaId)

                # Get Warehouse Dictionary Fields from Warehouse Object
                warehouseDict = self.__getWarehouseDict(warehouse)

                # Get Current City Main Warehouse ID
                currWarehouse = self._cityTable.find(cityId)

                # Check if there's a Main Warehouse
                if currWarehouse != None:
                    currWarehouseId = currWarehouse.warehouseId

                    # TO DEVELOP: Drop Old Warehouse Connections with the Main Region Warehouse, all the Main City Warehouses at the Same Region, and all the Main City Area Warehouses at the Given City
                    self._warehouseConnTable.removeCityMainWarehouse(cityId, currWarehouseId)

                # TO DEVELOP: Add Warehouse Connections for the Current Warehouse with the Main Region Warehouse, all the Main City Warehouses at the Given Region and all the Main City Area Warehouses at the Given City

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSES_ID]

            # Modify City
            self._cityTable.modify(regionId, field, value)

        elif tableName == CITY_AREA_TABLENAME:
            # Ask for City Area ID to Modify
            areaId = IntPrompt.ask("\nEnter City Area ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityTable.get(CITY_AREA_ID, areaId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[CITY_AREA_DESCRIPTION],
            )

            # Prompt to Ask the New Value
            if field == CITY_AREA_DESCRIPTION:
                value = Prompt.ask(MOD_VALUE_MSG)

                # Check City Area Description
                isAddressValid(tableName, field, value)

            # Prompt to Ask the New Value
            elif field == CITY_AREA_FK_WAREHOUSE:
                # Clear Terminal
                clear()

                # Get Main Warehouse for the Given City Area
                warehouse = self.__getCityAreaWarehouse(areaId)

                # Get Warehouse Dictionary Fields from Warehouse Object
                warehouseDict = self.__getWarehouseDict(warehouse)

                # Get Current City Area Main Warehouse ID
                currWarehouse = self._cityAreaTable.find(areaId)

                # Check if there's a Main Warehouse
                if currWarehouse != None:
                    currWarehouseId = currWarehouse.warehouseId

                    # TO DEVELOP: Drop Old Warehouse Connections with the Main City Warehouse, all the Main City Area Warehouses at the Same City, and all the Warehouses at the Given City Area
                    self._warehouseConnTable.removeCityAreaMainWarehouse(areaId, currWarehouseId)

                # TO DEVELOP: Add Warehouse Connections for the Current Warehouse with the Main City Warehouse, all the Main City Area Warehouses at the Given City and all the Warehouses at the Given City Area

                # Assign Warehouse ID to value
                value = warehouseDict[DICT_WAREHOUSES_ID]

            # Modify City
            self._cityTable.modify(regionId, field, value)

            # Modify City Area
            self._cityAreaTable.modify(areaId, field, value)

        elif tableName == WAREHOUSE_TABLENAME:
            # Ask for Warehouse ID to Modify
            warehouseId = IntPrompt.ask("\nEnter Warehouse ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._warehouseTable.get(WAREHOUSE_ID, warehouseId):
                noCoincidenceFetched()
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
            value = self.__askBuildingValue(buildingType, field)

            # Modify Warehouse
            self._warehouseTable.modify(warehouseId, field, value)

        elif tableName == BRANCH_TABLENAME:
            # Ask for Branch ID to Modify
            branchId = IntPrompt.ask("\nEnter Branch ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._branchTable.get(BRANCH_ID, branchId):
                noCoincidenceFetched()
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
                value = self.__askBuildingValue(buildingType, field)

                # Modify Branch
                self._branchTable.modify(branchId, field, value)

            else:
                # Get Branch Object
                branch = self._branchTable.find(branchId)

                # Get City Area ID where the Branch is Located
                areaId = branch.areaId

                # Get Branch Coordinate
                location = {
                    NOMINATIM_LATITUDE: branch.gpsLatitude,
                    NOMINATIM_LONGITUDE: branch.gpsLongitude,
                }

                # Get New Warehouse Connection ID and Route Distance
                warehouseId, routeDistance = self.__getBranchWarehouseConnection(
                    areaId, location
                )

                # Modify Branch
                self._branchTable.modify(
                    branchId, BRANCH_FK_WAREHOUSE_CONNECTION, warehouseId
                )
                self._branchTable.modify(branchId, BRANCH_ROUTE_DISTANCE, routeDistance)

    # Add Row to Table Handler
    def _addHandler(self, tableName: str) -> None:
        # Location Dictionary
        location = None

        # Building Type
        buildingType = None

        # Get Building Type
        if tableName == WAREHOUSE_TABLENAME or tableName == BRANCH_ID:
            buildingType = self.__buildingType(tableName)

        while True:
            if tableName == COUNTRY_TABLENAME:
                # Asks for Country Fields
                countrySearch = Prompt.ask(self._GET_COUNTRY_MSG)
                phonePrefix = IntPrompt.ask("Enter Phone Prefix")

                # Check Country Name
                isAddressValid(tableName, COUNTRY_NAME, countrySearch)

                # Check if Country is Stored in Local Database
                countryNameId = self._tables.getCountrySearchNameId(countrySearch)
                countryName = None

                # Check Country Name ID
                if countryNameId != None:
                    # Get Country Name from Local Database
                    countryName = self._tables.getCountryName(countryNameId)
                else:
                    # Get Country Name from GeoPy API based on the Name Provided
                    countryName = self._geoPyGeocoder.getCountry(countrySearch)

                    # Store Country Search in Local Database
                    self._tables.addCountry(countrySearch, countryName)

                # Check if Country Name has already been Inserted
                if self._countryTable.get(COUNTRY_NAME, countryName, False):
                    uniqueInserted(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)
                    return

                # Insert Country
                self._countryTable.add(Country(countryName, phonePrefix))

            elif tableName == PROVINCE_TABLENAME:
                # Get Territory Location
                if location == None:
                    location = self.getCountryId()

                # Asks for Province Fields
                provinceSearch = Prompt.ask(self._GET_PROVINCE_MSG)

                # Check Province Name
                isAddressValid(tableName, PROVINCE_NAME, provinceSearch)

                # Check if Province is Stored in Local Database
                provinceNameId = self._tables.getProvinceSearchNameId(
                    location[DICT_COUNTRY_NAME_ID], provinceSearch
                )
                provinceName = None

                # Check Province Name ID
                if provinceNameId != None:
                    # Get Province Name from Local Database
                    provinceName = self._tables.getProvinceName(provinceNameId)
                else:
                    # Get Province Name from GeoPy API based on the Name Provided
                    provinceName = self._geoPyGeocoder.getProvince(
                        location, provinceSearch
                    )

                    # Store Province Search in Local Database
                    self._tables.addProvince(
                        location[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
                    )

                provinceFields = [PROVINCE_FK_COUNTRY, PROVINCE_NAME]
                provinceValues = [location[DICT_COUNTRY_ID], provinceName]

                # Check if Province Name has already been Inserted for the Given Country
                if self._provinceTable.getMult(provinceFields, provinceValues, False):
                    uniqueInsertedMult(
                        PROVINCE_TABLENAME, provinceFields, provinceValues
                    )
                    return

                # Insert Province
                self._provinceTable.add(
                    Province(provinceName, location[DICT_COUNTRY_ID])
                )

            elif tableName == REGION_TABLENAME:
                # Get Territory Location
                if location == None:
                    location = self.getProvinceId()

                # Asks for Region Fields
                regionSearch = Prompt.ask(self._GET_REGION_MSG)

                # Check Region Name
                isAddressValid(tableName, REGION_NAME, regionSearch)

                # Check if Region is Stored in Local Database
                regionNameId = self._tables.getRegionSearchNameId(
                    location[DICT_PROVINCE_NAME_ID], regionSearch
                )
                regionName = None

                # Check Region Name ID
                if regionNameId != None:
                    # Get Region Name from Local Database
                    regionName = self._tables.getRegionName(regionNameId)
                else:
                    # Get Region Name from GeoPy API based on the Name Provided
                    regionName = self._geoPyGeocoder.getRegion(location, regionSearch)

                    # Store Region Search in Local Database
                    self._tables.addRegion(
                        location[DICT_PROVINCE_NAME_ID], regionSearch, regionName
                    )

                regionFields = [REGION_FK_PROVINCE, REGION_NAME]
                regionValues = [location[DICT_PROVINCE_ID], regionName]

                # Check if Region Name has already been Inserted for the Given Province
                if self._regionTable.getMult(regionFields, regionValues, False):
                    uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
                    return

                # Insert Region
                self._regionTable.add(Region(regionName, location[DICT_PROVINCE_ID]))

            elif tableName == CITY_TABLENAME:
                # Get Territory Location
                if location == None:
                    location = self.getRegionId()

                # Asks for City Fields
                citySearch = Prompt.ask(self._GET_CITY_MSG)

                # Check City Name
                isAddressValid(tableName, CITY_NAME, citySearch)

                # Check if City is Stored in Local Database
                cityNameId = self._tables.getCitySearchNameId(
                    location[DICT_REGION_NAME_ID], citySearch
                )
                cityName = None

                # Check City Name ID
                if cityNameId != None:
                    # Get City Name from Local Database
                    cityName = self._tables.getCityName(cityNameId)
                else:
                    # Get City Name from GeoPy API based on the Name Provided
                    cityName = self._geoPyGeocoder.getCity(location, citySearch)

                    # Store City Search in Local Database
                    self._tables.addCity(
                        location[DICT_REGION_NAME_ID], citySearch, cityName
                    )

                cityFields = [CITY_FK_REGION, CITY_NAME]
                cityValues = [location[DICT_REGION_ID], cityName]

                # Check if City Name has already been Inserted for the Given Province
                if self._cityTable.getMult(cityFields, cityValues, False):
                    uniqueInsertedMult(CITY_TABLENAME, cityFields, cityValues)
                    return

                # Insert City
                self._cityTable.add(City(cityName, location[DICT_REGION_ID]))

            elif tableName == CITY_AREA_TABLENAME:
                # Get Territory Location
                if location == None:
                    location = self.getCityId()

                # Asks for City Area Fields
                areaSearch = Prompt.ask(self._GET_CITY_AREA_MSG)
                areaDescription = Prompt.ask("Enter City Area Description")

                # Check City Area Name and Description
                isAddressValid(tableName, CITY_AREA_NAME, areaSearch)
                isAddressValid(tableName, CITY_AREA_DESCRIPTION, areaDescription)

                # Check if City Area is Stored in Local Database
                areaNameId = self._tables.getCityAreaSearchNameId(
                    location[DICT_CITY_ID], areaSearch
                )
                areaName = None

                # Check City Area Name ID
                if areaNameId != None:
                    # Get City Area Name from Local Database
                    areaName = self._tables.getCityAreaName(areaNameId)
                else:
                    # Get City Area Name from GeoPy API based on the Name Provided
                    areaName = self._geoPyGeocoder.getCityArea(location, areaSearch)

                    # Store City Area Search in Local Database
                    self._tables.addCityArea(
                        location[DICT_CITY_NAME_ID], areaSearch, areaName
                    )

                areaFields = [CITY_AREA_FK_CITY, CITY_AREA_NAME]
                areaValues = [location[DICT_CITY_ID], areaName]

                # Check if City Area Name has already been Inserted for the Given City
                if self._cityAreaTable.getMult(areaFields, areaValues, False):
                    uniqueInsertedMult(CITY_AREA_TABLENAME, areaFields, areaValues)
                    return

                # Insert City Area
                self._cityAreaTable.add(
                    CityArea(areaName, areaDescription, location[DICT_CITY_ID])
                )

            elif tableName == WAREHOUSE_TABLENAME or tableName == BRANCH_TABLENAME:
                # Get Building Coordinates
                if location == None:
                    location = self.getPlaceCoordinates(
                        f"Enter Place Name Near to {buildingType}"
                    )

                # Get City Area ID
                areaId = location[DICT_CITY_AREA_ID]

                # Get Building Fields
                buildingFields = self.__askBuildingFields(
                    tableName, buildingType, areaId
                )

                buildingName, buildingPhone, buildingEmail, addressDescription = (
                    buildingFields
                )

                if tableName == WAREHOUSE_TABLENAME:
                    # Insert Warehouse
                    self._warehouseTable.add(
                        Warehouse(
                            buildingName,
                            location[NOMINATIM_LATITUDE],
                            location[NOMINATIM_LONGITUDE],
                            buildingEmail,
                            buildingPhone,
                            areaId,
                            addressDescription,
                        )
                    )

                    # TO DEVELOP: Add Warehouse Connections or set it as Main

                elif tableName == BRANCH_TABLENAME:
                    # Get New Warehouse Connection ID and Route Distance
                    warehouseId, routeDistance = self.__getBranchWarehouseConnection(
                        areaId, location
                    )

                    # Insert Branch
                    self._branchTable.add(
                        Branch(
                            buildingName,
                            location[NOMINATIM_LATITUDE],
                            location[NOMINATIM_LONGITUDE],
                            buildingEmail,
                            buildingPhone,
                            areaId,
                            addressDescription,
                            warehouseId,
                            routeDistance,
                        )
                    )

            # Ask to Add More
            if not Confirm.ask(ADD_MORE_MSG):
                break

    # Remove Row from Table Handler
    def _rmHandler(self, tableName: str) -> None:
        if tableName == COUNTRY_TABLENAME:
            # Ask for Country ID to Remove
            countryId = IntPrompt.ask("\nEnter Country ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._countryTable.remove(countryId)

        elif tableName == PROVINCE_TABLENAME:
            # Ask for Province ID to Remove
            provinceId = IntPrompt.ask("\nEnter Province ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._provinceTable.get(PROVINCE_ID, provinceId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._provinceTable.remove(provinceId)

        elif tableName == REGION_TABLENAME:
            # Ask for Region ID to Remove
            regionId = IntPrompt.ask("\nEnter Region ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._regionTable.remove(regionId)

        elif tableName == CITY_TABLENAME:
            # Ask for City ID to Remove
            cityId = IntPrompt.ask("\nEnter City ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityTable.get(CITY_ID, cityId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._cityTable.remove(cityId)

        elif tableName == CITY_AREA_TABLENAME:
            # Ask for City Area ID to Remove
            areaId = IntPrompt.ask("\nEnter City Area ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._cityAreaTable.get(CITY_AREA_ID, areaId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._cityAreaTable.remove(areaId)

        elif tableName == WAREHOUSE_TABLENAME:
            # Ask for Warehouse ID to Remove
            warehouseId = IntPrompt.ask("\nEnter Warehouse ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._warehouseTable.get(WAREHOUSE_ID, warehouseId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            # TO DEVELOP: Remove Warehouse Connections

            self._warehouseTable.remove(warehouseId)

        elif tableName == BRANCH_TABLENAME:
            # Ask for Branch ID to Remove
            branchId = IntPrompt.ask("\nEnter Branch ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._branchTable.get(BRANCH_ID, branchId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._branchTable.remove(branchId)

    # Location Event Handler
    def handler(self, action: str, tableName: str) -> None:
        # Clear Terminal
        clear()

        if action == ALL:
            self._allHandler(tableName)

        elif action == GET:
            self._getHandler(tableName)

        elif action == MOD:
            self._modHandler(tableName)

        elif action == ADD:
            self._addHandler(tableName)

        elif action == RM:
            self._rmHandler(tableName)

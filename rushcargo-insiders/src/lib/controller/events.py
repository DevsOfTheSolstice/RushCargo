from rich.prompt import Prompt, IntPrompt, Confirm
import logging
from rich.logging import RichHandler

from .constants import *

from ..model.database import *
from ..model.database_territory import *

from ..local_database.database import *
from ..local_database.constants import *

# from ..model.database_building import *

from ..geocoding.constants import *
from ..geocoding.geopy import *

from ..model.classes import *
from ..model.constants import *
from ..model.exceptions import *
from ..io.validator import *


# Get Rich Logger
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")


# Event Handler Class
class EventHandler:
    # Database Connection
    __db = None
    __user = None

    # All Handler Messages
    _allSortByMsg = "How do you want to Sort it?"
    _allDescMsg = "\nDo you want to Sort it in Descending Order?"

    # Get Handler Messages
    _getFieldMsg = "\nWhich Field do you want to Compare?"
    _getValueMsg = "Which Value do you want to Compare that Field with?"

    # Modify Handler Messages
    _modConfirmMsg = "Is this the Row you want to Modify?"
    _modFieldMsg = "Which Field do you want to Modify?"
    _modValueMsg = "Which New Value do you want to Assign it?"
    _noModMsg = "Nothing to Modify"

    # Remove Handler Messages
    _rmConfirmMsg = "Is this the Row you want to Remove?"

    # Event Handlers
    __territoryEventHandler = None

    # Constructor
    def __init__(self):
        # Initialize Database Connection
        self.__db, self.__user = initDb()

        # Initialize Event Hanlder Classes
        self.__initHandlers()

    # Initialize Event Handler Classes
    def __initHandlers(self):
        self.__territoryEventHandler = TerritoryEventHandler(self.__db, self.__user)

    # Main Event Handler
    def handler(self, action: str, tableGroup: str, table: str) -> None:
        tableMsg = "At which Table?"

        try:
            while True:
                try:
                    # Call Territory Event Handler
                    if tableGroup == TABLE_TERRITORY_CMD:
                        self.__territoryEventHandler.handler(action, table)

                except Exception as err:
                    console.print(err, style="warning")

                # Ask to Change Action
                if Confirm.ask("\nDo you want to Continue with this Command?"):
                    # Clear Screen
                    clear()

                    continue

                # Clear Screen
                clear()

                # Ask Next Action
                action = Prompt.ask("\nWhat do you want to do?", choices=ACTION_CMDS)

                # Check if the User wants to Exit the Program
                if action == EXIT:
                    break

                # Ask for Table Group to Work with
                tableGroup = Prompt.ask(
                    "At which Table Group?", choices=TABLE_GROUP_CMDS
                )

                # Ask for Table to Work with
                if tableGroup == TABLE_TERRITORY_CMD:
                    table = Prompt.ask(tableMsg, choices=TABLE_TERRITORY_CMDS)

                elif tableGroup == TABLE_BUILDING_CMD:
                    table = Prompt.ask(tableMsg, choices=TABLE_BUILDING_CMDS)
        except KeyboardInterrupt:
            return


# Territory Table-related Event Handler
class TerritoryEventHandler(EventHandler):
    # Table Classes
    _countryTable = None
    _provinceTable = None
    _regionTable = None
    _cityTable = None
    _cityAreaTable = None

    # Geocoders
    _geopyGeocoder = None

    # GeoPy Local Database
    __localdb = None
    __tables = None

    # Get Location Messages
    _getCountryMsg = "\nEnter Country Name"
    _getProvinceMsg = "Enter Province Name"
    _getRegionMsg = "Enter Region Name"
    _getCityMsg = "Enter City Name"
    _getCityAreaMsg = "Enter City Area Name"

    # Constructor
    def __init__(self, db: Database, user: str):
        # Initialize Table Classes
        self._countryTable = CountryTable(db)
        self._provinceTable = ProvinceTable(db)
        self._regionTable = RegionTable(db)
        self._cityTable = CityTable(db)
        self._cityAreaTable = CityAreaTable(db)

        # Initialize Geocoders
        self._geopyGeocoder = initGeoPyGeocoder(NOMINATIM_USER_AGENT, user)

        # Initialize GeoPy Local Database
        self.__localdb = GeoPyDatabase()

        # Get GeoPy Local Database Cursor
        cursor = self.__localdb.getCursor()

        # Initialize Local Database Tables Class
        self.__tables = GeoPyTables(cursor)

    # Get Country Id and Name
    def getCountryId(self) -> dict | None:
        countrySearch = Prompt.ask(self._getCountryMsg)

        # Check Country Name
        isValueValid(COUNTRY_TABLENAME, COUNTRY_NAME, countrySearch)

        # Initialize Data Dictionary
        data = {}

        # Check if Country Search is Stored in Local Database
        countryNameId = self.__tables.getCountrySearchNameId(countrySearch)
        data[DICT_COUNTRY_NAME_ID] = countryNameId
        countryName = None

        # Check Country Name ID
        if countryNameId != None:
            # Get Country Name from Local Database
            countryName = self.__tables.getCountryName(countryNameId)
            data[DICT_COUNTRY_NAME] = countryName
        else:
            # Get Country Name from GeoPy API based on the Name Provided
            countryName = self._geopyGeocoder.getCountry(countrySearch)
            data[DICT_COUNTRY_NAME] = countryName

            # Store Country Search in Local Database
            self.__tables.addCountry(countrySearch, countryName)

            # Get Country Name ID from Local Database
            data[DICT_COUNTRY_NAME_ID] = self.__tables.getCountryNameId(countryName)

        # Get Country
        c = self._countryTable.find(COUNTRY_NAME, countryName)

        if c == None:
            raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

        # Set Country ID to Data Dictionary
        data[DICT_COUNTRY_ID] = c.countryId

        return data

    # Get Province Id based on its Name and the Country Id where it's Located
    def getProvinceId(self) -> dict | None:
        data = self.getCountryId()
        provinceSearch = Prompt.ask(self._getProvinceMsg)

        # Check Province Name
        isValueValid(PROVINCE_TABLENAME, PROVINCE_NAME, provinceSearch)

        # Check if Province Search is Stored in Local Database
        provinceNameId = self.__tables.getProvinceSearchNameId(
            data[DICT_COUNTRY_NAME_ID], provinceSearch
        )
        data[DICT_PROVINCE_NAME_ID] = provinceNameId
        provinceName = None

        # Check Province Name ID
        if provinceNameId != None:
            # Get Province Name from Local Database
            provinceName = self.__tables.getProvinceName(provinceNameId)
            data[DICT_PROVINCE_NAME] = provinceName
        else:
            # Get Province Name from GeoPy API based on the Name Provided
            provinceName = self._geopyGeocoder.getProvince(data, provinceSearch)
            data[DICT_PROVINCE_NAME] = provinceName

            # Store Province Search at Local Database
            self.__tables.addProvince(
                data[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
            )

            # Get Province Name ID from Local Database
            data[DICT_PROVINCE_NAME_ID] = self.__tables.getProvinceNameId(
                data[DICT_COUNTRY_NAME_ID], provinceName
            )

        # Get Province
        p = self._provinceTable.find(data[DICT_COUNTRY_ID], provinceName)

        if p == None:
            raise RowNotFound(PROVINCE_TABLENAME, PROVINCE_NAME, provinceName)

        # Drop Country ID and Country Name ID from Data Dictionary
        data.pop(DICT_COUNTRY_ID)
        data.pop(DICT_COUNTRY_NAME_ID)

        # Set Province ID to Data Dictionary
        data[DICT_PROVINCE_ID] = p.provinceId

        return data

    # Get Region Id based on its Name and the Province Id where it's Located
    def getRegionId(self) -> dict | None:
        data = self.getProvinceId()
        regionSearch = Prompt.ask(self._getRegionMsg)

        # Check Region Name
        isValueValid(REGION_TABLENAME, REGION_NAME, regionSearch)

        # Check if Region Search is Stored in Local Database
        regionNameId = self.__tables.getRegionSearchNameId(
            data[DICT_PROVINCE_NAME_ID], regionSearch
        )
        data[DICT_REGION_NAME_ID] = regionNameId
        regionName = None

        # Check Region Name ID
        if regionNameId != None:
            # Get Region Name from Local Database
            regionName = self.__tables.getRegionName(regionNameId)
            data[DICT_REGION_NAME] = regionName
        else:
            # Get Region Name from GeoPy API based on the Name Provided
            regionName = self._geopyGeocoder.getRegion(data, regionSearch)
            data[DICT_REGION_NAME] = regionName

            # Store Region Search in Local Database
            self.__tables.addRegion(
                data[DICT_PROVINCE_NAME_ID], regionSearch, regionName
            )

            # Get Region Name ID from Local Database
            data[DICT_REGION_NAME_ID] = self.__tables.getRegionNameId(
                data[DICT_PROVINCE_NAME_ID], regionName
            )

        # Get Region
        r = self._regionTable.find(data[DICT_PROVINCE_ID], regionName)

        if r == None:
            raise RowNotFound(REGION_TABLENAME, REGION_NAME, regionName)

        # Drop Province ID and Province Name ID from Data Dictionary
        data.pop(DICT_PROVINCE_ID)
        data.pop(DICT_PROVINCE_NAME_ID)

        # Set Region ID to Data Dictionary
        data[DICT_REGION_ID] = r.regionId

        return data

    # Get City Id based on its Name and the Region Id where it's Located
    def getCityId(self) -> dict | None:
        data = self.getRegionId()
        citySearch = Prompt.ask(self._getCityMsg)

        # Check City Name
        isValueValid(CITY_TABLENAME, CITY_NAME, citySearch)

        # Check if City Search is Stored in Local Database
        cityNameId = self.__tables.getCitySearchNameId(
            data[DICT_REGION_NAME_ID], citySearch
        )
        data[DICT_CITY_NAME_ID] = cityNameId
        cityName = None

        # Check City Name ID
        if cityNameId != None:
            # Get City Name from Local Database
            cityName = self.__tables.getCityName(cityNameId)
            data[DICT_CITY_NAME] = cityName
        else:
            # Get City Name from GeoPy API based on the Name Provided
            cityName = self._geopyGeocoder.getCity(
                data,
                citySearch,
            )
            data[DICT_CITY_NAME] = cityName

            # Store Region Search at Local Database
            self.__tables.addCity(data[DICT_REGION_NAME_ID], citySearch, cityName)

            # Get City Name ID from Local Database
            data[DICT_CITY_NAME_ID] = self.__tables.getCityNameId(
                data[DICT_REGION_NAME_ID], cityName
            )

        # Get City
        c = self._cityTable.find(data[DICT_REGION_ID], cityName)

        if c == None:
            raise RowNotFound(CITY_TABLENAME, CITY_NAME, cityName)

        # Drop Region ID and Region Name ID from Data Dictionary
        data.pop(DICT_REGION_ID)
        data.pop(DICT_REGION_NAME_ID)

        # Set City ID to Data Dictionary
        data[DICT_CITY_ID] = c.cityId

        return data

    # Get City Area Id based on its Name and the City Id where it's Located
    def getCityAreaId(self) -> dict | None:
        data = self.getCityId()
        areaSearch = Prompt.ask(self._getCityAreaMsg)

        # Check City Area Name
        isValueValid(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaSearch)

        # Check if City Area Search is Stored in Local Database
        areaNameId = self.__tables.getCityAreaSearchNameId(
            data[DICT_CITY_NAME_ID], areaSearch
        )
        data[DICT_CITY_AREA_NAME_ID] = areaNameId
        areaName = None

        # Check City Name ID
        if areaNameId != None:
            # Get City Name from Local Database
            areaName = self.__tables.getCityName(areaNameId)
            data[DICT_CITY_AREA_NAME] = areaName
        else:
            # Get City Area Name from GeoPy API based on the Name Provided
            areaName = self._geopyGeocoder.getCityArea(
                data,
                areaSearch,
            )
            data[DICT_CITY_AREA_NAME] = areaName

            # Store City Area Search at Local Database
            self.__tables.addCity(data[DICT_CITY_NAME_ID], areaSearch, areaName)

            # Get City Area Name ID from Local Database
            data[DICT_CITY_AREA_NAME_ID] = self.__tables.getCityAreaNameId(
                data[DICT_CITY_NAME_ID], areaName
            )

        # Get City Area
        a = self._cityAreaTable.find(data[DICT_CITY_ID], areaName)

        if a == None:
            raise RowNotFound(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaName)

        # Drop City ID and City Name ID from Data Dictionary
        data.pop(DICT_CITY_ID)
        data.pop(DICT_CITY_NAME_ID)

        # Set City Area ID to Data Dictionary
        data[DICT_CITY_AREA_ID] = a.areaId

        return data

    # Get All Table Handler
    def _allHandler(self, table: str) -> None:
        sortBy = None

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(self._allDescMsg)

        if table == COUNTRY_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Print Table
            self._countryTable.all(sortBy, desc)

        elif table == PROVINCE_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[
                    PROVINCE_ID,
                    PROVINCE_FK_COUNTRY,
                    PROVINCE_NAME,
                    PROVINCE_FK_AIR_FORWARDER,
                    PROVINCE_FK_OCEAN_FORWARDER,
                ],
            )

            # Print Table
            self._provinceTable.all(sortBy, desc)

        elif table == REGION_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[
                    REGION_ID,
                    REGION_FK_PROVINCE,
                    REGION_NAME,
                    REGION_FK_WAREHOUSE,
                ],
            )

            # Print Table
            self._regionTable.all(sortBy, desc)

        elif table == CITY_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME],
            )

            # Print Table
            self._cityTable.all(sortBy, desc)

        elif table == CITY_AREA_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[CITY_AREA_ID, CITY_AREA_FK_CITY, CITY_AREA_NAME],
            )

            # Print Table
            self._cityAreaTable.all(sortBy, desc)

    # Get Table Handler
    def _getHandler(self, table: str) -> None:
        field = value = None

        if table == COUNTRY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Prompt to Ask the Value to be Compared
            if field == COUNTRY_NAME:
                value = Prompt.ask(self._getValueMsg)

                # Check Value
                isValueValid(table, field, value)

            else:
                value = str(IntPrompt.ask(self._getValueMsg))

            # Print Table Coincidences
            self._countryTable.get(field, value)

        elif table == PROVINCE_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[
                    PROVINCE_ID,
                    PROVINCE_FK_COUNTRY,
                    PROVINCE_NAME,
                    PROVINCE_FK_AIR_FORWARDER,
                    PROVINCE_FK_OCEAN_FORWARDER,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == PROVINCE_NAME:
                value = Prompt.ask(self._getValueMsg)

                # Check Value
                isValueValid(table, field, value)

            else:
                value = str(IntPrompt.ask(self._getValueMsg))

            # Print Table Coincidences
            self._provinceTable.get(field, value)

        elif table == REGION_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[
                    REGION_ID,
                    REGION_FK_PROVINCE,
                    REGION_NAME,
                    REGION_FK_WAREHOUSE,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == REGION_NAME:
                value = Prompt.ask(self._getValueMsg)

                # Check Value
                isValueValid(table, field, value)

            else:
                value = str(IntPrompt.ask(self._getValueMsg))

            # Print Table Coincidences
            self._regionTable.get(field, value)

        elif table == CITY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_NAME:
                value = Prompt.ask(self._getValueMsg)

                # Check Value
                isValueValid(table, field, value)

            else:
                value = str(IntPrompt.ask(self._getValueMsg))

            # Print Table Coincidences
            self._cityTable.get(field, value)

        elif table == CITY_AREA_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[CITY_AREA_ID, CITY_AREA_FK_CITY, CITY_AREA_NAME],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_AREA_NAME:
                value = Prompt.ask(self._getValueMsg)

                # Check Value
                isValueValid(table, field, value)

            else:
                value = str(IntPrompt.ask(self._getValueMsg))

            # Print Table Coincidences
            self._cityAreaTable.get(field, value)

    # Modify Row from Table Handler
    def _modHandler(self, table: str) -> None:
        field = value = None
        countryId = provinceId = None

        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Modify
            countryId = IntPrompt.ask("\nEnter Country ID to Modify")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(self._modFieldMsg, choices=[COUNTRY_PHONE_PREFIX])

            # Prompt to Ask the New Value
            if field == COUNTRY_PHONE_PREFIX:
                value = str(IntPrompt.ask(self._modValueMsg))

            # Modify Country
            self._countryTable.modify(countryId, field, value)

        elif table == PROVINCE_TABLENAME:
            # Ask for Province ID to Modify
            provinceId = IntPrompt.ask("\nEnter Province ID to Modify")

            # Print Fetched Results
            if not self._provinceTable.get(PROVINCE_ID, provinceId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self._modFieldMsg,
                choices=[PROVINCE_FK_AIR_FORWARDER, PROVINCE_FK_OCEAN_FORWARDER],
            )

            # Prompt to Ask the New Value
            if (
                field == PROVINCE_FK_AIR_FORWARDER
                or field == PROVINCE_FK_OCEAN_FORWARDER
            ):
                value = str(IntPrompt.ask(self._modValueMsg))

            # TO DEVELOP: CHECK AND CONFIRM FORWARDERS

            # Modify Province
            self._provinceTable.modify(provinceId, field, value)

        elif table == REGION_TABLENAME:
            # Ask for Region ID to Modify
            regionId = IntPrompt.ask("\nEnter Region ID to Modify")

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self._modFieldMsg,
                choices=[REGION_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == REGION_FK_WAREHOUSE:
                value = str(IntPrompt.ask(self._modValueMsg))

            # TO DEVELOP: CHECK AND CONFIRM WAREHOUSE

            # Modify Region
            self._regionTable.modify(regionId, field, value)

        elif table == CITY_TABLENAME:
            console.print(self._noModMsg, style="warning")

        elif table == CITY_AREA_TABLENAME:
            # Ask for City Area ID to Modify
            areaId = IntPrompt.ask("\nEnter City Area ID to Modify")

            # Print Fetched Results
            if not self._cityTable.get(CITY_AREA_ID, areaId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self._modFieldMsg,
                choices=[CITY_AREA_DESCRIPTION],
            )

            # Prompt to Ask the New Value
            if field == CITY_AREA_DESCRIPTION:
                value = Prompt.ask(self._modValueMsg)

            # Modify City Area
            self._cityAreaTable.modify(areaId, field, value)

    # Add Row to Table Handler
    def _addHandler(self, table: str) -> None:
        if table == COUNTRY_TABLENAME:
            # Asks for Country Fields
            countrySearch = Prompt.ask(self._getCountryMsg)
            phonePrefix = IntPrompt.ask("Enter Phone Prefix")

            # Check Country Name
            isValueValid(table, COUNTRY_NAME, countrySearch)

            # Check if Country is Stored in Local Database
            countryNameId = self.__tables.getCountrySearchNameId(countrySearch)
            countryName = None

            # Check Country Name ID
            if countryNameId != None:
                # Get Country Name from Local Database
                countryName = self.__tables.getCountryName(countryNameId)
            else:
                # Get Country Name from GeoPy API based on the Name Provided
                countryName = self._geopyGeocoder.getCountry(countrySearch)

                # Store Country Search in Local Database
                self.__tables.addCountry(countrySearch, countryName)

            # Check if Country Name has already been Inserted
            if self._countryTable.get(COUNTRY_NAME, countryName):
                uniqueInserted(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)
                return

            # Insert Country
            self._countryTable.add(Country(countryName, phonePrefix))

        elif table == PROVINCE_TABLENAME:
            # Asks for Province Fields
            data = self.getCountryId()
            provinceSearch = Prompt.ask(self._getProvinceMsg)

            # Check Province Name
            isValueValid(table, PROVINCE_NAME, provinceSearch)

            # Check if Province is Stored in Local Database
            provinceNameId = self.__tables.getProvinceSearchNameId(
                data[DICT_COUNTRY_NAME_ID], provinceSearch
            )
            provinceName = None

            # Check Province Name ID
            if provinceNameId != None:
                # Get Province Name from Local Database
                provinceName = self.__tables.getProvinceName(provinceNameId)
            else:
                # Get Province Name from GeoPy API based on the Name Provided
                provinceName = self._geopyGeocoder.getProvince(data, provinceSearch)

                # Store Province Search in Local Database
                self.__tables.addProvince(
                    data[DICT_COUNTRY_NAME_ID], provinceSearch, provinceName
                )

            provinceFields = [PROVINCE_FK_COUNTRY, PROVINCE_NAME]
            provinceValues = [data[DICT_COUNTRY_ID], provinceName]

            # Check if Province Name has already been Inserted for the Given Country
            if self._provinceTable.getMult(provinceFields, provinceValues):
                uniqueInsertedMult(PROVINCE_TABLENAME, provinceFields, provinceValues)
                return

            # Insert Province
            self._provinceTable.add(Province(provinceName, data[DICT_COUNTRY_ID]))

        elif table == REGION_TABLENAME:
            # Asks for Region Fields
            data = self.getProvinceId()
            regionSearch = Prompt.ask(self._getRegionMsg)

            # Check Region Name
            isValueValid(table, REGION_NAME, regionSearch)

            # Check if Region is Stored in Local Database
            regionNameId = self.__tables.getRegionSearchNameId(
                data[DICT_PROVINCE_NAME_ID], regionSearch
            )
            regionName = None

            # Check Region Name ID
            if regionNameId != None:
                # Get Region Name from Local Database
                regionName = self.__tables.getRegionName(regionNameId)
            else:
                # Get Region Name from GeoPy API based on the Name Provided
                regionName = self._geopyGeocoder.getRegion(data, regionSearch)

                # Store Region Search in Local Database
                self.__tables.addRegion(
                    data[DICT_PROVINCE_NAME_ID], regionSearch, regionName
                )

            regionFields = [REGION_FK_PROVINCE, REGION_NAME]
            regionValues = [data[DICT_PROVINCE_ID], regionName]

            # Check if Region Name has already been Inserted for the Given Province
            if self._regionTable.getMult(regionFields, regionValues):
                uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
                return

            # Insert Region
            self._regionTable.add(Region(regionName, data[DICT_PROVINCE_ID]))

        elif table == CITY_TABLENAME:
            # Asks for City Fields
            data = self.getRegionId()
            citySearch = Prompt.ask(self._getCityMsg)

            # Check City Name
            isValueValid(table, CITY_NAME, citySearch)

            # Check if City is Stored in Local Database
            cityNameId = self.__tables.getCitySearchNameId(
                data[DICT_REGION_NAME_ID], citySearch
            )
            cityName = None

            # Check City Name ID
            if cityNameId != None:
                # Get City Name from Local Database
                cityName = self.__tables.getCityName(cityNameId)
            else:
                # Get City Name from GeoPy API based on the Name Provided
                cityName = self._geopyGeocoder.getCity(data, citySearch)

                # Store City Search in Local Database
                self.__tables.addCity(data[DICT_REGION_NAME_ID], citySearch, cityName)

            cityFields = [CITY_FK_REGION, CITY_NAME]
            cityValues = [data[DICT_REGION_ID], cityName]

            # Check if City Name has already been Inserted for the Given Province
            if self._cityTable.getMult(cityFields, cityValues):
                uniqueInsertedMult(CITY_TABLENAME, cityFields, cityValues)
                return

            # Insert City
            self._cityTable.add(City(cityName, data[DICT_REGION_ID]))

        elif table == CITY_AREA_TABLENAME:
            # Asks for City Area Fields
            data = self.getCityId()
            areaSearch = Prompt.ask(self._getCityAreaMsg)
            areaDescription = Prompt.ask("Enter City Area Description")

            # Check City Area Name and Description
            isValueValid(table, CITY_AREA_NAME, areaSearch)
            isValueValid(table, CITY_AREA_DESCRIPTION, areaDescription)

            # Check if City Area is Stored in Local Database
            areaNameId = self.__tables.getCityAreaSearchNameId(data, areaSearch)
            areaName = None

            # Check City Area Name ID
            if areaNameId != None:
                # Get City Area Name from Local Database
                areaName = self.__tables.getCityAreaName(areaNameId)
            else:
                # Get City Area Name from GeoPy API based on the Name Provided
                areaName = self._geopyGeocoder.getCityArea(data, areaSearch)

                # Store City Area Search in Local Database
                self.__tables.addCityArea(data[DICT_CITY_NAME_ID], areaSearch, areaName)

            areaFields = [CITY_AREA_FK_CITY, CITY_AREA_NAME]
            areaValues = [data[DICT_CITY_ID], areaName]

            # Check if City Area Name has already been Inserted for the Given City
            if self._cityAreaTable.getMult(areaFields, areaValues):
                uniqueInsertedMult(CITY_AREA_TABLENAME, areaFields, areaValues)
                return

            # Insert City Area
            self._cityAreaTable.add(
                CityArea(areaName, areaDescription, data[DICT_CITY_ID])
            )

    # Remove Row from Table Handler
    def _rmHandler(self, table: str) -> None:
        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Remove
            countryId = IntPrompt.ask("\nEnter Country ID to Remove")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._countryTable.remove(countryId)

        elif table == PROVINCE_TABLENAME:
            # Ask for Province ID to Remove
            provinceId = IntPrompt.ask("\nEnter Province ID to Remove")

            # Print Fetched Results
            if not self._provinceTable.get(PROVINCE_ID, provinceId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._provinceTable.remove(provinceId)

        elif table == REGION_TABLENAME:
            # Ask for Region ID to Remove
            regionId = IntPrompt.ask("\nEnter Region ID to Remove")

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._regionTable.remove(regionId)

        elif table == CITY_TABLENAME:
            # Ask for City ID to Remove
            cityId = IntPrompt.ask("\nEnter City ID to Remove")

            # Print Fetched Results
            if not self._cityTable.get(CITY_ID, cityId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._cityTable.remove(cityId)

        elif table == CITY_AREA_TABLENAME:
            # Ask for City Area ID to Remove
            areaId = IntPrompt.ask("\nEnter City Area ID to Remove")

            # Print Fetched Results
            if not self._cityAreaTable.get(CITY_AREA_ID, areaId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._cityAreaTable.remove(areaId)

    # Territory Event Handler
    def handler(self, action: str, table: str) -> None:
        if action == ALL:
            self._allHandler(table)

        elif action == GET:
            self._getHandler(table)

        elif action == MOD:
            self._modHandler(table)

        elif action == ADD:
            self._addHandler(table)

        elif action == RM:
            self._rmHandler(table)

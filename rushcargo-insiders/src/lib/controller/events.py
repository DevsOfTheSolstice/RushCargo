from rich.prompt import Prompt, IntPrompt, Confirm
import logging
from rich.logging import RichHandler

from ..model.database import *
from ..model.database_locations import *

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
        self.__db, self.__user, self.__arcGisApiKey = initDb()

        # Initialize Event Hanlder Classes
        self.__initHandlers()

    # Initialize Event Handler Classes
    def __initHandlers(self):
        self.__territoryEventHandler = TerritoryEventHandler(
            self.__db, self.__user, self.__arcGisApiKey
        )

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
    _regionTable = None
    _subregionTable = None
    _cityTable = None
    _cityAreaTable = None

    # Geocoders
    _geopyGeocoder = None

    # ArcGIS Credentials
    _arcGisApiKey = None

    # Constructor
    def __init__(self, db: Database, user: str, arcGisApiKey: str):
        # Initialize Table Classes
        self._countryTable = CountryTable(db)
        self._regionTable = RegionTable(db)
        self._subregionTable = SubregionTable(db)
        self._cityTable = CityTable(db)
        self._cityAreaTable = CityAreaTable(db)

        # Initialize Geocoders
        self._geopyGeocoder = initGeopyGeocoder(NOMINATIM_USER_AGENT, user)
        self._arcGisApiKey = arcGisApiKey

    # Get Country Id and Name
    def getCountryId(self) -> tuple:
        countryName = Prompt.ask("\nEnter Country Name")

        # Check Country Name
        isValueValid(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

        # Get Country Name from Geopy API based on the Name Provided
        countryName = self._geopyGeocoder.getCountry(countryName)

        # Get Country
        c = self._countryTable.find(COUNTRY_NAME, countryName)

        if c == None:
            raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

        return c.countryId, countryName

    # Get Region Id based on its Name and the Country Id where it's Located
    def getRegionId(self) -> tuple:
        countryId, countryName = self.getCountryId()
        regionName = Prompt.ask("Enter Region Name")

        # Check Region Name
        isValueValid(REGION_TABLENAME, REGION_NAME, regionName)

        # Get Region Name from Geopy API on the Name Provided
        regionName = self._geopyGeocoder.getRegion(countryName, regionName)

        # Get Region
        r = self._regionTable.find(countryId, regionName)

        if r == None:
            raise RowNotFound(REGION_TABLENAME, REGION_NAME, regionName)

        return countryName, r.regionId, regionName

    # Get Subregion Id based on its Name and the Region Id where it's Located
    def getSubregionId(self) -> tuple | None:
        countryName, regionId, regionName = self.getRegionId()
        subregionName = Prompt.ask("Enter Subregion Name")

        # Check Subregion Name
        isValueValid(SUBREGION_TABLENAME, SUBREGION_NAME, subregionName)

        # Get Subregion Name from Geopy API based on the Name Provided
        subregionName = self._geopyGeocoder.getSubregion(
            countryName, regionName, subregionName
        )

        # Get Subregion
        s = self._subregionTable.find(regionId, subregionName)

        if s == None:
            raise RowNotFound(SUBREGION_TABLENAME, SUBREGION_NAME, subregionName)

        return countryName, regionName, s.subregionId, subregionName

    # Get City Id based on its Name and the Subregion Id where it's Located
    def getCityId(self) -> int:
        countryName, regionName, subregionId, subregionName = self.getSubregionId()
        cityName = Prompt.ask("Enter City Name")

        # Check City Name
        isValueValid(CITY_TABLENAME, CITY_NAME, cityName)

        # Get City Name from Geopy API based on the Name Provided
        cityName = self._geopyGeocoder.getCity(
            countryName, regionName, subregionName, cityName
        )

        # Get City
        c = self._cityTable.find(subregionId, cityName)

        if c == None:
            raise RowNotFound(CITY_TABLENAME, CITY_NAME, cityName)

        return countryName, regionName, subregionName, c.cityId, cityName

    # Get City Area Id based on its Name and the City Id where it's Located
    def getCityAreaId(self) -> int:
        countryName, regionName, subregionName, cityId, cityName = self.getCityId()
        areaName = Prompt.ask("Enter City Area Name")

        # Check City Area Name
        isValueValid(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaName)

        # Get City Area Name from Geopy API based on the Name Provided
        cityName = self._geopyGeocoder.getCityArea(
            countryName, regionName, subregionName, cityName, areaName
        )

        # Get City Area
        a = self._cityAreaTable.find(cityId, areaName)

        if a == None:
            raise RowNotFound(CITY_AREA_TABLENAME, CITY_AREA_NAME, areaName)

        return countryName, regionName, subregionName, cityName, a.areaId, areaName

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

        elif table == REGION_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[
                    REGION_ID,
                    REGION_FK_COUNTRY,
                    REGION_NAME,
                    REGION_FK_AIR_FORWARDER,
                    REGION_FK_OCEAN_FORWARDER,
                ],
            )

            # Print Table
            self._regionTable.all(sortBy, desc)

        elif table == SUBREGION_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[
                    SUBREGION_ID,
                    SUBREGION_FK_REGION,
                    SUBREGION_NAME,
                    SUBREGION_FK_WAREHOUSE,
                ],
            )

            # Print Table
            self._subregionTable.all(sortBy, desc)

        elif table == CITY_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self._allSortByMsg,
                choices=[CITY_ID, CITY_FK_SUBREGION, CITY_NAME],
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

        elif table == REGION_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[
                    REGION_ID,
                    REGION_FK_COUNTRY,
                    REGION_NAME,
                    REGION_FK_AIR_FORWARDER,
                    REGION_FK_OCEAN_FORWARDER,
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

        elif table == SUBREGION_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[
                    SUBREGION_ID,
                    SUBREGION_FK_REGION,
                    SUBREGION_NAME,
                    SUBREGION_FK_WAREHOUSE,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == SUBREGION_NAME:
                value = Prompt.ask(self._getValueMsg)

                # Check Value
                isValueValid(table, field, value)

            else:
                value = str(IntPrompt.ask(self._getValueMsg))

            # Print Table Coincidences
            self._subregionTable.get(field, value)

        elif table == CITY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self._getFieldMsg,
                choices=[CITY_ID, CITY_FK_SUBREGION, CITY_NAME],
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
        countryId = regionId = None

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
                choices=[REGION_FK_AIR_FORWARDER, REGION_FK_OCEAN_FORWARDER],
            )

            # Prompt to Ask the New Value
            if field == REGION_FK_AIR_FORWARDER or field == REGION_FK_OCEAN_FORWARDER:
                value = str(IntPrompt.ask(self._modValueMsg))

            # TO DEVELOP: CHECK AND CONFIRM FORWARDERS

            # Modify Region
            self._regionTable.modify(regionId, field, value)

        elif table == SUBREGION_TABLENAME:
            # Ask for Subregion ID to Modify
            subregionId = IntPrompt.ask("\nEnter Subregion ID to Modify")

            # Print Fetched Results
            if not self._subregionTable.get(SUBREGION_ID, subregionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self._modFieldMsg,
                choices=[SUBREGION_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == SUBREGION_FK_WAREHOUSE:
                value = str(IntPrompt.ask(self._modValueMsg))

            # TO DEVELOP: CHECK AND CONFIRM WAREHOUSE

            # Modify Subregion
            self._subregionTable.modify(subregionId, field, value)

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
            countryName = Prompt.ask("\nEnter Country Name")
            phonePrefix = IntPrompt.ask("Enter Phone Prefix")

            # Check Country Name
            isValueValid(table, COUNTRY_NAME, countryName)

            # Check if Country Name has already been Inserted
            if self._countryTable.get(COUNTRY_NAME, countryName):
                uniqueInserted(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)
                return

            # Check if Country Phone Prefix has already been Inserted
            if self._countryTable.get(COUNTRY_PHONE_PREFIX, phonePrefix):
                uniqueInserted(COUNTRY_TABLENAME, COUNTRY_PHONE_PREFIX, phonePrefix)
                return

            # Get Country Name from Geopy API based on the Name Provided
            countryName = self._geopyGeocoder.getCountry(countryName)

            # Insert Country
            self._countryTable.add(Country(countryName, phonePrefix))

        elif table == REGION_TABLENAME:
            # Asks for Region Fields
            countryId, countryName = self.getCountryId()
            regionName = Prompt.ask("Enter Region Name")

            # Check Region Name
            isValueValid(table, REGION_NAME, regionName)

            regionFields = [REGION_FK_COUNTRY, REGION_NAME]
            regionValues = [countryId, regionName]

            # Check if Region Name has already been Inserted for the Given Country
            if self._regionTable.getMult(regionFields, regionValues):
                uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
                return

            # Get Region Name from Geopy API based on the Name Provided
            regionName = self._geopyGeocoder.getRegion(countryName, regionName)

            # Insert Region
            self._regionTable.add(Region(regionName, countryId))

        elif table == SUBREGION_TABLENAME:
            # Asks for Subregion Fields
            countryName, regionId, regionName = self.getRegionId()
            subregionName = Prompt.ask("Enter Subregion Name")

            # Check Subregion Name
            isValueValid(table, SUBREGION_NAME, subregionName)

            subregionFields = [SUBREGION_FK_REGION, SUBREGION_NAME]
            subregionValues = [regionId, subregionName]

            # Check if Subregion Name has already been Inserted for the Given Region
            if self._subregionTable.getMult(subregionFields, subregionValues):
                uniqueInsertedMult(
                    SUBREGION_TABLENAME, subregionFields, subregionValues
                )
                return

            # Get Subregion Name from Geopy API based on the Name Provided
            subregionName = self._geopyGeocoder.getSubregion(
                countryName, regionName, subregionName
            )

            # Insert Subregion
            self._subregionTable.add(Subregion(subregionName, regionId))

        elif table == CITY_TABLENAME:
            # Asks for City Fields
            countryName, regionName, subregionId, subregionName = self.getSubregionId()
            cityName = Prompt.ask("Enter City Name")

            # Check City Name
            isValueValid(table, CITY_NAME, cityName)

            cityFields = [CITY_FK_SUBREGION, CITY_NAME]
            cityValues = [subregionId, cityName]

            # Check if City Name has already been Inserted for the Given Region
            if self._cityTable.getMult(cityFields, cityValues):
                uniqueInsertedMult(CITY_TABLENAME, cityFields, cityValues)
                return

            # Get City Name from Geopy API based on the Name Provided
            cityName = self._geopyGeocoder.getCity(
                countryName, regionName, subregionName, cityName
            )

            # Insert City
            self._cityTable.add(City(cityName, subregionId))

        elif table == CITY_AREA_TABLENAME:
            # Asks for City Area Fields
            countryName, regionName, subregionName, cityId, cityName = self.getCityId()
            areaName = Prompt.ask("Enter City Area Name")
            areaDescription = Prompt.ask("Enter City Area Description")

            # Check City Area Name and Description
            isValueValid(table, CITY_AREA_NAME, areaName)
            isValueValid(table, CITY_AREA_DESCRIPTION, areaDescription)

            areaFields = [CITY_AREA_FK_CITY, CITY_AREA_NAME]
            areaValues = [cityId, areaName]

            # Check if City Area Name has already been Inserted for the Given City
            if self._cityAreaTable.getMult(areaFields, areaValues):
                uniqueInsertedMult(CITY_AREA_TABLENAME, areaFields, areaValues)
                return

            # Get City Area Name from Geopy API based on the Name Provided
            areaName = self._geopyGeocoder.getCityArea(
                countryName, regionName, subregionName, cityName, areaName
            )

            # Insert City Area
            self._cityAreaTable.add(CityArea(areaName, areaDescription, cityId))

    # Remove Row from Table Handler
    def _rmHandler(self, table: str) -> None:
        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Remove
            countryID = IntPrompt.ask("\nEnter Country ID to Remove")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryID):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._countryTable.remove(countryID)

        elif table == REGION_TABLENAME:
            # Ask for Region ID to Remove
            regionID = IntPrompt.ask("\nEnter Region ID to Remove")

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionID):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._regionTable.remove(regionID)

        elif table == SUBREGION_TABLENAME:
            # Ask for Subregion ID to Remove
            subregionId = IntPrompt.ask("\nEnter Subregion ID to Remove")

            # Print Fetched Results
            if not self._subregionTable.get(SUBREGION_ID, subregionId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self._rmConfirmMsg):
                return

            self._subregionTable.remove(subregionId)

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

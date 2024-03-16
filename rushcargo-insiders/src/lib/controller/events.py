from rich.prompt import Prompt, IntPrompt, Confirm
import os
import logging
from rich.logging import RichHandler

from ..model.database import *
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
    _db = None

    # Table Classes
    _countryTable = None
    _regionTable = None
    _cityTable = None

    # All Handler Messages
    __allSortByMsg = "How do you want to Sort it?"
    __allDescMsg = "\nDo you want to Sort it in Descending Order?"

    # Get Handler Messages
    __getFieldMsg = "\nWhich Field do you want to Compare?"
    __getValueMsg = "Which Value do you want to Compare that Field with?"

    # Modify Handler Messages
    __modConfirmMsg = "Is this the Row you want to Modify?"
    __modFieldMsg = "Which Field do you want to Modify?"
    __modValueMsg = "Which New Value do you want to Assign it?"

    # Remove Handler Messages
    __rmConfirmMsg = "Is this the Row you want to Remove?"

    # Constructor
    def __init__(self):
        # Initialize Database Connection
        self._db = initdb()

        # Initialize Table Classes
        self.__initTables()

    # Initialize Table Classes
    def __initTables(self):
        # Initialize Table Classes
        self._countryTable = CountryTable(self._db)
        self._regionTable = RegionTable(self._db)
        self._cityTable = CityTable(self._db)

    # Get All Table Handler
    def _allHandler(self, table: str):
        sortBy = None

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(self.__allDescMsg)

        if table == COUNTRY_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self.__allSortByMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Print Table
            self._countryTable.all(sortBy, desc)

        elif table == REGION_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self.__allSortByMsg,
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

        elif table == CITY_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self.__allSortByMsg,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME, CITY_FK_WAREHOUSE],
            )

            # Print Table
            self._cityTable.all(sortBy, desc)

    # Get Table Handler
    def _getHandler(self, table: str):
        field = value = None

        if table == COUNTRY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self.__getFieldMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Prompt to Ask the Value to be Compared
            if field == COUNTRY_NAME:
                value = Prompt.ask(self.__getValueMsg)

                # Check Value
                if not checkTableField(table, field, value):
                    raise ValueError(table, field, value)

            else:
                value = str(IntPrompt.ask(self.__getValueMsg))

            # Print Table Coincidences
            self._countryTable.get(field, value)

        elif table == REGION_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self.__getFieldMsg,
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
                value = Prompt.ask(self.__getValueMsg)

                # Check Value
                if not checkTableField(table, field, value):
                    raise ValueError(table, field, value)

            else:
                value = str(IntPrompt.ask(self.__getValueMsg))

            # Print Table Coincidences
            self._regionTable.get(field, value)

        elif table == CITY_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                self.__getFieldMsg,
                choices=[CITY_ID, CITY_FK_REGION, CITY_NAME, CITY_FK_WAREHOUSE],
            )

            # Prompt to Ask the Value to be Compared
            if field == CITY_NAME:
                value = Prompt.ask(self.__getValueMsg)

                # Check Value
                if not checkTableField(table, field, value):
                    raise ValueError(table, field, value)

            else:
                value = str(IntPrompt.ask(self.__getValueMsg))

            # Print Table Coincidences
            self._cityTable.get(field, value)

    # Modify Row from Table Handler
    def _modHandler(self, table: str):
        field = value = None
        countryId = regionId = None

        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Modify
            countryId = IntPrompt.ask("\nEnter Country ID to Modify")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryId):
                noCoincidenceFetched()

            # Ask for Confirmation
            if not Confirm.ask(self.__modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(self.__modFieldMsg, choices=[COUNTRY_PHONE_PREFIX])

            # Prompt to Ask the New Value
            if field == COUNTRY_PHONE_PREFIX:
                value = str(IntPrompt.ask(self.__modValueMsg))

            # Modify Country
            self._countryTable.modify(countryId, field, value)

        elif table == REGION_TABLENAME:
            # Ask for Region ID to Modify
            regionId = IntPrompt.ask("\nEnter Region ID to Modify")

            # Print Fetched Results
            if not self._regionTable.get(REGION_ID, regionId):
                noCoincidenceFetched()

            # Ask for Confirmation
            if not Confirm.ask(self.__modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self.__modFieldMsg,
                choices=[REGION_FK_AIR_FORWARDER, REGION_FK_OCEAN_FORWARDER],
            )

            # Prompt to Ask the New Value
            if field == REGION_FK_AIR_FORWARDER or field == REGION_FK_OCEAN_FORWARDER:
                value = str(IntPrompt.ask(self.__modValueMsg))

            # TO DEVELOP: CHECK AND CONFIRM FORWARDERS

            # Modify Region
            self._regionTable.modify(regionId, field, value)

        elif table == CITY_TABLENAME:
            # Ask for City ID to Modify
            cityId = IntPrompt.ask("\nEnter City ID to Modify")

            # Print Fetched Results
            if not self._cityTable.get(CITY_ID, cityId):
                noCoincidenceFetched()

            # Ask for Confirmation
            if not Confirm.ask(self.__modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self.__modFieldMsg,
                choices=[CITY_FK_WAREHOUSE],
            )

            # Prompt to Ask the New Value
            if field == CITY_FK_WAREHOUSE:
                value = str(IntPrompt.ask(self.__modValueMsg))

            # TO DEVELOP: CHECK AND CONFIRM WAREHOUSE

            # Modify City
            self._cityTable.modify(cityId, field, value)

    # Add Row to Table Handler
    def _addHandler(self, table: str):
        if table == COUNTRY_TABLENAME:
            # Asks for Country Fields
            countryName = Prompt.ask("\nEnter Country Name")
            phonePrefix = IntPrompt.ask("Enter Phone Prefix")

            # Check Country Name
            if not checkTableField(table, COUNTRY_NAME, countryName):
                raise ValueError(table, COUNTRY_NAME, countryName)

            # Check if Country Name has already been Inserted
            if self._countryTable.get(COUNTRY_NAME, countryName):
                uniqueInserted(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)
                return

            # Check if Country Phone Prefix has already been Inserted
            if self._countryTable.get(COUNTRY_PHONE_PREFIX, phonePrefix):
                uniqueInserted(COUNTRY_TABLENAME, COUNTRY_PHONE_PREFIX, phonePrefix)
                return

            # Insert Country
            self._countryTable.add(Country(countryName, phonePrefix))

        elif table == REGION_TABLENAME:
            # Asks for Region Fields
            countryName = Prompt.ask("\nEnter Country Name where the Region is Located")
            regionName = Prompt.ask("Enter Region Name")

            # Check Country Name
            if not checkTableField(COUNTRY_TABLENAME, COUNTRY_NAME, countryName):
                raise ValueError(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

            # Check Region Name
            if not checkTableField(table, REGION_NAME, regionName):
                raise ValueError(table, REGION_NAME, regionName)

            # Get Country based on the Name Provided
            country = self._countryTable.find(COUNTRY_NAME, countryName)

            if country == None:
                raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

            # Get Country ID
            countryId = country.countryId

            regionFields = [REGION_FK_COUNTRY, REGION_NAME]
            regionValues = [countryId, regionName]

            # Check if Region Name has already been Inserted for the Given Country
            if self._regionTable.getMult(regionFields, regionValues):
                uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
                return

            # Insert Region
            self._regionTable.add(Region(regionName, countryId))

        elif table == CITY_TABLENAME:
            # Asks for City Fields
            countryName = Prompt.ask("\nEnter Country Name where the City is Located")
            regionName = Prompt.ask("Enter Region Name where the City is Located")
            cityName = Prompt.ask("Enter City Name")

            # Check Country Name
            if not checkTableField(COUNTRY_TABLENAME, COUNTRY_NAME, countryName):
                raise ValueError(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

            # Check Region Name
            if not checkTableField(REGION_TABLENAME, REGION_NAME, regionName):
                raise ValueError(REGION_TABLENAME, REGION_NAME, regionName)

            # Check City Name
            if not checkTableField(table, CITY_NAME, cityName):
                raise ValueError(table, CITY_NAME, cityName)

            # Get Country based on the Name Provided
            c = self._countryTable.find(COUNTRY_NAME, countryName)

            if c == None:
                raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

            # Get Region based on the Name Provided and the Country Id
            r = self._regionTable.find(c.countryId, regionName)

            if r == None:
                raise RowNotFound(REGION_TABLENAME, REGION_NAME, regionName)

            # Get Region ID
            regionId = r.regionId

            cityFields = [CITY_FK_REGION, CITY_NAME]
            cityValues = [regionId, cityName]

            # Check if City Name has already been Inserted for the Given Region
            if self._cityTable.getMult(cityFields, cityValues):
                uniqueInsertedMult(CITY_TABLENAME, cityFields, cityValues)
                return

            # Insert City
            self._cityTable.add(City(cityName, regionId))

    # Remove Row from Table Handler
    def _rmHandler(self, table: str):
        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Remove
            countryID = IntPrompt.ask("\nEnter Country ID to Remove")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryID):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self.__rmConfirmMsg):
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
            if not Confirm.ask(self.__rmConfirmMsg):
                return

            self._regionTable.remove(regionID)

        elif table == CITY_TABLENAME:
            # Ask for City ID to Remove
            cityId = IntPrompt.ask("\nEnter City ID to Remove")

            # Print Fetched Results
            if not self._cityTable.get(CITY_ID, cityId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(self.__rmConfirmMsg):
                return

            self._cityTable.remove(cityId)

    # Main Event Handler
    def mainHandler(self, action: str, table: str):
        try:
            while True:
                try:
                    # Print All Rows from Given Table
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

                except Exception as err:
                    console.print(err, style="warning")

                # Stop Program Flow
                Prompt.ask("\nPress ENTER to Continue")

                # Clear Screen
                clear()

                # Ask Next Action
                action = Prompt.ask("\nWhat do you want to do?", choices=ACTION_CMDS)

                # Check if the User wants to Exit the Program
                if action == EXIT:
                    break

                table = Prompt.ask("At which table?", choices=TABLE_CMDS)
        except KeyboardInterrupt:
            return

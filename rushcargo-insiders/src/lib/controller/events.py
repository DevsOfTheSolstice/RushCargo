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

    # All Handler Messages
    __allSortByMsg = "\nHow do you want to Sort it?"
    __allDescMsg = "Do you want to Sort it in Descending Order?"

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

    # Get All Table Handler
    def _allHandler(self, table: str):
        sortBy = desc = None

        if table == COUNTRY_TABLENAME:
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self.__allSortByMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )
            desc = Confirm.ask(self.__allDescMsg)

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
            desc = Confirm.ask(self.__allDescMsg)

            # Print Table
            self._regionTable.all(sortBy, desc)

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

            # Modify Country
            self._countryTable.modify(regionId, field, value)

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

            # Get Country ID
            country = self._countryTable.find(COUNTRY_NAME, countryName)

            if country == None:
                raise RowNotFound(COUNTRY_TABLENAME, COUNTRY_NAME, countryName)

            countryId = country.countryId

            regionFields = [REGION_FK_COUNTRY, REGION_NAME]
            regionValues = [countryId, regionName]

            # Check if Region Name has already been Inserted for the Given Country
            if self._regionTable.getMult(regionFields, regionValues):
                uniqueInsertedMult(REGION_TABLENAME, regionFields, regionValues)
                return

            # Insert Region
            self._regionTable.add(Region(regionName, countryId))

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

            # Ask for Confirmation
            if Confirm.ask("\nAre you Sure to Remove this Country?"):
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

            # Ask for Confirmation
            if Confirm.ask("\nAre you Sure to Remove this Region?"):
                self._regionTable.remove(regionID)

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

                # Ask if the User wants to Exit the Program
                exit = Confirm.ask("\nDo you want to End the Current Session?")

                if exit:
                    break

                # Clear Screen
                clear()

                # Ask Next Action
                action = Prompt.ask("\nWhat do you want to do?", choices=ACTION_CMDS)
                table = Prompt.ask("At which table?", choices=TABLE_CMDS)
        except KeyboardInterrupt:
            console.print("\nExiting...", style="warning")

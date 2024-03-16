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
            # Asks for Sort Order
            sortBy = Prompt.ask(
                self.__allSortByMsg,
                choices=[
                    REGION_FK_COUNTRY,
                    REGION_FK_AIR_FORWARDER,
                    REGION_FK_OCEAN_FORWARDER,
                    REGION_ID,
                    REGION_NAME,
                ],
            )
            desc = Confirm.ask(self.__allDescMsg)

            # Print Table
            self._countryTable.all(sortBy, desc)

    # Get Table Handler
    def _getHandler(self, table: str):
        field = value = None

        if table == COUNTRY_TABLENAME:
            # Asks for Sort Order
            field = Prompt.ask(
                self.__getFieldMsg,
                choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
            )

            # Prompt to Ask the Value to be Compared
            if field == COUNTRY_ID or field == COUNTRY_PHONE_PREFIX:
                value = str(IntPrompt.ask(self.__getValueMsg))

            elif field == COUNTRY_NAME:
                value = Prompt.ask(self.__getValueMsg)

                # Check Value
                if not checkTableField(table, field, value):
                    raise ValueError(table, field, value)

            # Print Table Coincidences
            self._countryTable.get(field, value)

    # Modify Row from Table Handler
    def _modHandler(self, table: str):
        countryID = field = value = None

        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Modify
            countryID = IntPrompt.ask("\nEnter Country ID to Modify")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryID):
                noCoincidenceFetched()

            # Ask for Confirmation
            if not Confirm.ask(self.__modConfirmMsg):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                self.__modFieldMsg, choices=[COUNTRY_NAME, COUNTRY_PHONE_PREFIX]
            )

            # Prompt to Ask the New Value
            if COUNTRY_PHONE_PREFIX:
                value = str(IntPrompt.ask(self.__modValueMsg))

            elif field == COUNTRY_NAME:
                value = Prompt.ask(self.__modValueMsg)

                # Check Value
                if not checkTableField(table, field, value):
                    raise ValueError(table, field, value)

            # Modify Country
            self._countryTable.modify(countryID, field, value)

    # Add Row to Table Handler
    def addHandler(self, table: str):
        if table == COUNTRY_TABLENAME:
            # Asks for Country Fields
            countryName = Prompt.ask("\nEnter Country Name")
            phonePrefix = IntPrompt.ask("Enter Phone Prefix")

            # Check Country Name
            if not checkTableField(table, COUNTRY_NAME, countryName):
                raise ValueError(table, COUNTRY_NAME, countryName)

            # Insert Country
            self._countryTable.add(Country(countryName, phonePrefix))

    # Remove Row from Table Handler
    def _rmHandler(self, table: str):
        if table == COUNTRY_TABLENAME:
            # Ask for Country ID to Modify
            countryID = IntPrompt.ask("\nEnter Country ID to Remove")

            # Print Fetched Results
            if not self._countryTable.get(COUNTRY_ID, countryID):
                noCoincidenceFetched()

            # Ask for Confirmation
            if not Confirm.ask(self.__rmConfirmMsg):
                return

            # Ask for Confirmation
            if Confirm.ask("\nAre you Sure to Remove this Country?"):
                self._countryTable.remove(countryID)

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
                    log.exception(err)

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

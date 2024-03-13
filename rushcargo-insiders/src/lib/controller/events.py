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

# Initialize Database Connection
db = initdb()

# Initialize Table Classes
countryTable = CountryTable(db)
# regionTable = RegionTable(db)


# Clear Function
def clear():
    # For Windows
    if os.name == "nt":
        os.system("cls")

    # For Posix
    else:
        os.system("clear")


# Get All Table Handler
def allHandler(table: str):
    sortBy = desc = None

    if table == COUNTRY_TABLENAME:
        # Asks for Sort Order
        sortBy = Prompt.ask(
            "\nHow do you want to Sort it?",
            choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
        )
        desc = Confirm.ask("Do you want to Sort it in Descending Order?")

        # Print Table
        countryTable.all(sortBy, desc)


# Get Table Handler
def getHandler(table: str):
    fieldMsg = "\nWhich Field do you want to Compare?"
    valueMsg = "Which Value do you want to Compare that Field with?"

    field = value = None

    if table == COUNTRY_TABLENAME:
        # Asks for Sort Order
        field = Prompt.ask(
            fieldMsg, choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX]
        )

        # Prompt to Ask the Value to be Compared
        if field == COUNTRY_ID or field == COUNTRY_PHONE_PREFIX:
            value = str(IntPrompt.ask(valueMsg))

        elif field == COUNTRY_NAME:
            value = Prompt.ask(valueMsg)

            # Check Value
            if not checkTableField(table, field, value):
                raise ValueError(table, field, value)

        # Print Table Coincidences
        countryTable.get(field, value)


# Modify Row from Table Handler
def modHandler(table: str):
    confirmMsg = "Is this the Row you want to Modify?"
    fieldMsg = "Which Field do you want to Modify?"
    valueMsg = "Which New Value do you want to Assign it?"

    countryID = field = value = None

    if table == COUNTRY_TABLENAME:
        # Ask for Country ID to Modify
        countryID = IntPrompt.ask("\nEnter Country ID to Modify")

        # Ask for Confirmation
        countryTable.get(COUNTRY_ID, countryID)
        if not Confirm.ask(confirmMsg):
            return

        # Ask for Field to Modify
        field = Prompt.ask(fieldMsg, choices=[COUNTRY_NAME, COUNTRY_PHONE_PREFIX])

        # Prompt to Ask the New Value
        if COUNTRY_PHONE_PREFIX:
            value = str(IntPrompt.ask(valueMsg))

        elif field == COUNTRY_NAME:
            value = Prompt.ask(valueMsg)

            # Check Value
            if not checkTableField(table, field, value):
                raise ValueError(table, field, value)

        # Modify Country
        countryTable.modify(countryID, field, value)


# Add Row to Table Handler
def addHandler(table: str):
    if table == COUNTRY_TABLENAME:
        # Asks for Country Fields
        countryName = Prompt.ask("\nEnter Country Name")
        phonePrefix = IntPrompt.ask("Enter Phone Prefix")

        # Check Country Name
        if not checkTableField(table, COUNTRY_NAME, countryName):
            raise ValueError(table, COUNTRY_NAME, countryName)

        # Insert Country
        countryTable.add(Country(countryName, phonePrefix))


# Remove Row from Table Handler
def rmHandler(table: str):
    confirmMsg = "Is this the Row you want to Remove?"

    if table == COUNTRY_TABLENAME:
        # Ask for Country ID to Modify
        countryID = IntPrompt.ask("\nEnter Country ID to Remove")

        # Ask for Confirmation
        countryTable.get(COUNTRY_ID, countryID)
        if not Confirm.ask(confirmMsg):
            return

        # Ask for Confirmation
        if Confirm.ask("\nAre you Sure to Remove this Country?"):
            countryTable.remove(countryID)


# Main Event Handler
def eventHandler(action: str, table: str):

    while True:
        try:
            # Print All Rows from Given Table
            if action == ALL:
                allHandler(table)

            elif action == GET:
                getHandler(table)

            elif action == MOD:
                modHandler(table)

            elif action == ADD:
                addHandler(table)

            elif action == RM:
                rmHandler(table)

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

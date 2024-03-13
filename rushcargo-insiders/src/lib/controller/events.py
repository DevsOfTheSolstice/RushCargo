from dotenv import load_dotenv
from rich.prompt import Prompt, IntPrompt, Confirm
from pathlib import Path
import os

from ..model.database import *
from ..model.classes import *
from ..model.constants import *
from ..model.exceptions import *
from ..io.validator import *


# Clear Function
def clear():
    # For Windows
    if os.name == "nt":
        os.system("cls")

    # For Posix
    else:
        os.system("clear")


# Initialize Database Connection
def initdb():
    # Get Path to 'src' Directory
    src = Path(__file__).parent.parent.parent

    # Get Path to 'rushcargo-insiders' Directory
    main = src.parent

    # Get Path to the .env File for Local Environment Variables
    dotenvPath = main / "venv/.env"

    # Load .env File
    load_dotenv(dotenvPath)

    # Get Database-related Environment Variables
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    dbname = os.getenv("DBNAME")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")

    # Initialize Database Object
    return Database(dbname, user, password, host, port)


# Get All Table Handler
def getAllHandler(table: str, dbTable):
    sortBy = desc = None

    if table == COUNTRY_TABLENAME:
        # Asks for Sort Order
        sortBy = Prompt.ask(
            "\nHow do you want to Sort it?",
            choices=[COUNTRY_ID, COUNTRY_NAME, COUNTRY_PHONE_PREFIX],
        )
        desc = Confirm.ask("Do you want to Sort it in Descending Order?")

        # Print Table
        dbTable.getAll(sortBy, desc)


# Get Table Handler
def getHandler(table: str, dbTable):
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
        dbTable.get(field, value)


# Modify Row from Table Handler
def modHandler(table: str, dbTable):
    fieldMsg = "Which Field do you want to Modify?"
    valueMsg = "Which New Value do you want to Assign it?"

    countryID = field = value = None

    if table == COUNTRY_TABLENAME:
        # Ask for Country ID to Modify
        countryID = IntPrompt.ask("\nEnter Country ID to Modify")

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
        dbTable.modify(countryID, field, value)


# Add Row to Table Handler
def addHandler(table: str, dbTable):
    if table == COUNTRY_TABLENAME:
        # Asks for Country Fields
        countryName = Prompt.ask("\nEnter Country Name")
        phonePrefix = IntPrompt.ask("Enter Phone Prefix")

        # Check Country Name
        if not checkTableField(table, COUNTRY_NAME, countryName):
            raise ValueError(table, COUNTRY_NAME, countryName)

        # Insert Country
        dbTable.add(Country(countryName, phonePrefix))


# Remove Row from Table Handler
def rmHandler(table: str, dbTable):
    if table == COUNTRY_TABLENAME:
        # Ask for Country ID to Modify
        countryID = IntPrompt.ask("\nEnter Country ID to Remove")

        # Ask for Confirmation
        if Confirm.ask("\nAre you Sure to Remove this Country?"):
            dbTable.remove(countryID)


# Main Event Handler
def eventHandler(action: str, table: str):
    # Initialize Database Connection
    db = initdb()

    # Initialize Table Classes
    countryTable = CountryTable(db)

    while True:
        try:
            # Print All Rows from Given Table
            if action == GET_ALL:
                getAllHandler(table, countryTable)

            elif action == GET:
                getHandler(table, countryTable)

            elif action == MOD:
                modHandler(table, countryTable)

            elif action == ADD:
                addHandler(table, countryTable)

            elif action == RM:
                rmHandler(table, countryTable)
        except:
            print(111)

        # Ask if the User wants to Exit the Program
        exit = Confirm.ask("\nDo you want to End the Current Session?")

        if exit:
            break

        # Clear Screen
        clear()

        # Ask Next Action
        action = Prompt.ask("\nWhat do you want to do?", choices=ACTION_CMDS)
        table = Prompt.ask("At which table?", choices=TABLE_CMDS)

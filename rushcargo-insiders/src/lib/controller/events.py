import logging

from rich.prompt import Prompt
from rich.logging import RichHandler

from .constants import RICH_LOGGER_DEBUG_MODE
from .locationsEvents import LocationsEventHandler

from ..io.arguments import getEventHandlerArguments
from ..io.constants import *
from ..io.validator import clear

from ..model.database import Database
from ..model.database_tables import console

from ..terminal.constants import END_MSG, PRESS_ENTER

# Get Rich Logger
if RICH_LOGGER_DEBUG_MODE:
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    log = logging.getLogger("rich")


class EventHandler:
    """
    Class that Handles All the Events
    """

    # Database Connection
    __conn = None
    __c = None

    # Event Handlers
    __locationsEventHandler = None

    def __init__(self, db: Database, user: str, ORSApiKey: str):
        """
        Event Handler Class Constructor

        :param Database db: Database Object of the Current Connection with the Remote Database
        :param str user: Remote Database Role Name
        :param str ORSApiKey: Open Routing Service API Key
        """

        # Store Database Connection and Cursor
        self.__conn = db.getConnection()
        self.__c = db.getCursor()

        # Initialize Location Event Handler
        self.__locationsEventHandler = LocationsEventHandler(
            self.__conn, self.__c, user, ORSApiKey
        )

    def handler(self, argsDict: dict) -> None:
        """
        Main Handler of ``add``, ``all``, ``get``, ``mod`` and ``rm`` Commands

        :param dict argsDict: Dictionary that Contains All the Commands and its Arguments. If there's No Input by the User, returns None
        :return: Nothing
        :rtype: NoneType
        """

        while True:
            try:
                # Clear Terminal
                clear()

                # Check if it's a Database-related Command
                if argsDict[CMD_TYPE] == DB:
                    # Check if it's a Locations Scheme Table
                    if argsDict[DB_SCHEME] == DB_LOCATIONS_SCHEME_CMD:
                        # Call Location Database Event Handler
                        self.__locationsEventHandler.dbHandler(
                            argsDict[DB_ACTION], argsDict[DB_TABLE]
                        )

                # Check if it's a Graph-related Command
                elif argsDict[CMD_TYPE] == GRAPH:
                    # Call Location Graph Event Handler
                    self.__locationsEventHandler.graphHandler(
                        argsDict[GRAPH_TYPE], argsDict[GRAPH_LEVEL]
                    )

                # Clear Terminal
                clear()

                argsDict = getEventHandlerArguments()

                # Check if the User wants to Exit the Program
                if argsDict == None:
                    break

            # End Program
            except KeyboardInterrupt:
                console.print(END_MSG, style="warning")
                return

            except Exception as err:
                try:
                    console.print(err, style="warning")

                    # Press ENTER to Continue
                    Prompt.ask(PRESS_ENTER)

                    # Clear Terminal
                    clear()

                    argsDict = getEventHandlerArguments()

                    # Check if the User wants to Exit the Program
                    if argsDict == None:
                        break

                    continue

                # End Program
                except KeyboardInterrupt:
                    console.print(END_MSG, style="warning")
                    return
